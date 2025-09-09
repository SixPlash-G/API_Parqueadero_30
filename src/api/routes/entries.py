from fastapi import APIRouter, Depends, HTTPException
from src.db.database import get_db_connection
from src.models.entry import RegistroIngreso, EstadoRegistro
from src.core.security import get_current_user  # Protección de rutas

router = APIRouter()

# 🔹 Crear Registro de Ingreso
@router.post("/", response_model=RegistroIngreso)
def create_entries(registro: RegistroIngreso, current_user: str = Depends(get_current_user)):
    """Registra un nuevo ingreso de vehículo"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """INSERT INTO ENTRIES 
                 (vehicle_id, user_id, rate_id, entry_date, status)
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (registro.vehicle_id, registro.user_id, registro.rate_id, registro.entry_date, registro.status.value))
        conn.commit()

        registro.entry_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return registro
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error al registrar el ingreso")

# 🔹 Obtener todos los Registros de Ingreso
@router.get("/", response_model=list[RegistroIngreso])
def get_entries(current_user: str = Depends(get_current_user)):
    """Devuelve la lista de todos los registros de ingreso"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ENTRIES")
    registros = cursor.fetchall()

    cursor.close()
    conn.close()

    # 🔹 Convertimos fechas a string para evitar errores
    for registro in registros:
        registro["entry_date"] = registro["entry_date"].strftime("%Y-%m-%d %H:%M:%S")
        if registro.get("exit_date"):
            registro["exit_date"] = registro["exit_date"].strftime("%Y-%m-%d %H:%M:%S")

    return registros

# 🔹 Obtener Registro por ID
@router.get("/{entry_id}", response_model=RegistroIngreso)
def get_entries(entry_id: int, current_user: str = Depends(get_current_user)):
    """Devuelve un registro de ingreso por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ENTRIES WHERE entry_id = %s", (entry_id,))
    registro = cursor.fetchone()

    cursor.close()
    conn.close()

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    # 🔹 Convertimos fechas a string
    registro["entry_date"] = registro["entry_date"].strftime("%Y-%m-%d %H:%M:%S")
    if registro.get("exit_date"):
        registro["exit_date"] = registro["exit_date"].strftime("%Y-%m-%d %H:%M:%S")

    return registro

# 🔹 Actualizar Registro de Ingreso
@router.put("/{entry_id}", response_model=RegistroIngreso)
def update_entries(entry_id: int, registro: RegistroIngreso, current_user: str = Depends(get_current_user)):
    """Actualiza los datos de un registro de ingreso"""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """UPDATE ENTRIES 
             SET vehicle_id=%s, user_id=%s, rate_id=%s, entry_date=%s, exit_date=%s, 
                 total_time=%s, total_amount=%s, status=%s
             WHERE entry_id=%s"""
    cursor.execute(sql, (
        registro.vehicle_id, registro.user_id, registro.rate_id, registro.entry_date, 
        registro.exit_date, registro.total_time, registro.total_amount, registro.status.value, entry_id
    ))
    conn.commit()

    cursor.close()
    conn.close()

    return registro

# 🔹 Finalizar Registro de Ingreso
@router.put("/{entry_id}/finalizar")
def finalizar_entries(entry_id: int, current_user: str = Depends(get_current_user)):
    """Marca un registro de ingreso como finalizado, calcula tiempo y monto total"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ENTRIES WHERE entry_id = %s", (entry_id,))
    registro = cursor.fetchone()

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    if registro["status"] == "finished":
        raise HTTPException(status_code=400, detail="El registro ya está finalizado")

    # 🔹 Calcular tiempo total en minutos y monto total
    from datetime import datetime
    exit_date = datetime.now()
    entry_date = registro["entry_date"]
    if isinstance(entry_date, str):
        entry_date = datetime.strptime(entry_date, "%Y-%m-%d %H:%M:%S")
    total_time = int((exit_date - entry_date).total_seconds() / 60)

    # 🔹 Obtener el valor de la tarifa
    cursor.execute("SELECT hourly_rate FROM RATES WHERE rate_id = %s", (registro["rate_id"],))
    rate = cursor.fetchone()

    if not rate:
        raise HTTPException(status_code=404, detail="Tarifa no encontrada")

    total_amount = (total_time / 60) * float(rate["hourly_rate"])

    # 🔹 Actualizar el registro
    sql = """UPDATE ENTRIES 
             SET exit_date=%s, total_time=%s, total_amount=%s, status=%s 
             WHERE entry_id=%s"""
    cursor.execute(sql, (exit_date, total_time, total_amount, "finished", entry_id))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Registro finalizado", "total_time": total_time, "total_amount": total_amount}

# 🔹 Eliminar Registro de Ingreso
@router.delete("/{entry_id}")
def delete_entries(entry_id: int, current_user: str = Depends(get_current_user)):
    """Elimina un registro de ingreso por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM ENTRIES WHERE entry_id = %s", (entry_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Registro eliminado correctamente"}
