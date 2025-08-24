from fastapi import APIRouter, Depends, HTTPException
from src.db.database import get_db_connection
from src.models.pago import Pago
from src.core.security import get_current_user

router = APIRouter()

# 🔹 Crear un pago
@router.post("/", response_model=Pago)
def create_pago(pago: Pago, current_user: str = Depends(get_current_user)):
    """Registra un nuevo pago"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """INSERT INTO PAGOS (registro_id, metodo_pago, codigo_qr, estado_pago, fecha_pago)
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (pago.registro_id, pago.metodo_pago, pago.codigo_qr, pago.estado_pago, pago.fecha_pago))
        conn.commit()

        pago.pago_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return pago
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error al registrar pago")

# 🔹 Obtener todos los pagos
@router.get("/", response_model=list[Pago])
def get_pagos(current_user: str = Depends(get_current_user)):
    """Devuelve la lista de todos los pagos"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT pago_id, registro_id, metodo_pago, codigo_qr, estado_pago, fecha_pago, created_at FROM PAGOS")
    pagos = cursor.fetchall()

    cursor.close()
    conn.close()

    return pagos

# 🔹 Obtener un pago por ID
@router.get("/{pago_id}", response_model=Pago)
def get_pago(pago_id: int, current_user: str = Depends(get_current_user)):
    """Devuelve un pago por su ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT pago_id, registro_id, metodo_pago, codigo_qr, estado_pago, fecha_pago, created_at FROM PAGOS WHERE pago_id = %s", (pago_id,))
    pago = cursor.fetchone()

    cursor.close()
    conn.close()

    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    
    return pago

# 🔹 Actualizar estado del pago
@router.put("/{pago_id}", response_model=Pago)
def update_pago(pago_id: int, pago: Pago, current_user: str = Depends(get_current_user)):
    """Actualiza el estado del pago"""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """UPDATE PAGOS SET metodo_pago=%s, codigo_qr=%s, estado_pago=%s, fecha_pago=%s WHERE pago_id=%s"""
    cursor.execute(sql, (pago.metodo_pago, pago.codigo_qr, pago.estado_pago, pago.fecha_pago, pago_id))
    conn.commit()

    cursor.close()
    conn.close()

    return pago

# 🔹 Eliminar un pago
@router.delete("/{pago_id}")
def delete_pago(pago_id: int, current_user: str = Depends(get_current_user)):
    """Elimina un pago por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM PAGOS WHERE pago_id = %s", (pago_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Pago eliminado correctamente"}
