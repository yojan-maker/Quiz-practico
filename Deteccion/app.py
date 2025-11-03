import streamlit as st
import cv2
import mediapipe as mp
import threading
import time

# --- Inicialización de MediaPipe ---
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# --- Variables compartidas ---
frame_compartido = None
etiqueta = "Esperando..."
mutex = threading.Lock()
semaforo = threading.Semaphore(0)
ejecutando = True

# --- Hilo de captura ---
def capturar_video():
    global frame_compartido, ejecutando
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("❌ No se pudo abrir la cámara.")
        return

    while ejecutando:
        ret, frame = cap.read()
        if not ret:
            break

        with mutex:
            frame_compartido = frame.copy()

        semaforo.release()
        time.sleep(0.02)

    cap.release()

# --- Hilo de procesamiento ---
def procesar_postura():
    global etiqueta, frame_compartido, ejecutando
    while ejecutando:
        semaforo.acquire()
        with mutex:
            if frame_compartido is None:
                continue
            frame_rgb = cv2.cvtColor(frame_compartido, cv2.COLOR_BGR2RGB)
            resultado = pose.process(frame_rgb)

        if resultado.pose_landmarks:
            # Dibuja puntos y conexiones sobre el frame
            mp_drawing.draw_landmarks(
                frame_rgb,
                resultado.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(0,0,255), thickness=2)
            )

            # Calcula postura
            landmarks = resultado.pose_landmarks.landmark
            cadera = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y
            rodilla = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y

            if cadera < rodilla - 0.1:
                etiqueta = "🧍 De pie"
            else:
                etiqueta = "💺 Sentado"

            # Devuelve frame con dibujos
            with mutex:
                frame_compartido = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        else:
            etiqueta = "No detectado"

        time.sleep(0.05)

# --- Interfaz con Streamlit ---
st.set_page_config(page_title="Detección de Postura con MediaPipe", layout="centered")
st.title("🤖 Detección de Postura con MediaPipe y Hilos")
st.markdown("**Se usan hilos, mutex, sección crítica y semáforo para procesar video en tiempo real.**")

frame_placeholder = st.empty()
etiqueta_placeholder = st.empty()

# Botón para iniciar
if st.button("Iniciar detección"):
    ejecutando = True
    threading.Thread(target=capturar_video, daemon=True).start()
    threading.Thread(target=procesar_postura, daemon=True).start()

    while True:
        with mutex:
            if frame_compartido is not None:
                frame_rgb = cv2.cvtColor(frame_compartido, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                etiqueta_placeholder.markdown(f"### Estado actual: **{etiqueta}**")
        time.sleep(0.05)
