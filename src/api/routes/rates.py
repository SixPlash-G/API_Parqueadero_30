from fastapi import APIRouter, Depends, HTTPException
from src.db.database import get_db_connection
from src.models.rate import Tarifa
from src.core.security import get_current_user  # Protección de rutas

router = APIRouter()

# 🔹 Crear Tarifa
@router.post("/", response_model=Tarifa)
def create_rates(tarifa: Tarifa, current_user: str = Depends(get_current_user)):
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

# 🔹 Obtener todas las Tarifas
@router.get("/", response_model=list[Tarifa])
def get_rates(current_user: str = Depends(get_current_user)):
    """Devuelve la lista de todas las tarifas"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT rate_id, type, hourly_rate, created_at FROM RATES")
    tarifas = cursor.fetchall()

    cursor.close()
    conn.close()

    # 🔹 Convertimos `created_at` a string
    for tarifa in tarifas:
        tarifa["created_at"] = tarifa["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return tarifas

# 🔹 Obtener Tarifa por ID
@router.get("/{rate_id}", response_model=Tarifa)
def get_rates(rate_id: int, current_user: str = Depends(get_current_user)):
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
def update_rates(rate_id: int, tarifa: Tarifa, current_user: str = Depends(get_current_user)):
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
def delete_rates(rate_id: int, current_user: str = Depends(get_current_user)):
    """Elimina una tarifa por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM RATES WHERE rate_id = %s", (rate_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Tarifa eliminada correctamente"}