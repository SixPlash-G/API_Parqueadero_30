from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoRegistro(str, Enum):
    in_progress = "in_progress"
    finished = "finished"

class RegistroIngreso(BaseModel):
    entry_id: Optional[int] = None  # Opcional en la creación
    vehicle_id: int  # FK - Vehículo que ingresa
    user_id: int  # FK - Usuario que registra la entrada
    rate_id: int  # FK - Tarifa aplicada
    entry_date: datetime
    exit_date: Optional[datetime] = None
    total_time: Optional[int] = None  # Tiempo total en minutos
    total_amount: Optional[float] = None
    status: EstadoRegistro = EstadoRegistro.in_progress  # Estado por defecto
    created_at: Optional[datetime] = None  # Se asigna automáticamente
