from pydantic import BaseModel
from typing import Optional

class Vehiculo(BaseModel):
    vehiculo_id: Optional[int] = None  # Opcional en la creación
    cliente_id: int
    placa: str
    marca: str
    modelo: str
    created_at: Optional[str] = None  # Se asigna automáticamente en la BD
