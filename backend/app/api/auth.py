from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.models.parent import Parent
from app.config import settings
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(data: dict, expires_minutes: int = 60 * 12) -> str:
    payload = {**data, "exp": datetime.utcnow() + timedelta(minutes=expires_minutes)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    parent = db.query(Parent).filter(Parent.username == req.username).first()
    if not parent or not pwd_context.verify(req.password, parent.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": str(parent.id), "role": "parent"})
    return TokenResponse(access_token=token, role="parent")
