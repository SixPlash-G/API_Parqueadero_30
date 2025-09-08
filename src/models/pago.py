from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Pago(BaseModel):
    payment_id: Optional[int] = None  # Se genera automáticamente
    entry_id: int
    payment_method: str  # "cash" o "transfer"
    qr_code: Optional[str] = None  # Solo para transfer
    payment_status: str = "pending"  # "pending" o "completed"
    payment_date: Optional[datetime] = None
    created_at: Optional[datetime] = None  # Se asigna automáticamente
