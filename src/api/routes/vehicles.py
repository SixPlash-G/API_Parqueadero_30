from fastapi import APIRouter, Depends, HTTPException, Query
from src.db.database import get_db_connection
from src.models.vehicle import Vehiculo
from src.models.paginate import PaginatedResponse
from src.core.security import get_current_user  # Protección de rutas

router = APIRouter()

# 🔹 Crear Vehículo
@router.post("/", response_model=Vehiculo)
def create_vehicle(vehiculo: Vehiculo, current_user: str = Depends(get_current_user)):
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

# 🔹 Obtener todos los Vehículos con busqueda y paginación
@router.get("/", response_model=PaginatedResponse[Vehiculo])
def get_vehicles(
    search: str | None = Query(None, description="Buscar por placa, marca o modelo"),
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(10, ge=1, le=100, description="Número de resultados por página"),
    current_user: str = Depends(get_current_user)
):
    """Devuelve la lista de todos los vehículos con paginación y búsqueda"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- 1. Calcular total ---
    count_query = "SELECT COUNT(*) as total FROM VEHICLES"
    params = []
    if search:
        count_query += " WHERE plate LIKE %s OR brand LIKE %s OR model LIKE %s"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])

    cursor.execute(count_query, tuple(params))
    total = cursor.fetchone()["total"]

    # --- 2. Obtener página de resultados ---
    query = "SELECT vehicle_id, client_id, plate, brand, model, created_at FROM VEHICLES"
    if search:
        query += " WHERE plate LIKE %s OR brand LIKE %s OR model LIKE %s"
    query += " ORDER BY vehicle_id LIMIT %s OFFSET %s"

    offset = (page - 1) * limit
    params_page = params + [limit, offset]

    cursor.execute(query, tuple(params_page))
    rows = cursor.fetchall()

    # Convertimos created_at a string si es datetime
    for row in rows:
        if row["created_at"] and hasattr(row["created_at"], "strftime"):
            row["created_at"] = row["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    vehiculos = [Vehiculo(**row) for row in rows]

    cursor.close()
    conn.close()

    return PaginatedResponse[Vehiculo](
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit,
        data=vehiculos
    )

# 🔹 Obtener Vehículo por ID
@router.get("/{vehicle_id}", response_model=Vehiculo)
def get_vehicle(vehicle_id: int, current_user: str = Depends(get_current_user)):
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
def update_vehicle(vehicle_id: int, vehiculo: Vehiculo, current_user: str = Depends(get_current_user)):
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
def delete_vehicle(vehicle_id: int, current_user: str = Depends(get_current_user)):
    """Elimina un vehículo por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM VEHICLES WHERE vehicle_id = %s", (vehicle_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Vehículo eliminado correctamente"}
