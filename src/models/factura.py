from pydantic import BaseModel
from typing import Optional

class Factura(BaseModel):
    invoice_id: Optional[int] = None  # Se genera automáticamente
    payment_id: int
    client_id: int
    details: str
    issue_date: Optional[str] = None  # Se genera automáticamente en la BD
