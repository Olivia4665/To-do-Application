from fastapi import FastAPI, Depends, HTTPException, status, Header, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from typing import Optional
import secrets
import json
import base64
from pydantic import BaseModel
from passlib.context import CryptContext
from models import SessionLocal, User, Todo

# Setup logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Mock token settings
MOCK_TOKEN_SECRET = "mock-secret-key-12345"
MOCK_TOKEN_PREFIX = "mock_"

app = FastAPI(title="Todo API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Password utilities
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# User authentication
def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

# Pydantic models for JSON requests
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TodoUpdate(BaseModel):
    completed: bool

# Mock token functions
def create_mock_token(username: str, expires_minutes: int = 30) -> str:
    """Create a simple mock token (not a real JWT)"""
    expire_time = datetime.utcnow() + timedelta(minutes=expires_minutes)
    
    # Create a simple token payload
    payload = {
        "sub": username,
        "exp": expire_time.timestamp(),
        "type": "mock_token"
    }
    
    # Convert to JSON and base64 encode
    payload_json = json.dumps(payload)
    payload_encoded = base64.urlsafe_b64encode(payload_json.encode()).decode()
    
    # Add a simple signature (not cryptographically secure)
    signature = secrets.token_urlsafe(16)
    
    return f"{MOCK_TOKEN_PREFIX}{payload_encoded}.{signature}"

def validate_mock_token(token: str) -> dict:
    """Validate and decode mock token"""
    if not token.startswith(MOCK_TOKEN_PREFIX):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    try:
        # Remove prefix and split
        token_without_prefix = token[len(MOCK_TOKEN_PREFIX):]
        payload_encoded, signature = token_without_prefix.split('.', 1)
        
        # Decode payload
        payload_json = base64.urlsafe_b64decode(payload_encoded).decode()
        payload = json.loads(payload_json)
        
        # Check expiration
        if datetime.utcnow().timestamp() > payload["exp"]:
            raise HTTPException(status_code=401, detail="Token expired")
            
        return payload
        
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=401, detail="Invalid token")

# Dependency to get current user from mock token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = validate_mock_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except HTTPException:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.post("/register")
def register(
    username: str = Form(...),  
    email: str = Form(...),       
    password: str = Form(...),  
    db: Session = Depends(get_db)
):
    logger.info(f"=== REGISTRATION STARTED ===")
    logger.info(f"Username: {username}, Email: {email}")
    
    try:
        # Check if user already exists
        db_user = db.query(User).filter(User.username == username).first()
        if db_user:
            logger.warning(f"Registration failed - username already exists: {username}")
            raise HTTPException(status_code=400, detail="Username already registered")
        
        db_email = db.query(User).filter(User.email == email).first()
        if db_email:
            logger.warning(f"Registration failed - email already exists: {email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_password = get_password_hash(password)
        logger.info(f"Password hashed successfully")
        
        new_user = User(username=username, email=email, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"User saved to database with ID: {new_user.id}")
        
        # Create mock token
        access_token = create_mock_token(username)
        
        logger.info(f"Mock token generated successfully: {access_token}")
        logger.info(f"User registered and automatically logged in: {username}")
        
        return {
            "message": "User created successfully",
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        logger.error(f"Registration failed with error: {str(e)}")
        raise

@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    logger.info(f"=== LOGIN ATTEMPT ===")
    logger.info(f"Username: {username}")
    
    user = authenticate_user(db, username, password)
    if not user:
        logger.warning(f"Login failed for username: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create mock token
    access_token = create_mock_token(user.username)
    logger.info(f"Generated token: {access_token}")
    
    logger.info(f"Login successful for username: {username}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    logger.info(f"=== PROTECTED ROUTE ACCESSED ===")
    logger.info(f"User: {current_user.username}")
    logger.info(f"Token validated successfully")
    return {"message": f"Hello {current_user.username}, you are authenticated!"}

# Todo routes with JSON support
@app.get("/todos")
def get_todos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    todos = db.query(Todo).filter(Todo.owner_id == current_user.id).all()
    return todos

@app.post("/todos")
def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Creating todo for user {current_user.username}: {todo_data}")
    
    # Validate title
    if not todo_data.title or not todo_data.title.strip():
        raise HTTPException(status_code=422, detail="Title cannot be empty")
    
    new_todo = Todo(
        title=todo_data.title.strip(),
        description=todo_data.description.strip() if todo_data.description else "",
        owner_id=current_user.id
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    
    logger.info(f"Todo created successfully: {new_todo.id}")
    return new_todo

@app.put("/todos/{todo_id}")
def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Updating todo {todo_id} for user {current_user.username}: {todo_data}")
    
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo.completed = todo_data.completed
    db.commit()
    db.refresh(todo)
    
    logger.info(f"Todo updated successfully: {todo_id}")
    return todo

@app.delete("/todos/{todo_id}")
def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Deleting todo {todo_id} for user {current_user.username}")
    
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.owner_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(todo)
    db.commit()
    
    logger.info(f"Todo deleted successfully: {todo_id}")
    return {"message": "Todo deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)