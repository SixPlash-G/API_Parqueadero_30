from fastapi import APIRouter, Depends, HTTPException, Query
from src.db.database import get_db_connection
from src.models.rate import Tarifa
from src.models.paginate import PaginatedResponse
from src.core.security import get_current_user  # Protección de rutas

router = APIRouter()

# 🔹 Crear Tarifa
@router.post("/", response_model=Tarifa)
def create_rate(tarifa: Tarifa, current_user: str = Depends(get_current_user)):
    """Registra una nueva tarifa"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """INSERT INTO RATES (type, hourly_rate) VALUES (%s, %s)"""
        cursor.execute(sql, (tarifa.type.value, tarifa.hourly_rate))
        conn.commit()

        tarifa.rate_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return tarifa
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error al registrar la tarifa")

# 🔹 Obtener todas las Tarifas con busqueda y paginación
@router.get("/", response_model=PaginatedResponse[Tarifa])
def get_rates(
    search: str | None = Query(None, description="Buscar por tipo"),
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Número de resultados por página"),
    current_user: str = Depends(get_current_user)
):
    """Devuelve la lista de todas las tarifas con paginación y búsqueda"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- 1. Calcular total ---
    count_query = "SELECT COUNT(*) as total FROM RATES"
    params = []
    if search:
        count_query += " WHERE type LIKE %s"
        params.append(f"%{search}%")

    cursor.execute(count_query, tuple(params))
    total = cursor.fetchone()["total"]

    # --- 2. Obtener página de resultados ---
    query = "SELECT rate_id, type, hourly_rate, created_at FROM RATES"
    if search:
        query += " WHERE type LIKE %s"
    query += " ORDER BY rate_id LIMIT %s OFFSET %s"

    offset = (page - 1) * limit
    params_page = params + [limit, offset]

    cursor.execute(query, tuple(params_page))
    rows = cursor.fetchall()

    # Convertimos created_at a string si es datetime
    for row in rows:
        if row["created_at"] and hasattr(row["created_at"], "strftime"):
            row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    tarifas = [Tarifa(**row) for row in rows]

    cursor.close()
    conn.close()

    return PaginatedResponse[Tarifa](
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit,
        data=tarifas
    )

# 🔹 Obtener Tarifa por ID
@router.get("/{rate_id}", response_model=Tarifa)
def get_rate(rate_id: int, current_user: str = Depends(get_current_user)):
    """Devuelve una tarifa por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT rate_id, type, hourly_rate, created_at FROM RATES WHERE rate_id = %s", (rate_id,))
    tarifa = cursor.fetchone()

    cursor.close()
    conn.close()

    if not tarifa:
        raise HTTPException(status_code=404, detail="Tarifa no encontrada")

    # 🔹 Convertimos `created_at` a string
    tarifa["created_at"] = tarifa["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return tarifa

# 🔹 Actualizar Tarifa
@router.put("/{rate_id}", response_model=Tarifa)
def update_rate(rate_id: int, tarifa: Tarifa, current_user: str = Depends(get_current_user)):
    """Actualiza los datos de una tarifa"""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """UPDATE RATES SET type=%s, hourly_rate=%s WHERE rate_id=%s"""
    cursor.execute(sql, (tarifa.type.value, tarifa.hourly_rate, rate_id))
    conn.commit()

    cursor.close()
    conn.close()

    return tarifa

# 🔹 Eliminar Tarifa
@router.delete("/{rate_id}")
def delete_rate(rate_id: int, current_user: str = Depends(get_current_user)):
    """Elimina una tarifa por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM RATES WHERE rate_id = %s", (rate_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Tarifa eliminada correctamente"}