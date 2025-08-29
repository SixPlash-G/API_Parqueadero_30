from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, JSONResponse
from src.core.security import get_current_user  # Protección de rutas
from src.plate_detection.ANPR import generate_frames, get_last_plate, activate_camera

router = APIRouter()

# 🔹 Streaming de video con detección de placas
@router.get("/video")
def video_feed(token: str = Query('token', description="Token OAuth2 para autenticación")):
    """Devuelve el streaming de video con detección de placas (requiere token OAuth2 como query param o header)"""
    # Obtener token de query param o header
    if token:
        # Validar token manualmente
        try:
            user = get_current_user(token)
            activate_camera()
        except HTTPException as e:
            raise HTTPException(status_code=401, detail="Token inválido")
    else:
            raise HTTPException(status_code=401, detail="Token requerido")

    try:
        return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar el video: {str(e)}")

# 🔹 Última placa detectada
@router.get("/last_plate")
def last_plate(current_user: str = Depends(get_current_user)):
    """Devuelve la última placa detectada"""
    try:
        plate = get_last_plate()
        if plate:
            return JSONResponse({"plate": plate})
        return JSONResponse({"plate": None})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener la placa: {str(e)}")
