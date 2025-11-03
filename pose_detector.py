import cv2
import mediapipe as mp
import threading
import numpy as np

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mutex = threading.Lock()
semaforo = threading.Semaphore(1)

frame_compartido = None
etiqueta = "Desconocido"

def capturar_video():
    global frame_compartido
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        with mutex:
            frame_compartido = frame.copy()
        semaforo.release()

    cap.release()

def procesar_postura():
    global etiqueta, frame_compartido
    while True:
        semaforo.acquire()
        with mutex:
            if frame_compartido is None:
                continue
            frame_rgb = cv2.cvtColor(frame_compartido, cv2.COLOR_BGR2RGB)
            resultado = pose.process(frame_rgb)

        if resultado.pose_landmarks:
            # Obtener puntos clave relevantes
            landmarks = resultado.pose_landmarks.landmark
            cadera = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y
            rodilla = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y

            # Si la cadera está mucho más alta que la rodilla → de pie
            if cadera < rodilla - 0.1:
                etiqueta = "🧍 De pie"
            else:
                etiqueta = "💺 Sentado"
        else:
            etiqueta = "No detectado"
