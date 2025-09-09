from fastapi import APIRouter, Depends, HTTPException
from src.db.database import get_db_connection
from src.models.vehicle import Vehiculo
from src.core.security import get_current_user  # Protección de rutas

router = APIRouter()

# 🔹 Crear Vehículo
@router.post("/", response_model=Vehiculo)
def create_vehicles(vehiculo: Vehiculo, current_user: str = Depends(get_current_user)):
    """Registra un nuevo vehículo"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """INSERT INTO VEHICLES (client_id, plate, brand, model) VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (vehiculo.client_id, vehiculo.plate, vehiculo.brand, vehiculo.model))
        conn.commit()

        vehiculo.vehicle_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return vehiculo
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error al registrar el vehículo")

# 🔹 Obtener todos los Vehículos
@router.get("/", response_model=list[Vehiculo])
def get_vehicles(current_user: str = Depends(get_current_user)):
    """Devuelve la lista de todos los vehículos"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT vehicle_id, client_id, plate, brand, model, created_at FROM VEHICLES")
    vehiculos = cursor.fetchall()

    cursor.close()
    conn.close()

    # 🔹 Convertimos `created_at` a string
    for vehiculo in vehiculos:
        vehiculo["created_at"] = vehiculo["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return vehiculos

# 🔹 Obtener Vehículo por ID
@router.get("/{vehicle_id}", response_model=Vehiculo)
def get_vehicles(vehicle_id: int, current_user: str = Depends(get_current_user)):
    """Devuelve un vehículo por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT vehicle_id, client_id, plate, brand, model, created_at FROM VEHICLES WHERE vehicle_id = %s", (vehicle_id,))
    vehiculo = cursor.fetchone()

    cursor.close()
    conn.close()

    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")

    # 🔹 Convertimos `created_at` a string
    vehiculo["created_at"] = vehiculo["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return vehiculo

# 🔹 Actualizar Vehículo
@router.put("/{vehicle_id}", response_model=Vehiculo)
def update_vehicles(vehicle_id: int, vehiculo: Vehiculo, current_user: str = Depends(get_current_user)):
    """Actualiza los datos de un vehículo"""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """UPDATE VEHICLES SET client_id=%s, plate=%s, brand=%s, model=%s WHERE vehicle_id=%s"""
    cursor.execute(sql, (vehiculo.client_id, vehiculo.plate, vehiculo.brand, vehiculo.model, vehicle_id))
    conn.commit()

    cursor.close()
    conn.close()

    return vehiculo

# 🔹 Eliminar Vehículo
@router.delete("/{vehicle_id}")
def delete_vehicles(vehicle_id: int, current_user: str = Depends(get_current_user)):
    """Elimina un vehículo por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM VEHICLES WHERE vehicle_id = %s", (vehicle_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Vehículo eliminado correctamente"}
