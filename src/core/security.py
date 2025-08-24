from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from src.db.database import get_db_connection

# Configuración para encriptar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Clave secreta para JWT (cambia esto en producción)
SECRET_KEY = "clave_super_secreta"
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """Encripta la contraseña con bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con la almacenada."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Crea un token JWT sin expiración."""
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    """Valida el JWT y extrae el usuario"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
def create_super_user():
    """Crea un superusuario si no existe uno en la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si ya existe un superusuario
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE is_superuser = TRUE")
    result = cursor.fetchone()

     # Verificar que result no sea None y que tenga el índice 0
    if result is None:
        print("Error: No se pudo obtener el resultado de la consulta.")
        return
    
    print(result)
    # Si no se encuentra ningún superusuario, result será (0,)
    if result['COUNT(*)'] == 0:
        # Crear un superusuario
        hashed_password = hash_password("admin123")  # Cambiar esta contraseña por una segura en producción
        cursor.execute("INSERT INTO usuarios (nombre, email, celular, password, is_superuser) VALUES (%s, %s, %s, %s, %s)",
                       ("admin", "admin@admin.com", "1234567890", hashed_password, True))  # Se crea el superusuario
        conn.commit()
        print("Superusuario creado exitosamente.")
    else:
        print("Ya existe un superusuario.")

    cursor.close()
    conn.close()