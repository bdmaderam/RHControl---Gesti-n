from datetime import datetime, timedelta, timezone
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.config import settings
from ..db import get_db
from ..models import Usuario
from ..schemas.auth import LoginRequest, LoginResponse
from ..services.auth import verify_password

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.usuario == payload.usuario).first()
    if not user or not verify_password(payload.contraseña, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    token = jwt.encode({"sub": user.usuario, "exp": datetime.now(timezone.utc)+timedelta(hours=8)}, settings.jwt_secret, algorithm="HS256")
    return LoginResponse(access_token=token, usuario=user.usuario, nombre=user.nombre)
