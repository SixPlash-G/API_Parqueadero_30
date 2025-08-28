from fastapi import APIRouter, Depends, HTTPException
from src.db.database import get_db_connection
from src.models.factura import Factura
from src.core.security import get_current_user

router = APIRouter()

# 🔹 Crear factura
@router.post("/", response_model=Factura)
def create_factura(factura: Factura, current_user: str = Depends(get_current_user)):
    """Registra una nueva factura"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """INSERT INTO FACTURAS (pago_id, cliente_id, detalle)
                 VALUES (%s, %s, %s)"""
        cursor.execute(sql, (factura.pago_id, factura.cliente_id, factura.detalle))
        conn.commit()

        factura.factura_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return factura
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Error al crear factura: {str(e)}")

# 🔹 Obtener todas las facturas
@router.get("/", response_model=list[Factura])
def get_facturas(current_user: str = Depends(get_current_user)):
    """Devuelve todas las facturas registradas"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT factura_id, pago_id, cliente_id, detalle, fecha_emision FROM FACTURAS")
    facturas = cursor.fetchall()

    cursor.close()
    conn.close()

    return facturas

# 🔹 Obtener una factura por ID
@router.get("/{factura_id}", response_model=Factura)
def get_factura(factura_id: int, current_user: str = Depends(get_current_user)):
    """Devuelve una factura específica"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT factura_id, pago_id, cliente_id, detalle, fecha_emision FROM FACTURAS WHERE factura_id = %s", (factura_id,))
    factura = cursor.fetchone()

    cursor.close()
    conn.close()

    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    return factura

# 🔹 Actualizar factura
@router.put("/{factura_id}", response_model=Factura)
def update_factura(factura_id: int, factura: Factura, current_user: str = Depends(get_current_user)):
    """Actualiza una factura"""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """UPDATE FACTURAS SET pago_id=%s, cliente_id=%s, detalle=%s WHERE factura_id=%s"""
    cursor.execute(sql, (factura.pago_id, factura.cliente_id, factura.detalle, factura_id))
    conn.commit()

    cursor.close()
    conn.close()

    return factura

# 🔹 Eliminar factura
@router.delete("/{factura_id}")
def delete_factura(factura_id: int, current_user: str = Depends(get_current_user)):
    """Elimina una factura por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM FACTURAS WHERE factura_id = %s", (factura_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Factura eliminada correctamente"}
