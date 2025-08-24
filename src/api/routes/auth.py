from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.core.security import verify_password, create_access_token, hash_password
from src.db.database import get_db_connection

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Autenticación de usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM USUARIOS WHERE email = %s", (form_data.username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token({"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/create_user")
def create_user(email: str, password: str, token: str = Depends(oauth2_scheme)):
    """Crea un nuevo usuario solo si es superusuario"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe")

    # Verificar que el que crea el usuario es un superusuario
    cursor.execute("SELECT is_superuser FROM usuarios WHERE email = %s", (token,))
    user = cursor.fetchone()

    if not user or not user["is_superuser"]:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para crear usuarios")

    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO usuarios (email, password, is_superuser) VALUES (%s, %s, %s)",
                   (email, hashed_password, False))  # Aquí estamos creando un usuario regular, no un superusuario
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Usuario creado exitosamente"}
