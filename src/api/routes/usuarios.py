from fastapi import APIRouter, Depends, HTTPException, status
from src.core.security import hash_password, verify_password, get_current_user
from src.db.database import get_db_connection
from src.models.usuario import Usuario

router = APIRouter()

# 🔹 Crear usuario (Registro)
@router.post("/", response_model=Usuario)
def create_usuario(usuario: Usuario, current_user: str = Depends(get_current_user)):  # 🔒 Validación agregada
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
        cursor.close()
        conn.close()

        return usuario
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error al crear usuario")

# 🔹 Obtener todos los usuarios
@router.get("/", response_model=list[Usuario])
def get_usuarios(current_user: str = Depends(get_current_user)):
    """Devuelve la lista de todos los usuarios"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, name, email, phone, is_superuser FROM USERS")
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return usuarios

# 🔹 Obtener usuario por ID
@router.get("/{user_id}", response_model=Usuario)
def get_usuario(user_id: int, current_user: str = Depends(get_current_user)):
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
def update_usuario(user_id: int, usuario: Usuario, current_user: str = Depends(get_current_user)):
    """Actualiza los datos de un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = hash_password(usuario.password)

    sql = "UPDATE USERS SET name=%s, email=%s, phone=%s, password=%s, is_superuser=%s WHERE user_id=%s"
    cursor.execute(sql, (usuario.name, usuario.email, usuario.phone, hashed_password, usuario.is_superuser, user_id))
    conn.commit()

    cursor.close()
    conn.close()

    return usuario

# 🔹 Eliminar usuario
@router.delete("/{user_id}")
def delete_usuario(user_id: int, current_user: str = Depends(get_current_user)):
    """Elimina un usuario por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM USERS WHERE user_id = %s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Usuario eliminado correctamente"}
