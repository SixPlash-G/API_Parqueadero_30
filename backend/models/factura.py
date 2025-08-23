from pydantic import BaseModel
from typing import Optional

class Factura(BaseModel):
    factura_id: Optional[int] = None  # Se genera automáticamente
    pago_id: int
    cliente_id: int
    detalle: str
    fecha_emision: Optional[str] = None  # Se genera automáticamente en la BD
