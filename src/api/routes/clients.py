from fastapi import APIRouter, Depends, HTTPException, Query
from src.db.database import get_db_connection
from src.models.client import Cliente
from src.models.paginate import PaginatedResponse
from src.core.security import get_current_user  # Protección de rutas

router = APIRouter()

# 🔹 Crear Cliente
@router.post("/", response_model=Cliente)
def create_client(cliente: Cliente, current_user: str = Depends(get_current_user)):
    """Registra un nuevo cliente"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """INSERT INTO CLIENTS (name, email, phone) VALUES (%s, %s, %s)"""
        cursor.execute(sql, (cliente.name, cliente.email, cliente.phone))
        conn.commit()

        cliente.client_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return cliente
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error al crear cliente")

# 🔹 Obtener todos los Clientes con busqueda y paginación
@router.get("/", response_model=PaginatedResponse[Cliente])
def get_clients(
    search: str | None = Query(None, description="Buscar por nombre o email"),
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Número de resultados por página"),
    current_user: str = Depends(get_current_user)
):
    """Devuelve la lista de todos los clientes con paginación y búsqueda"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- 1. Calcular total ---
    count_query = "SELECT COUNT(*) as total FROM CLIENTS"
    params = []
    if search:
        count_query += " WHERE name LIKE %s OR email LIKE %s"
        params.extend([f"%{search}%", f"%{search}%"])

    cursor.execute(count_query, tuple(params))
    total = cursor.fetchone()["total"]

    # --- 2. Obtener página de resultados ---
    query = "SELECT client_id, name, email, phone, created_at FROM CLIENTS"
    if search:
        query += " WHERE name LIKE %s OR email LIKE %s"
    query += " ORDER BY client_id LIMIT %s OFFSET %s"
    
    offset = (page - 1) * limit
    params_page = params + [limit, offset]

    cursor.execute(query, tuple(params_page))
    rows = cursor.fetchall()

    clientes = [Cliente(**row) for row in rows]

    cursor.close()
    conn.close()

    return PaginatedResponse[Cliente](
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit,
        data=clientes
    )

# 🔹 Obtener Cliente por ID
@router.get("/{client_id}", response_model=Cliente)
def get_client(client_id: int, current_user: str = Depends(get_current_user)):
    """Devuelve un cliente por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT client_id, name, email, phone, created_at FROM CLIENTS WHERE client_id = %s", (client_id,))
    cliente = cursor.fetchone()

    cursor.close()
    conn.close()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # 🔹 Convertimos `created_at` a string
    cliente["created_at"] = cliente["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return cliente

# 🔹 Actualizar Cliente
@router.put("/{client_id}", response_model=Cliente)
def update_client(client_id: int, cliente: Cliente, current_user: str = Depends(get_current_user)):
    """Actualiza los datos de un cliente"""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """UPDATE CLIENTS SET name=%s, email=%s, phone=%s WHERE client_id=%s"""
    cursor.execute(sql, (cliente.name, cliente.email, cliente.phone, client_id))
    conn.commit()

    cursor.close()
    conn.close()

    return cliente

# 🔹 Eliminar Cliente
@router.delete("/{client_id}")
def delete_client(client_id: int, current_user: str = Depends(get_current_user)):
    """Elimina un cliente por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM CLIENTS WHERE client_id = %s", (client_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Cliente eliminado correctamente"}
