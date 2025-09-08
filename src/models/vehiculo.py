from pydantic import BaseModel
from typing import Optional

class Vehiculo(BaseModel):
    vehicle_id: Optional[int] = None  # Opcional en la creación
    client_id: int
    plate: str
    brand: str
    model: str
    created_at: Optional[str] = None  # Se asigna automáticamente en la BD