from fastapi import APIRouter, Depends, HTTPException
from src.db.database import get_db_connection
from src.models.vehiculo import Vehiculo
from src.core.security import get_current_user  # Protección de rutas

router = APIRouter()

# 🔹 Crear Vehículo
@router.post("/", response_model=Vehiculo)
def create_vehiculo(vehiculo: Vehiculo, current_user: str = Depends(get_current_user)):
    """Registra un nuevo vehículo"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """INSERT INTO VEHICULOS (cliente_id, placa, marca, modelo) VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (vehiculo.cliente_id, vehiculo.placa, vehiculo.marca, vehiculo.modelo))
        conn.commit()

        vehiculo.vehiculo_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return vehiculo
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error al registrar el vehículo")

# 🔹 Obtener todos los Vehículos
@router.get("/", response_model=list[Vehiculo])
def get_vehiculos(current_user: str = Depends(get_current_user)):
    """Devuelve la lista de todos los vehículos"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT vehiculo_id, cliente_id, placa, marca, modelo, created_at FROM VEHICULOS")
    vehiculos = cursor.fetchall()

    cursor.close()
    conn.close()

    # 🔹 Convertimos `created_at` a string
    for vehiculo in vehiculos:
        vehiculo["created_at"] = vehiculo["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return vehiculos

# 🔹 Obtener Vehículo por ID
@router.get("/{vehiculo_id}", response_model=Vehiculo)
def get_vehiculo(vehiculo_id: int, current_user: str = Depends(get_current_user)):
    """Devuelve un vehículo por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT vehiculo_id, cliente_id, placa, marca, modelo, created_at FROM VEHICULOS WHERE vehiculo_id = %s", (vehiculo_id,))
    vehiculo = cursor.fetchone()

    cursor.close()
    conn.close()

    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    # 🔹 Convertimos `created_at` a string
    vehiculo["created_at"] = vehiculo["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return vehiculo

# 🔹 Actualizar Vehículo
@router.put("/{vehiculo_id}", response_model=Vehiculo)
def update_vehiculo(vehiculo_id: int, vehiculo: Vehiculo, current_user: str = Depends(get_current_user)):
    """Actualiza los datos de un vehículo"""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """UPDATE VEHICULOS SET cliente_id=%s, placa=%s, marca=%s, modelo=%s WHERE vehiculo_id=%s"""
    cursor.execute(sql, (vehiculo.cliente_id, vehiculo.placa, vehiculo.marca, vehiculo.modelo, vehiculo_id))
    conn.commit()

    cursor.close()
    conn.close()

    return vehiculo

# 🔹 Eliminar Vehículo
@router.delete("/{vehiculo_id}")
def delete_vehiculo(vehiculo_id: int, current_user: str = Depends(get_current_user)):
    """Elimina un vehículo por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM VEHICULOS WHERE vehiculo_id = %s", (vehiculo_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Vehículo eliminado correctamente"}
