from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MusicItem, User

app = FastAPI(
    title="Music Collection Manager API",
    version="0.1.0",
    description="Backend für die Verwaltung einer persönlichen Musiksammlung (KV Service Engineering, Übung 1).",
)


@app.get("/health/db", tags=["health"], summary="Datenbankverbindung prüfen")
def health_db(db: Session = Depends(get_db)) -> dict:
    """Prüft, ob die Verbindung zur Supabase-Datenbank funktioniert."""
    try:
        version = db.execute(text("SELECT version()")).scalar_one()
        users = db.scalar(select(func.count()).select_from(User))
        items = db.scalar(select(func.count()).select_from(MusicItem))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"Datenbank nicht erreichbar: {exc}") from exc
    return {"status": "ok", "database": version, "users": users, "music_items": items}
