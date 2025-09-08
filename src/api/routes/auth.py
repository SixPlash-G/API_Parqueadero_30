from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src.core.security import verify_password, create_access_token, hash_password
from src.db.database import get_db_connection

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/login")
async def login(request: Request):
    """User authentication (accepts JSON and form-data)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
    else:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

    cursor.execute("SELECT * FROM USERS WHERE email = %s", (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user or not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token({"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/create_user")
def create_user(email: str, password: str, token: str = Depends(oauth2_scheme)):
    """Create a new user only if superuser"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM USERS WHERE email = %s", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    # Verify that the creator is a superuser
    cursor.execute("SELECT is_superuser FROM USERS WHERE email = %s", (token,))
    user = cursor.fetchone()

    if not user or not user["is_superuser"]:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to create users")

    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO USERS (email, password, is_superuser) VALUES (%s, %s, %s)",
                   (email, hashed_password, False))  # Creating a regular user, not a superuser
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "User created successfully"}
