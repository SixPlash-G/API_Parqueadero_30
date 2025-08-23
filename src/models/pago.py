from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Pago(BaseModel):
    pago_id: Optional[int] = None  # Se genera automáticamente
    registro_id: int
    metodo_pago: str  # "efectivo" o "transferencia"
    codigo_qr: Optional[str] = None  # Solo para transferencia
    estado_pago: str = "pendiente"  # "pendiente" o "completado"
    fecha_pago: Optional[datetime] = None
    created_at: Optional[datetime] = None  # Se asigna automáticamente en la BD
