# from ultralytics import YOLO
# import easyocr
# import cv2
# import re

# # Inicialización de modelo YOLO entrenado para placas
# model = YOLO("best.pt")
# # Inicializar EasyOCR (inglés, números y letras latinas)
# reader = easyocr.Reader(['en'])
# # Variable global para almacenar la última placa
# last_plate = None
# # Iniciar camara
# def generate_frames(camera_index=0):
#     global last_plate
#     cam = cv2.VideoCapture(camera_index)

#     while True:
#         ret, frame = cam.read()
#         if not ret:
#             break
        
#         # Detección de placa con YOLO
#         results = model.predict(frame, conf=0.25, verbose=False)

#         for r in results:
#             for box in r.boxes:
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 roi = frame[y1:y2, x1:x2] #Recortar ROI (placa detectada)

#                 if roi.size > 0:
#                     ocr_result = reader.readtext(roi) #Pasar ROI a EasyOCR directamente (en color)

#                     plate_text = ""
#                     if ocr_result:
#                         # Elegir el texto con mayor score (más confiable)
#                         best_match = max(ocr_result, key=lambda x: x[2])
#                         plate_text = re.sub(r'[^A-Z0-9]', '', best_match[1].upper())

#                     if plate_text:
#                         last_plate = plate_text.strip()
#                          # Mostrar texto reconocido en la imagen
#                         cv2.putText(frame, last_plate, (x1, y1 - 10),
#                                     cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

#         # Codificar frame
#         _, buffer = cv2.imencode('.jpg', frame)
#         frame_bytes = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

#     cam.release()

# def get_last_plate():
#     """Devuelve la última placa detectada"""
#     global last_plate
#     return last_plate


from ultralytics import YOLO
import easyocr
import cv2
import re
import os

# ---------------------------
# Configuración de rutas
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # carpeta de este script
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")

# Inicialización de modelo YOLO entrenado
model = YOLO(MODEL_PATH)
# Inicializar EasyOCR (inglés, números y letras latinas)
reader = easyocr.Reader(['en'])

# Variable global para almacenar la última placa
last_plate = None

# ---------------------------
# Funciones principales
# ---------------------------
def detectar_placa(frame):
    #Detecta placa en un frame y devuelve el texto reconocido (si lo hay)
    global last_plate

    # Detección de placa con YOLO
    results = model.predict(frame, conf=0.25, verbose=False)

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            roi = frame[y1:y2, x1:x2]  # Recortar ROI (placa detectada)

            if roi.size > 0:
                ocr_result = reader.readtext(roi)

                plate_text = ""
                if ocr_result:
                    # Elegir el texto con mayor score (más confiable)
                    best_match = max(ocr_result, key=lambda x: x[2])
                    plate_text = re.sub(r'[^A-Z0-9]', '', best_match[1].upper())

                if plate_text:
                    last_plate = plate_text.strip()
                    # Mostrar texto reconocido en la imagen
                    cv2.putText(frame, last_plate, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    return frame, last_plate


def get_last_plate():
    """Devuelve la última placa detectada"""
    global last_plate
    return last_plate

def generate_frames(camera_index=0):
    """Generador de frames para streaming tipo MJPEG (API)"""
    global last_plate
    cam = cv2.VideoCapture(camera_index)

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        frame, _ = detectar_placa(frame)

        # Codificar frame para streaming
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cam.release()

# -------------------------
# Ejecución como script
# -------------------------
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)  # Cámara web (0 = default)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame, plate = detectar_placa(frame)
        if plate:
            print("Placa detectada:", plate)

        cv2.imshow("ANPR Test", frame)

        # Presiona 'q' para salir
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()