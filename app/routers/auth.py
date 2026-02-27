from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.services.auth_service import AuthService
from datetime import timedelta
from app.services.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.user import UserCreate, Token
from pydantic import BaseModel

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class GoogleLoginRequest(BaseModel):
    email: str

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = AuthService.get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email, 
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Return token immediately
    access_token = AuthService.create_access_token(data={"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not AuthService.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/google", response_model=Token)
def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    # Mock Google Login Endpoint. Real production uses OAuth2 validation flow.
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Create a mock user on the fly if they don't exist
        mock_pass = AuthService.get_password_hash("mock_google_oauth_pass")
        user = User(email=request.email, hashed_password=mock_pass)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Return success anyway to prevent email enumeration
        return {"msg": "If an account exists, a reset link was sent."}
    
    # Generate a temporary short-lived JWT for password reset
    reset_token = AuthService.create_access_token(data={"sub": str(user.id), "type": "reset"})
    
    # IN A REAL APP: Send this link via email. Here, we print it to the console.
    reset_link = f"http://localhost:5173/reset-password?token={reset_token}"
    print(f"\n{'='*50}\nPASSWORD RESET LINK GENERATED:\n{reset_link}\n{'='*50}\n")
    
    return {"msg": "If an account exists, a reset link was sent."}

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    from jose import jwt, JWTError
    from app.services.auth_service import SECRET_KEY, ALGORITHM
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if not user_id or token_type != "reset":
            raise HTTPException(status_code=400, detail="Invalid reset token")
            
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Update password
        user.hashed_password = AuthService.get_password_hash(request.new_password)
        db.commit()
        return {"msg": "Password updated successfully"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
