from fastapi import FastAPI
from api.routes import auth, usuarios,clientes, vehiculos,parqueaderos, tarifas,registro_ingresos, pago, factura
from core.security import create_super_user # Importamos la función que crea el superusuario

app = FastAPI()

# Crear el superusuario al iniciar la app, si no hay un superusuario, se cree uno.
create_super_user()

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
app.include_router(vehiculos.router, prefix="/vehiculos", tags=["Vehículos"])
app.include_router(parqueaderos.router, prefix="/parqueaderos", tags=["Parqueaderos"])
app.include_router(tarifas.router, prefix="/tarifas", tags=["Tarifas"])
app.include_router(registro_ingresos.router, prefix="/registros_ingreso", tags=["Registros de Ingreso"])
app.include_router(pago.router, prefix="/pagos", tags=["Pagos"])
app.include_router(factura.router, prefix="/facturas", tags=["Facturas"])

@app.get("/")
def home():
    return {"message": "API de parqueadero activa"}
