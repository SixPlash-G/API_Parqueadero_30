from fastapi import APIRouter, Depends, HTTPException
from src.db.database import get_db_connection
from src.models.registro_ingreso import RegistroIngreso, EstadoRegistro
from src.core.security import get_current_user  # Protección de rutas

router = APIRouter()

# 🔹 Crear Registro de Ingreso
@router.post("/", response_model=RegistroIngreso)
def create_registro(registro: RegistroIngreso, current_user: str = Depends(get_current_user)):
    """Registra un nuevo ingreso de vehículo"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """INSERT INTO REGISTRO_INGRESO 
                 (vehiculo_id, usuario_id, tarifa_id, fecha_ingreso, estado)
                 VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (registro.vehiculo_id, registro.usuario_id, registro.tarifa_id, registro.fecha_ingreso, registro.estado.value))
        conn.commit()

        registro.registro_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return registro
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error al registrar el ingreso")

# 🔹 Obtener todos los Registros de Ingreso
@router.get("/", response_model=list[RegistroIngreso])
def get_registros(current_user: str = Depends(get_current_user)):
    """Devuelve la lista de todos los registros de ingreso"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM REGISTRO_INGRESO")
    registros = cursor.fetchall()

    cursor.close()
    conn.close()

    # 🔹 Convertimos fechas a string para evitar errores
    for registro in registros:
        registro["fecha_ingreso"] = registro["fecha_ingreso"].strftime("%Y-%m-%d %H:%M:%S")
        if registro["fecha_salida"]:
            registro["fecha_salida"] = registro["fecha_salida"].strftime("%Y-%m-%d %H:%M:%S")

    return registros

# 🔹 Obtener Registro por ID
@router.get("/{registro_id}", response_model=RegistroIngreso)
def get_registro(registro_id: int, current_user: str = Depends(get_current_user)):
    """Devuelve un registro de ingreso por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM REGISTRO_INGRESO WHERE registro_id = %s", (registro_id,))
    registro = cursor.fetchone()

    cursor.close()
    conn.close()

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    # 🔹 Convertimos fechas a string
    registro["fecha_ingreso"] = registro["fecha_ingreso"].strftime("%Y-%m-%d %H:%M:%S")
    if registro["fecha_salida"]:
        registro["fecha_salida"] = registro["fecha_salida"].strftime("%Y-%m-%d %H:%M:%S")

    return registro

# 🔹 Actualizar Registro de Ingreso
@router.put("/{registro_id}", response_model=RegistroIngreso)
def update_registro(registro_id: int, registro: RegistroIngreso, current_user: str = Depends(get_current_user)):
    """Actualiza los datos de un registro de ingreso"""
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = """UPDATE REGISTRO_INGRESO 
             SET vehiculo_id=%s, usuario_id=%s, tarifa_id=%s, fecha_ingreso=%s, fecha_salida=%s, 
                 tiempo_total=%s, monto_total=%s, estado=%s
             WHERE registro_id=%s"""
    cursor.execute(sql, (
        registro.vehiculo_id, registro.usuario_id, registro.tarifa_id, registro.fecha_ingreso, 
        registro.fecha_salida, registro.tiempo_total, registro.monto_total, registro.estado.value, registro_id
    ))
    conn.commit()

    cursor.close()
    conn.close()

    return registro

# 🔹 Finalizar Registro de Ingreso
@router.put("/{registro_id}/finalizar")
def finalizar_registro(registro_id: int, current_user: str = Depends(get_current_user)):
    """Marca un registro de ingreso como finalizado, calcula tiempo y monto total"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM REGISTRO_INGRESO WHERE registro_id = %s", (registro_id,))
    registro = cursor.fetchone()

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    if registro["estado"] == "finalizado":
        raise HTTPException(status_code=400, detail="El registro ya está finalizado")

    # 🔹 Calcular tiempo total en minutos y monto total
    from datetime import datetime
    fecha_salida = datetime.now()
    fecha_ingreso = registro["fecha_ingreso"]
    tiempo_total = int((fecha_salida - fecha_ingreso).total_seconds() / 60)

    # 🔹 Obtener el valor de la tarifa
    cursor.execute("SELECT valor_hora FROM TARIFAS WHERE tarifa_id = %s", (registro["tarifa_id"],))
    tarifa = cursor.fetchone()

    if not tarifa:
        raise HTTPException(status_code=404, detail="Tarifa no encontrada")

    monto_total = (tiempo_total / 60) * tarifa["valor_hora"]

    # 🔹 Actualizar el registro
    sql = """UPDATE REGISTRO_INGRESO 
             SET fecha_salida=%s, tiempo_total=%s, monto_total=%s, estado=%s 
             WHERE registro_id=%s"""
    cursor.execute(sql, (fecha_salida, tiempo_total, monto_total, "finalizado", registro_id))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Registro finalizado", "tiempo_total": tiempo_total, "monto_total": monto_total}

# 🔹 Eliminar Registro de Ingreso
@router.delete("/{registro_id}")
def delete_registro(registro_id: int, current_user: str = Depends(get_current_user)):
    """Elimina un registro de ingreso por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM REGISTRO_INGRESO WHERE registro_id = %s", (registro_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Registro eliminado correctamente"}
