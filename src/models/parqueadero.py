from pydantic import BaseModel
from typing import Optional

class Parqueadero(BaseModel):
    parking_id: Optional[int] = None  # Opcional en la creación
    total_spaces: int
    available_spaces: int
    created_at: Optional[str] = None  # Se asigna automáticamente en la
