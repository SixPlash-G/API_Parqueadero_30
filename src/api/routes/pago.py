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
        sql = """INSERT INTO PAYMENTS (entry_id, payment_method, qr_code, payment_status, payment_date)
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (pago.entry_id, pago.payment_method, pago.qr_code, pago.payment_status, pago.payment_date))
        conn.commit()

        pago.payment_id = cursor.lastrowid
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

    cursor.execute("SELECT payment_id, entry_id, payment_method, qr_code, payment_status, payment_date, created_at FROM PAYMENTS")
    pagos = cursor.fetchall()

    cursor.close()
    conn.close()

    return pagos

# 🔹 Obtener un pago por ID
@router.get("/{payment_id}", response_model=Pago)
def get_pago(payment_id: int, current_user: str = Depends(get_current_user)):
    """Devuelve un pago por su ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT payment_id, entry_id, payment_method, qr_code, payment_status, payment_date, created_at FROM PAYMENTS WHERE payment_id = %s", (payment_id,))
    pago = cursor.fetchone()

    cursor.close()
    conn.close()

    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    
    return pago

# 🔹 Actualizar estado del pago
@router.put("/{payment_id}", response_model=Pago)
def update_pago(payment_id: int, pago: Pago, current_user: str = Depends(get_current_user)):
    """Actualiza el estado del pago"""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """UPDATE PAYMENTS SET payment_method=%s, qr_code=%s, payment_status=%s, payment_date=%s WHERE payment_id=%s"""
    cursor.execute(sql, (pago.payment_method, pago.qr_code, pago.payment_status, pago.payment_date, payment_id))
    conn.commit()

    cursor.close()
    conn.close()

    return pago

# 🔹 Eliminar un pago
@router.delete("/{payment_id}")
def delete_pago(payment_id: int, current_user: str = Depends(get_current_user)):
    """Elimina un pago por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM PAYMENTS WHERE payment_id = %s", (payment_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Pago eliminado correctamente"}
