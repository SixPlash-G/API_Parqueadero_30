from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class EstadoRegistro(str, Enum):
    en_proceso = "en proceso"
    finalizado = "finalizado"

class RegistroIngreso(BaseModel):
    registro_id: Optional[int] = None  # Opcional en la creación
    vehiculo_id: int  # FK - Vehículo que ingresa
    usuario_id: int  # FK - Usuario que registra la entrada
    tarifa_id: int  # FK - Tarifa aplicada
    fecha_ingreso: datetime
    fecha_salida: Optional[datetime] = None
    tiempo_total: Optional[int] = None  # Tiempo total en minutos
    monto_total: Optional[float] = None  # Eliminamos condecimal
    estado: EstadoRegistro = EstadoRegistro.en_proceso  # Estado por defecto
    created_at: Optional[datetime] = None  # Se asigna automáticamente en la BD
