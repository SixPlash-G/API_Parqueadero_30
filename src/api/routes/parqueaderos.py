from fastapi import APIRouter, Depends, HTTPException
from src.db.database import get_db_connection
from src.models.parqueadero import Parqueadero
from src.core.security import get_current_user  # Protección de rutas

router = APIRouter()

# 🔹 Crear Parqueadero
@router.post("/", response_model=Parqueadero)
def create_parqueadero(parqueadero: Parqueadero, current_user: str = Depends(get_current_user)):
    """Registra un nuevo parqueadero"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """INSERT INTO PARQUEADERO (total_espacios, espacios_disponibles) VALUES (%s, %s)"""
        cursor.execute(sql, (parqueadero.total_espacios, parqueadero.espacios_disponibles))
        conn.commit()

        parqueadero.parqueadero_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return parqueadero
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error al registrar el parqueadero")

# 🔹 Obtener todos los Parqueaderos
@router.get("/", response_model=list[Parqueadero])
def get_parqueaderos(current_user: str = Depends(get_current_user)):
    """Devuelve la lista de todos los parqueaderos"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT parqueadero_id, total_espacios, espacios_disponibles, created_at FROM PARQUEADERO")
    parqueaderos = cursor.fetchall()

    cursor.close()
    conn.close()

    # 🔹 Convertimos `created_at` a string
    for parqueadero in parqueaderos:
        parqueadero["created_at"] = parqueadero["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return parqueaderos

# 🔹 Obtener Parqueadero por ID
@router.get("/{parqueadero_id}", response_model=Parqueadero)
def get_parqueadero(parqueadero_id: int, current_user: str = Depends(get_current_user)):
    """Devuelve un parqueadero por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT parqueadero_id, total_espacios, espacios_disponibles, created_at FROM PARQUEADERO WHERE parqueadero_id = %s", (parqueadero_id,))
    parqueadero = cursor.fetchone()

    cursor.close()
    conn.close()

    if not parqueadero:
        raise HTTPException(status_code=404, detail="Parqueadero no encontrado")

    # 🔹 Convertimos `created_at` a string
    parqueadero["created_at"] = parqueadero["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return parqueadero

# 🔹 Actualizar Parqueadero
@router.put("/{parqueadero_id}", response_model=Parqueadero)
def update_parqueadero(parqueadero_id: int, parqueadero: Parqueadero, current_user: str = Depends(get_current_user)):
    """Actualiza los datos de un parqueadero"""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """UPDATE PARQUEADERO SET total_espacios=%s, espacios_disponibles=%s WHERE parqueadero_id=%s"""
    cursor.execute(sql, (parqueadero.total_espacios, parqueadero.espacios_disponibles, parqueadero_id))
    conn.commit()

    cursor.close()
    conn.close()

    return parqueadero

# 🔹 Eliminar Parqueadero
@router.delete("/{parqueadero_id}")
def delete_parqueadero(parqueadero_id: int, current_user: str = Depends(get_current_user)):
    """Elimina un parqueadero por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM PARQUEADERO WHERE parqueadero_id = %s", (parqueadero_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Parqueadero eliminado correctamente"}
