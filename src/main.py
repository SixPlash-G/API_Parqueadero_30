from fastapi import FastAPI
from src.api.routes import auth, anpr, clients, entries, invoices, parkings, payments, rates, users, vehicles
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
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(clients.router, prefix="/clients", tags=["Clients"])
app.include_router(vehicles.router, prefix="/vehicles", tags=["Vehicles"])
app.include_router(parkings.router, prefix="/parkings", tags=["Parkings"])
app.include_router(rates.router, prefix="/rates", tags=["Rates"])
app.include_router(entries.router, prefix="/entries", tags=["Entries"])
app.include_router(payments.router, prefix="/payments", tags=["Payments"])
app.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])

@app.get("/")
def home():
    return {"message": "Parking API is running"}
