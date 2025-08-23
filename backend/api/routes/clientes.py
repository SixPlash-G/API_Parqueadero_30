from fastapi import APIRouter, Depends, HTTPException
from db.database import get_db_connection
from models.cliente import Cliente
from core.security import get_current_user  # Protección de rutas

router = APIRouter()

# 🔹 Crear Cliente
@router.post("/", response_model=Cliente)
def create_cliente(cliente: Cliente, current_user: str = Depends(get_current_user)):
    """Registra un nuevo cliente"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """INSERT INTO CLIENTES (nombre, email, celular) VALUES (%s, %s, %s)"""
        cursor.execute(sql, (cliente.nombre, cliente.email, cliente.celular))
        conn.commit()

        cliente.cliente_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return cliente
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error al crear cliente")

# 🔹 Obtener todos los Clientes
@router.get("/", response_model=list[Cliente])
def get_clientes(current_user: str = Depends(get_current_user)):
    """Devuelve la lista de todos los clientes"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT cliente_id, nombre, email, celular, created_at FROM CLIENTES")
    clientes = cursor.fetchall()

    cursor.close()
    conn.close()

    # 🔹 Convertimos `created_at` a string
    for cliente in clientes:
        cliente["created_at"] = cliente["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return clientes

# 🔹 Obtener Cliente por ID
@router.get("/{cliente_id}", response_model=Cliente)
def get_cliente(cliente_id: int, current_user: str = Depends(get_current_user)):
    """Devuelve un cliente por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT cliente_id, nombre, email, celular, created_at FROM CLIENTES WHERE cliente_id = %s", (cliente_id,))
    cliente = cursor.fetchone()

    cursor.close()
    conn.close()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # 🔹 Convertimos `created_at` a string
    cliente["created_at"] = cliente["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return cliente

# 🔹 Actualizar Cliente
@router.put("/{cliente_id}", response_model=Cliente)
def update_cliente(cliente_id: int, cliente: Cliente, current_user: str = Depends(get_current_user)):
    """Actualiza los datos de un cliente"""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """UPDATE CLIENTES SET nombre=%s, email=%s, celular=%s WHERE cliente_id=%s"""
    cursor.execute(sql, (cliente.nombre, cliente.email, cliente.celular, cliente_id))
    conn.commit()

    cursor.close()
    conn.close()

    return cliente

# 🔹 Eliminar Cliente
@router.delete("/{cliente_id}")
def delete_cliente(cliente_id: int, current_user: str = Depends(get_current_user)):
    """Elimina un cliente por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM CLIENTES WHERE cliente_id = %s", (cliente_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Cliente eliminado correctamente"}
