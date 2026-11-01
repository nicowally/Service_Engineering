from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# pool_pre_ping: prüft Verbindungen vor der Verwendung – wichtig bei Supabase,
# weil der Pooler inaktive Verbindungen nach einiger Zeit schließt.
engine = create_engine(
    settings.database_url, # engine stellt die wirkliche verbindung zur Datenbank her, aber erst wenn was aus der datenbank benötigt wird
    echo=settings.sql_echo, #gibt den sql code im terminal aus
    pool_pre_ping=True, #prüft ob leitung zwischen backend und datenbank noch aktiv ist, mit false wird die überprüfung nicht gestartet
    pool_size=5, #bis zu 5 Leitungen zwischen backend und datenbank möglich, bleiben offen auch bei keiner nutzung
    max_overflow=5, #wenn mehr als 5 leitungen gleichzeitig gebraucht werden, können kurzzeitig 5 weitere geöffnet werden,schließen sich wieder
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False) #Ist die Vorlage dafür, was an die Datenbank gesendet werden soll. bind=engine - holt sich die leitung, autoflush - erst bei commit wird alles der datenbank übergeben, expire on commit - übergebene daten können weiterhin nach commit gelesen werden zb song.title


class Base(DeclarativeBase): #Base Überklasse für klassen, die die tabellen in supabase defineiren
    """Basisklasse für alle ORM-Modelle."""


def get_db() -> Generator[Session, None, None]: #Session die bei jeder aktion mit der Datenbank aufgerufen wird
    """FastAPI-Dependency: eine DB-Session pro Request."""
    db = SessionLocal() #erstellt nur die session, die eine leitung belegt
    try:
        yield db #wird dem endpoint übergeben. Dort wird dann gelöscht, geändert, hinzugefügt etc
    finally:
        db.close() #session wird beendet, die leitung wird wieder frei
