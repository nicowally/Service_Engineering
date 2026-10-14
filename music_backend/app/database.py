from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# pool_pre_ping: prüft Verbindungen vor der Verwendung – wichtig bei Supabase,
# weil der Pooler inaktive Verbindungen nach einiger Zeit schließt.
engine = create_engine(
    settings.database_url,
    echo=settings.sql_echo,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Basisklasse für alle ORM-Modelle."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI-Dependency: eine DB-Session pro Request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
