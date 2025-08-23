from fastapi import APIRouter, Depends, HTTPException
from db.database import get_db_connection
from models.tarifa import Tarifa
from core.security import get_current_user  # Protección de rutas

router = APIRouter()

# 🔹 Crear Tarifa
@router.post("/", response_model=Tarifa)
def create_tarifa(tarifa: Tarifa, current_user: str = Depends(get_current_user)):
    """Registra una nueva tarifa"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """INSERT INTO TARIFAS (tipo, valor_hora) VALUES (%s, %s)"""
        cursor.execute(sql, (tarifa.tipo.value, tarifa.valor_hora))
        conn.commit()

        tarifa.tarifa_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return tarifa
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error al registrar la tarifa")

# 🔹 Obtener todas las Tarifas
@router.get("/", response_model=list[Tarifa])
def get_tarifas(current_user: str = Depends(get_current_user)):
    """Devuelve la lista de todas las tarifas"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT tarifa_id, tipo, valor_hora, created_at FROM TARIFAS")
    tarifas = cursor.fetchall()

    cursor.close()
    conn.close()

    # 🔹 Convertimos `created_at` a string
    for tarifa in tarifas:
        tarifa["created_at"] = tarifa["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return tarifas

# 🔹 Obtener Tarifa por ID
@router.get("/{tarifa_id}", response_model=Tarifa)
def get_tarifa(tarifa_id: int, current_user: str = Depends(get_current_user)):
    """Devuelve una tarifa por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT tarifa_id, tipo, valor_hora, created_at FROM TARIFAS WHERE tarifa_id = %s", (tarifa_id,))
    tarifa = cursor.fetchone()

    cursor.close()
    conn.close()

    if not tarifa:
        raise HTTPException(status_code=404, detail="Tarifa no encontrada")

    # 🔹 Convertimos `created_at` a string
    tarifa["created_at"] = tarifa["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return tarifa

# 🔹 Actualizar Tarifa
@router.put("/{tarifa_id}", response_model=Tarifa)
def update_tarifa(tarifa_id: int, tarifa: Tarifa, current_user: str = Depends(get_current_user)):
    """Actualiza los datos de una tarifa"""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """UPDATE TARIFAS SET tipo=%s, valor_hora=%s WHERE tarifa_id=%s"""
    cursor.execute(sql, (tarifa.tipo.value, tarifa.valor_hora, tarifa_id))
    conn.commit()

    cursor.close()
    conn.close()

    return tarifa

# 🔹 Eliminar Tarifa
@router.delete("/{tarifa_id}")
def delete_tarifa(tarifa_id: int, current_user: str = Depends(get_current_user)):
    """Elimina una tarifa por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM TARIFAS WHERE tarifa_id = %s", (tarifa_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Tarifa eliminada correctamente"}
