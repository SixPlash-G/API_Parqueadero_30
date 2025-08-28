from pydantic import BaseModel
from typing import Optional
from enum import Enum

class TipoTarifa(str, Enum):
    ordinaria = "ordinaria"
    especial = "especial"

class Tarifa(BaseModel):
    tarifa_id: Optional[int] = None  # Opcional en la creación
    tipo: TipoTarifa  # ENUM ('ordinaria', 'especial')
    valor_hora: float  # Eliminamos condecimal
    created_at: Optional[str] = None  # Se asigna automáticamente en la BD
