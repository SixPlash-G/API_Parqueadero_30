from pydantic import BaseModel
from typing import Optional
from enum import Enum

class TipoTarifa(str, Enum):
    regular = "regular"
    special = "special"

class Tarifa(BaseModel):
    rate_id: Optional[int] = None  # Opcional en la creación
    type: TipoTarifa  # ENUM ('regular', 'special')
    hourly_rate: float
    created_at: Optional[str] = None  # Se asigna automáticamente
