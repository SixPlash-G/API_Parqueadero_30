from pydantic import BaseModel
from typing import Optional

class Parqueadero(BaseModel):
    parqueadero_id: Optional[int] = None  # Opcional en la creación
    total_espacios: int
    espacios_disponibles: int
    created_at: Optional[str] = None  # Se asigna automáticamente en la BD
