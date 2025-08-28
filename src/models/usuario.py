from pydantic import BaseModel

class Usuario(BaseModel):
    usuario_id: int | None = None  # Opcional en la creación
    nombre: str
    email: str
    celular: str
    password: str | None = None  # Se asigna automáticamente en la BD
    is_superuser: bool = False  # Valor por defecto a False 
    created_at: str | None = None  # Se asigna automáticamente en la BD
