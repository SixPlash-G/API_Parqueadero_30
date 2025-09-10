from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.core.security import hash_password, get_current_user
from src.db.database import get_db_connection
from src.models.user import Usuario
from src.models.paginate import PaginatedResponse


router = APIRouter()

# 🔹 Crear usuario (Registro)
@router.post("/", response_model=Usuario)
def create_user(usuario: Usuario, current_user: str = Depends(get_current_user)):  # 🔒 Validación agregada
    """Registra un nuevo usuario con contraseña encriptada"""
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(usuario.password)

    try:
        sql = """INSERT INTO USERS (name, email, phone, password, is_superuser)
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (usuario.name, usuario.email, usuario.phone, hashed_password, usuario.is_superuser))
        conn.commit()

        usuario.user_id = cursor.lastrowid
        usuario.password = None  # No devolver la contraseña
        cursor.close()
        conn.close()

        return usuario
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error al crear usuario")

# 🔹 Obtener todos los usuarios con busqueda y paginación
@router.get("/", response_model=PaginatedResponse[Usuario])
def get_users(
    search: str | None = Query(None, description="Buscar por nombre o email"),
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Número de resultados por página"),
    current_user: str = Depends(get_current_user)
):
    """Devuelve la lista de todos los usuarios con paginación y búsqueda"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- 1. Calcular total ---
    count_query = "SELECT COUNT(*) as total FROM USERS"
    params = []
    if search:
        count_query += " WHERE name LIKE %s OR email LIKE %s"
        params.extend([f"%{search}%", f"%{search}%"])

    cursor.execute(count_query, tuple(params))
    total = cursor.fetchone()["total"]

     # --- 2. Obtener página de resultados ---
    query = "SELECT user_id, name, email, phone, is_superuser FROM USERS"
    if search:
        query += " WHERE name LIKE %s OR email LIKE %s"
    query += " ORDER BY user_id LIMIT %s OFFSET %s"
    
    offset = (page - 1) * limit
    params_page = params + [limit, offset]

    cursor.execute(query, tuple(params_page))
    rows = cursor.fetchall()

    # Convertir cada fila (dict) en un objeto Usuario
    usuarios = [Usuario(**row) for row in rows]

    cursor.close()
    conn.close()

    return PaginatedResponse[Usuario](
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit,
        data=usuarios
    )

# 🔹 Obtener usuario por ID
@router.get("/{user_id}", response_model=Usuario)
def get_user(user_id: int, current_user: str = Depends(get_current_user)):
    """Devuelve un usuario por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, name, email, phone, is_superuser FROM USERS WHERE user_id = %s", (user_id,))
    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return usuario

# 🔹 Actualizar usuario
@router.put("/{user_id}", response_model=Usuario)
def update_user(user_id: int, usuario: Usuario, current_user: str = Depends(get_current_user)):
    """Actualiza los datos de un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Si no se envía nueva contraseña, no la actualices
    if usuario.password:
        hashed_password = hash_password(usuario.password)
        sql = "UPDATE USERS SET name=%s, email=%s, phone=%s, password=%s, is_superuser=%s WHERE user_id=%s"
        params = (usuario.name, usuario.email, usuario.phone, hashed_password, usuario.is_superuser, user_id)
    else:
        sql = "UPDATE USERS SET name=%s, email=%s, phone=%s, is_superuser=%s WHERE user_id=%s"
        params = (usuario.name, usuario.email, usuario.phone, usuario.is_superuser, user_id)

    cursor.execute(sql, params)
    conn.commit()

    cursor.close()
    conn.close()

    usuario.user_id = user_id
    usuario.password = None  # No devolver la contraseña
    return usuario

# 🔹 Eliminar usuario
@router.delete("/{user_id}")
def delete_user(user_id: int, current_user: str = Depends(get_current_user)):
    """Elimina un usuario por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM USERS WHERE user_id = %s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Usuario eliminado correctamente"}
