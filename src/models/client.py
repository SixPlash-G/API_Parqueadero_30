from pydantic import BaseModel
from typing import Optional

class Cliente(BaseModel):
    client_id: Optional[int] = None  # Opcional en la creación
    name: str
    email: str
    phone: str
    created_at: Optional[str] = None  # Se asigna automáticamente en
