# 🎯 Quiz_Practico_Tercer_Corte — Detección de Postura con MediaPipe, Hilos y Streamlit

**Autor:** Yojan Contreras (`yojan-maker`)  
**DockerHub:** `yojancg`  
**Fecha:** (añade la fecha de entrega)

Pequeña aplicación que utiliza **MediaPipe Pose** para detectar en tiempo real dos posturas humanas: **De pie** 🧍 y **Sentado** 💺.  
La app muestra la segmentación (landmarks y conexiones) sobre el video, etiqueta la postura, y está implementada con **concurrencia** (hilos), **sincronización** (mutex/Condition/semaphore) y desplegada con **Streamlit** y **Docker**.

---
## 🧾 Descripción de los componentes principales

- **app.py**  
  - Contiene la interfaz Streamlit y la lógica para iniciar/mostrar la detección.
  - Crea 2 hilos:
    - `capturar_video()` — captura frames desde la cámara (OpenCV).
    - `procesar_postura()` — aplica MediaPipe, dibuja landmarks/conexiones y decide la etiqueta.
  - Usa variables compartidas (`frame_compartido`, `etiqueta`) protegidas por **mutex** y sincronizadas con **semaphore** y **Condition**.

- **Dockerfile**  
  - Contiene instrucciones para construir una imagen que ejecute Streamlit + OpenCV + MediaPipe.
  - Incluye paquetes del sistema necesarios para el acceso a la cámara.

- **requirements.txt**  
  - Lista de dependencias: `streamlit`, `mediapipe`, `opencv-python`, `numpy` (si procede).

---

## 🔧 Instalación y ejecución (local - sin Docker)

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/yojan-maker/Quiz_Practico_Tercer_Corte.git
   cd Quiz_Practico_Tercer_Corte

2. (Recomendado) Crear un entorno virtual:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
3. Instalar dependencias:
    ```bash
    pip install -r requirements.txt
   ```
4. Ejecutar Streamlit:
  ```bash
  streamlit run app.py
  ```
- Abrir en el navegador: http://localhost:8501
- Pulsa Iniciar detección (o el botón que tenga la UI).

---

## 🐳 Ejecución en Docker (con cámara)

1. Construir la imagen:
  ```bash
  docker build -t quiz_pose .
  ```
2. Ejecutar el contenedor con acceso a la cámara:
  ```bash
  docker run -p 8501:8501 --device /dev/video0:/dev/video0 quiz_pose
  ```
  - Si tu cámara está en otro device cambia /dev/video0.
  - Abrir http://localhost:8501.
---

## 🧠 Diseño concurrente (hilos y sincronización)

**Variables compartidas**

- frame_compartido — frame actual capturado por la cámara.
- etiqueta — string con la postura detectada.

### **Hilos**

- **Hilo captura (capturar_video()):**
Lee frames de la cámara con OpenCV y escribe frame_compartido.
Después de escribir, notifica al hilo de procesamiento (ej. semaphore.release()).

- **Hilo procesamiento (procesar_postura()):**
Espera a que haya un nuevo frame (semaphore.acquire()), lee frame_compartido, procesa con MediaPipe, dibuja landmarks y actualiza etiqueta.

### **Sincronización**
**Mutex (Lock):**
- mutex = threading.Lock() protege el acceso a frame_compartido y etiqueta.
- Se usa with mutex: alrededor de lecturas/escrituras críticas para evitar condiciones de carrera.

**Condition / Semaphore:**
- semaphore (o Condition) coordina los hilos para que el procesador espere hasta que haya un frame nuevo, evitando loops ocupados (busy-wait).
- Ejemplo: semaphore.release() después de capturar; semaphore.acquire() antes de procesar.

## **Sección crítica**
- Todo bloque with mutex: que modifica o recorre enemigos o frame_compartido es sección crítica.
---
## 📋 Tabla resumen de concurrencia

| **Concepto**              | **Implementación**                     | **Función**                                  |
|----------------------------|----------------------------------------|----------------------------------------------|
| **Recurso compartido**     | `frame_compartido`, `etiqueta`         | Datos entre captura y procesado              |
| **Mutex (Lock)**           | `mutex = threading.Lock()`             | Exclusión mutua en accesos críticos          |
| **Semáforo / Condition**   | `semaphore.acquire()/release()`        | Sincroniza disponibilidad del frame          |
| **Hilo captura**           | `capturar_video()`                     | Produce frames                               |
| **Hilo procesado**         | `procesar_postura()`                   | Consume frames y calcula etiqueta            |

---

### **✅ Detección de posturas (lógica simplificada)**

- Uso de landmarks de MediaPipe:
- Ejemplo de comprobación: comparar la coordenada y de la cadera con la rodilla.
- Regla simple (ajustable):
    if hip_y < knee_y - umbral: De pie
    else: Sentado
Se recomienda calibrar umbral con pruebas reales para mejorar precisión.
---

### 🧩 Visualización (segmentación y landmarks)
- El ejemplo usa mp.solutions.drawing_utils.draw_landmarks() para pintar:
    puntos (landmarks) con DrawingSpec(circle_radius=, color=...)
    conexiones (POSE_CONNECTIONS) con connection_drawing_spec.
- El frame con los dibujos se muestra en Streamlit como imagen convertida BGR->RGB.
---

### 📦 Dockerfile recomendado (ejemplo)
  ```bash
FROM python:3.10-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
Ejecutar
  ```bash
docker build -t quiz_pose .
docker run -p 8501:8501 --device /dev/video0:/dev/video0 quiz_pose
```
---
### 📸 Registro fotográfico

![Image](https://github.com/user-attachments/assets/c84a30b4-3801-48cc-970c-ff02b9e0ec76)

![Image](https://github.com/user-attachments/assets/cc38cc58-a815-4ed9-96d8-b954f3c989d4)


---
## 🧩 Conclusión

- La implementación desarrollada integra de forma efectiva **MediaPipe Pose**, **Python** y **Streamlit**, demostrando cómo las herramientas de visión por computadora pueden complementarse con conceptos de **programación concurrente** para lograr una aplicación funcional, eficiente y modular.

- El uso de **MediaPipe** permitió realizar la **detección de puntos de referencia corporales (landmarks)** en tiempo real, posibilitando la identificación precisa de dos posturas humanas básicas: **de pie** y **sentado**. Gracias a la API de MediaPipe, se logró visualizar los puntos clave y las conexiones del esqueleto corporal, lo que brinda una interpretación visual intuitiva del análisis postural.

- Por otra parte, la aplicación de **hilos (threads)** permitió separar las tareas de captura de video y procesamiento de pose, optimizando el rendimiento y evitando bloqueos del flujo principal. - La incorporación de **mutex**, **sección crítica** y **semaforización** garantizó la sincronización adecuada entre los hilos, evitando condiciones de carrera y asegurando la consistencia de los datos compartidos.

- En conjunto, este proyecto demuestra cómo combinar **técnicas de visión artificial**, **sincronización concurrente** y **contenedorización** para crear sistemas interactivos y robustos basados en inteligencia artificial aplicada.

---
### Creditos
## 🙌 Créditos

Este proyecto hace uso de la tecnología de **MediaPipe Pose Landmarker**, desarrollada por **Google Research** dentro del framework **MediaPipe**.  
El sistema de detección de puntos de referencia corporales y la segmentación visual están basados en el modelo original disponible en:

🔗 [MediaPipe Studio – Pose Landmarker Demo](https://mediapipe-studio.webapps.google.com/demo/pose_landmarker?hl=es-419)

Se agradece a la comunidad de desarrolladores de **MediaPipe** por proporcionar herramientas abiertas que facilitan la integración de modelos de visión por computadora en aplicaciones interactivas, fomentando el aprendizaje y la experimentación en el campo de la inteligencia artificial aplicada.
