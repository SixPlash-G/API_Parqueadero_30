from fastapi import FastAPI
from src.api.routes import auth, usuarios,clientes, vehiculos,parqueaderos, tarifas,registro_ingresos, pago, factura, anpr
from fastapi.middleware.cors import CORSMiddleware
from src.core.security import create_super_user # Importamos la función que crea el superusuario

app = FastAPI()

# Add CORS middleware to allow OPTIONS method
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods including OPTIONS
    allow_headers=["*"]
)

# Crear el superusuario al iniciar la app, si no hay un superusuario, se cree uno.
create_super_user()

app.include_router(anpr.router, prefix="/anpr", tags=["Plate Detection"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Users"])
app.include_router(clientes.router, prefix="/clientes", tags=["Clients"])
app.include_router(vehiculos.router, prefix="/vehiculos", tags=["Vehicles"])
app.include_router(parqueaderos.router, prefix="/parqueaderos", tags=["Parkings"])
app.include_router(tarifas.router, prefix="/tarifas", tags=["Rates"])
app.include_router(registro_ingresos.router, prefix="/registros_ingreso", tags=["Entries"])
app.include_router(pago.router, prefix="/pagos", tags=["Payments"])
app.include_router(factura.router, prefix="/facturas", tags=["Invoices"])

@app.get("/")
def home():
    return {"message": "Parking API is running"}
