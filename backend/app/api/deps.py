from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def require_parent(user=Depends(get_current_user)):
    if user.get("role") != "parent":
        raise HTTPException(status_code=403, detail="Parent access required")
    return user


def require_child(user=Depends(get_current_user)):
    if user.get("role") not in ("child", "parent"):
        raise HTTPException(status_code=403, detail="Access denied")
    return user
