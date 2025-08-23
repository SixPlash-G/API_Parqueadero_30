from pydantic import BaseModel
from typing import Optional

class Cliente(BaseModel):
    cliente_id: Optional[int] = None  # Opcional en la creación
    nombre: str
    email: str
    celular: str
    created_at: Optional[str] = None  # Se asigna automáticamente en la BD
