"""SQLAlchemy setup — รองรับทั้ง SQLite (dev) และ PostgreSQL (Railway prod)

ใช้ env var `DATABASE_URL`:
    - Dev (ไม่ตั้ง): default = sqlite:///./local.db
    - Prod (Railway): postgresql://user:pass@host:5432/dbname

ตัวอย่างใน .env:
    DATABASE_URL=postgresql://user:pass@containers-us-west-X.railway.app:7777/railway
"""
from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ============================================================
# Database URL — env-driven
# ============================================================
DEFAULT_SQLITE_PATH = Path(__file__).parent.parent / "local.db"
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}",
)

# Railway sometimes returns postgres:// (legacy) — SQLAlchemy ต้องการ postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

_engine_kwargs = {}
if DATABASE_URL.startswith("sqlite:"):
    # SQLite ต้องการ flag นี้สำหรับ multi-thread (uvicorn workers)
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================
# Dependency for FastAPI routes
# ============================================================
def get_db() -> Session:
    """FastAPI dependency — yields a session, ensures close"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session() -> Session:
    """Synchronous helper — caller is responsible for close()"""
    return SessionLocal()
