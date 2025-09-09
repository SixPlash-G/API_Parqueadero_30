from fastapi import APIRouter, Depends, HTTPException
from src.db.database import get_db_connection
from src.models.invoice import Factura
from src.core.security import get_current_user

router = APIRouter()

# 🔹 Crear factura
@router.post("/", response_model=Factura)
def create_invoices(factura: Factura, current_user: str = Depends(get_current_user)):
    """Registra una nueva factura"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """INSERT INTO INVOICES (payment_id, client_id, details)
                 VALUES (%s, %s, %s)"""
        cursor.execute(sql, (factura.payment_id, factura.client_id, factura.details))
        conn.commit()

        factura.invoice_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return factura
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error al crear factura: {str(e)}")

# 🔹 Obtener todas las facturas
@router.get("/", response_model=list[Factura])
def get_invoices(current_user: str = Depends(get_current_user)):
    """Devuelve todas las facturas registradas"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT invoice_id, payment_id, client_id, details, issue_date FROM INVOICES")
    facturas = cursor.fetchall()

    cursor.close()
    conn.close()

    return facturas

# 🔹 Obtener una factura por ID
@router.get("/{invoice_id}", response_model=Factura)
def get_invoices(invoice_id: int, current_user: str = Depends(get_current_user)):
    """Devuelve una factura específica"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT invoice_id, payment_id, client_id, details, issue_date FROM INVOICES WHERE invoice_id = %s", (invoice_id,))
    factura = cursor.fetchone()

    cursor.close()
    conn.close()

    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    return factura

# 🔹 Actualizar factura
@router.put("/{invoice_id}", response_model=Factura)
def update_invoices(invoice_id: int, factura: Factura, current_user: str = Depends(get_current_user)):
    """Actualiza una factura"""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """UPDATE INVOICES SET payment_id=%s, client_id=%s, details=%s WHERE invoice_id=%s"""
    cursor.execute(sql, (factura.payment_id, factura.client_id, factura.details, invoice_id))
    conn.commit()

    cursor.close()
    conn.close()

    return factura

# 🔹 Eliminar factura
@router.delete("/{invoice_id}")
def delete_invoices(invoice_id: int, current_user: str = Depends(get_current_user)):
    """Elimina una factura por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM INVOICES WHERE invoice_id = %s", (invoice_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Factura eliminada correctamente"}
