from typing import Generic, TypeVar, List
from pydantic import BaseModel

# Tipo genérico T (puede ser Usuario, Cliente, etc.)
T = TypeVar("T")

# 🔹 Modelo de paginación genérico
class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    limit: int
    total_pages: int
    data: List[T]