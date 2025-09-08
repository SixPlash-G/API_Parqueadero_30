from pydantic import BaseModel
from typing import Optional

class Usuario(BaseModel):
    user_id: Optional[int] = None  # Opcional en la creación
    name: str
    email: str
    phone: str
    password: Optional[str] = None  # Se asigna automáticamente en la BD
    is_superuser: bool = False  # Valor por defecto a False 
    created_at: Optional[str] = None  # Se asigna automáticamente en la BD
