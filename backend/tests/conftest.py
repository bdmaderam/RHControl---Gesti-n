import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

# La app debe usar una base SQLite aislada: se define ANTES de importar la app.
DB_FILE = Path(__file__).parent / "test_rhcontrol.db"
os.environ["DATABASE_URL"] = f"sqlite:///{DB_FILE.as_posix()}"
os.environ["JWT_SECRET"] = "secreto-solo-para-pruebas"

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def base_limpia():
    """Cada prueba empieza con las tablas vacías."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def borrar_archivo_al_final():
    yield
    engine.dispose()
    if DB_FILE.exists():
        DB_FILE.unlink()


@pytest.fixture
def client():
    # Sin "with": no se ejecuta el evento startup, que carga datos de ejemplo.
    return TestClient(app)


@pytest.fixture
def auth_headers():
    token = jwt.encode(
        {"sub": "admin", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        settings.jwt_secret,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}