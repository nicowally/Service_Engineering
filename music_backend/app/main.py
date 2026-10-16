
import uuid
from datetime import datetime
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    CollectionEntry,
    Comment,
    MusicItem,
    MusicItemTrack,
    MusicItemType,
    Rating,
    Reaction,
    User,
    UserRole,
)

app = FastAPI(
    title="Music Collection Manager API",
    version="1.0.0",
    description=(
        "Backend für die Verwaltung einer persönlichen Musiksammlung "
        "(KV Service Engineering, Übung 1).\n\n"
        "Testuser: `admin` (Rolle admin), `anna`, `ben` (Rolle user)."
    ),
)

DB = Annotated[Session, Depends(get_db)]


# ===========================================================================
# 1. DTOs
# ===========================================================================
class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TrackCreate(BaseModel):
    """Einzelnen Song anlegen."""

    title: str = Field(min_length=1, max_length=255)
    artist: str | None = None
    album_name: str | None = None
    genre: str | None = None
    release_year: int | None = Field(default=None, ge=1000, le=9999)
    duration_seconds: int | None = Field(default=None, ge=0)
    description: str | None = None
    external_url: str | None = Field(
        default=None, description="Referenz auf den eigentlichen Track, z. B. Spotify-Link"
    )

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "title": "Bohemian Rhapsody", "artist": "Queen", "album_name": "A Night at the Opera",
        "genre": "Rock", "release_year": 1975, "duration_seconds": 354,
        "external_url": "https://open.spotify.com/track/...",
    }]})


class AlbumCreate(BaseModel):
    """Album (oder Playlist) anlegen – die Tracks müssen schon einzeln im Katalog stehen."""

    type: Literal["album", "playlist"] = "album"
    title: str = Field(min_length=1, max_length=255)
    artist: str | None = None
    genre: str | None = None
    release_year: int | None = Field(default=None, ge=1000, le=9999)
    description: str | None = None
    external_url: str | None = None
    track_ids: list[uuid.UUID] = Field(
        min_length=1, description="IDs der enthaltenen Tracks in Reihenfolge (siehe GET /music-items?type=track)"
    )

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "type": "album", "title": "A Night at the Opera", "artist": "Queen",
        "genre": "Rock", "release_year": 1975,
        "track_ids": ["<ID von Track 1>", "<ID von Track 2>"],
    }]})


class MusicItemUpdate(BaseModel):
    """Alle Felder optional – nur mitgeschickte Felder werden geändert."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    artist: str | None = None
    album_name: str | None = None
    genre: str | None = None
    release_year: int | None = Field(default=None, ge=1000, le=9999)
    duration_seconds: int | None = Field(default=None, ge=0)
    description: str | None = None
    external_url: str | None = None
    track_ids: list[uuid.UUID] | None = Field(
        default=None, description="Nur bei Album/Playlist: ersetzt die Trackliste"
    )


class MusicItemRead(ORM):
    id: uuid.UUID
    type: MusicItemType
    title: str
    artist: str | None
    album_name: str | None
    genre: str | None
    release_year: int | None
    duration_seconds: int | None
    description: str | None
    external_url: str | None


class MusicItemDetail(MusicItemRead):
    tracks: list[MusicItemRead] = Field(description="Bei Album/Playlist: enthaltene Tracks")


class CollectionAdd(BaseModel):
    """Item über die ID oder über den Titel angeben."""

    music_item_id: uuid.UUID | None = None
    title: str | None = Field(default=None, examples=["Bohemian Rhapsody"])

    model_config = ConfigDict(json_schema_extra={"examples": [{"title": "Bohemian Rhapsody"}]})

    @model_validator(mode="after")
    def _id_or_title(self):
        if self.music_item_id is None and not self.title:
            raise ValueError("Entweder 'music_item_id' oder 'title' angeben")
        return self


class CollectionMark(BaseModel):
    """Markierung ändern – nur mitgeschickte Felder werden geändert."""

    reaction: Reaction | None = Field(
        default=None, description="'like', 'dislike' oder null (= Reaktion entfernen)"
    )
    is_favourite: bool | None = None

    model_config = ConfigDict(json_schema_extra={"examples": [{"reaction": "like", "is_favourite": True}]})


class CollectionEntryRead(ORM):
    music_item: MusicItemRead
    reaction: Reaction | None
    is_favourite: bool
    added_at: datetime


class UserCollection(BaseModel):
    username: str
    items: list[CollectionEntryRead]


class CommentCreate(BaseModel):
    username: str = Field(examples=["anna"])
    text: str = Field(min_length=1, max_length=2000, examples=["Absoluter Klassiker!"])


class CommentRead(BaseModel):
    id: uuid.UUID
    username: str
    text: str
    created_at: datetime


class RatingSet(BaseModel):
    username: str = Field(examples=["anna"])
    stars: int = Field(ge=1, le=5, examples=[5])


class RatingSummary(BaseModel):
    music_item_id: uuid.UUID
    average: float | None = Field(description="Durchschnitt, null wenn noch keine Bewertung")
    count: int
    ratings: dict[str, int] = Field(description="Username -> Sterne")


# ===========================================================================
# 2. Hilfsfunktionen
# ===========================================================================
def get_user(db: Session, username: str) -> User:
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        raise HTTPException(404, f"User '{username}' nicht gefunden")
    return user


def get_item(db: Session, item_id: uuid.UUID) -> MusicItem:
    item = db.get(MusicItem, item_id)
    if item is None:
        raise HTTPException(404, "Music Item nicht gefunden")
    return item


def find_item_by_title(db: Session, title: str) -> MusicItem:
    items = db.scalars(select(MusicItem).where(func.lower(MusicItem.title) == title.lower())).all()
    if not items:
        raise HTTPException(404, f"Kein Music Item mit dem Titel '{title}' gefunden")
    if len(items) > 1:
        raise HTTPException(
            409,
            {
                "message": f"Mehrere Items heißen '{title}' – bitte 'music_item_id' angeben",
                "candidates": [
                    {"music_item_id": str(i.id), "type": i.type.value, "artist": i.artist} for i in items
                ],
            },
        )
    return items[0]


def get_caller(
        db: DB, x_username: Annotated[str, Header(description="Username des Aufrufers (ersetzt den Login)")]
) -> User:
    """Dependency: wer schickt die Anfrage? (Header X-Username)"""
    user = db.scalar(select(User).where(User.username == x_username))
    if user is None:
        raise HTTPException(401, f"Unbekannter Aufrufer '{x_username}'")
    return user


Caller = Annotated[User, Depends(get_caller)]


def require_admin(caller: Caller) -> User:
    """Dependency für Admin-Endpoints: Aufrufer muss die Rolle admin haben."""
    if caller.role != UserRole.admin:
        raise HTTPException(403, "Nur Admins dürfen den Katalog ändern")
    return caller


Admin = Annotated[User, Depends(require_admin)]


def require_owner_or_admin(caller: User, username: str) -> None:
    """User dürfen nur ihre eigene Sammlung ändern, Admins jede."""
    if caller.role != UserRole.admin and caller.username != username:
        raise HTTPException(403, "Du darfst nur deine eigene Sammlung ändern")


def set_tracks(db: Session, item: MusicItem, track_ids: list[uuid.UUID]) -> None:
    """Trackliste eines Albums / einer Playlist setzen."""
    if track_ids and item.type == MusicItemType.track:
        raise HTTPException(422, "'track_ids' gibt es nur bei Album und Playlist")
    if len(set(track_ids)) != len(track_ids):
        raise HTTPException(422, "Ein Track darf nur einmal vorkommen")
    links = []
    for position, track_id in enumerate(track_ids, start=1):
        track = db.get(MusicItem, track_id)
        if track is None:
            raise HTTPException(404, f"Track {track_id} existiert nicht – bitte zuerst einzeln anlegen")
        if track.type != MusicItemType.track:
            raise HTTPException(422, f"'{track.title}' ist kein einzelner Track")
        links.append(MusicItemTrack(track=track, position=position))
    item.track_links = links


def get_entry(db: Session, user: User, item_id: uuid.UUID) -> CollectionEntry:
    entry = db.scalar(
        select(CollectionEntry).where(
            CollectionEntry.user_id == user.id, CollectionEntry.music_item_id == item_id
        )
    )
    if entry is None:
        raise HTTPException(404, f"Item ist nicht in der Sammlung von {user.username}")
    return entry


# ===========================================================================
# 3a. Katalog – lesen: alle, ändern: nur Admin
# ===========================================================================
@app.get("/music-items", response_model=list[MusicItemRead], tags=["Katalog"],
         summary="Alle Music Items (optional suchen / filtern)")
def list_music_items(db: DB, search: str | None = None, type: MusicItemType | None = None):
    stmt = select(MusicItem).order_by(MusicItem.type, MusicItem.title)
    if search:
        stmt = stmt.where(or_(MusicItem.title.ilike(f"%{search}%"), MusicItem.artist.ilike(f"%{search}%")))
    if type:
        stmt = stmt.where(MusicItem.type == type)
    return db.scalars(stmt).all()


@app.get("/music-items/{item_id}", response_model=MusicItemDetail, tags=["Katalog"],
         summary="Ein Music Item (bei Album/Playlist inkl. Tracks)")
def get_music_item(item_id: uuid.UUID, db: DB):
    return get_item(db, item_id)


@app.post("/music-items/tracks", response_model=MusicItemDetail, status_code=201, tags=["Katalog"],
          summary="Einzelnen Song anlegen (Admin)")
def create_track(body: TrackCreate, db: DB, admin: Admin):
    item = MusicItem(type=MusicItemType.track, **body.model_dump(), created_by=admin)
    db.add(item)
    db.commit()
    return item


@app.post("/music-items/albums", response_model=MusicItemDetail, status_code=201, tags=["Katalog"],
          summary="Album oder Playlist anlegen (Admin)",
          description="Die Songs werden über ihre IDs referenziert und müssen vorher einzeln "
                      "über POST /music-items/tracks angelegt worden sein.")
def create_album(body: AlbumCreate, db: DB, admin: Admin):
    item = MusicItem(
        type=MusicItemType(body.type), created_by=admin,
        **body.model_dump(exclude={"type", "track_ids"}),
    )
    set_tracks(db, item, body.track_ids)
    db.add(item)
    db.commit()
    return item


@app.patch("/music-items/{item_id}", response_model=MusicItemDetail, tags=["Katalog"],
           summary="Music Item ändern (Admin)")
def update_music_item(item_id: uuid.UUID, body: MusicItemUpdate, db: DB, admin: Admin):
    item = get_item(db, item_id)
    changes = body.model_dump(exclude_unset=True)
    if "track_ids" in changes:
        set_tracks(db, item, changes.pop("track_ids") or [])
    for field, value in changes.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/music-items/{item_id}", status_code=204, tags=["Katalog"],
            summary="Music Item löschen (Admin) – auch aus allen Sammlungen")
def delete_music_item(item_id: uuid.UUID, db: DB, admin: Admin):
    db.delete(get_item(db, item_id))
    db.commit()
    return Response(status_code=204)


# ===========================================================================
# 3b. Persönliche Sammlung – User
# ===========================================================================
@app.get("/users/{username}/collection", response_model=list[CollectionEntryRead],
         tags=["Sammlung"], summary="Sammlung eines Users")
def get_collection(username: str, db: DB, only_favourites: bool = False):
    user = get_user(db, username)
    stmt = select(CollectionEntry).where(CollectionEntry.user_id == user.id)
    if only_favourites:
        stmt = stmt.where(CollectionEntry.is_favourite)
    return db.scalars(stmt.order_by(CollectionEntry.added_at.desc())).all()


@app.post("/users/{username}/collection", response_model=CollectionEntryRead, status_code=201,
          tags=["Sammlung"], summary="Item zur Sammlung hinzufügen (per ID oder Titel)",
          description="Nur Items, die schon im Katalog sind. Erlaubt: der User selbst oder ein Admin.")
def add_to_collection(username: str, body: CollectionAdd, db: DB, caller: Caller):
    require_owner_or_admin(caller, username)
    user = get_user(db, username)
    item = get_item(db, body.music_item_id) if body.music_item_id else find_item_by_title(db, body.title)
    if db.scalar(select(CollectionEntry.id).where(
            CollectionEntry.user_id == user.id, CollectionEntry.music_item_id == item.id
    )):
        raise HTTPException(409, f"'{item.title}' ist schon in der Sammlung von {username}")
    entry = CollectionEntry(user=user, music_item=item)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@app.patch("/users/{username}/collection/{item_id}", response_model=CollectionEntryRead,
           tags=["Sammlung"], summary="Als like / dislike / favourite markieren",
           description="Erlaubt: der User selbst oder ein Admin.")
def mark_collection_item(username: str, item_id: uuid.UUID, body: CollectionMark, db: DB, caller: Caller):
    require_owner_or_admin(caller, username)
    entry = get_entry(db, get_user(db, username), item_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    db.commit()
    return entry


@app.delete("/users/{username}/collection/{item_id}", status_code=204,
            tags=["Sammlung"], summary="Item aus der Sammlung entfernen",
            description="Erlaubt: der User selbst oder ein Admin (aus jeder Sammlung).")
def remove_from_collection(username: str, item_id: uuid.UUID, db: DB, caller: Caller):
    require_owner_or_admin(caller, username)
    db.delete(get_entry(db, get_user(db, username), item_id))
    db.commit()
    return Response(status_code=204)


# ===========================================================================
# 3c. Übersicht aller User
# ===========================================================================
@app.get("/collections", response_model=list[UserCollection], tags=["Übersicht"],
         summary="Sammlungen aller User")
def get_all_collections(db: DB):
    users = db.scalars(select(User).order_by(User.username)).all()
    return [UserCollection(username=u.username, items=u.collection) for u in users]


# ===========================================================================
# 3d. Kommentare und 5-Sterne-Bewertungen
# ===========================================================================
@app.get("/music-items/{item_id}/comments", response_model=list[CommentRead],
         tags=["Kommentare & Bewertungen"], summary="Kommentare zu einem Item")
def list_comments(item_id: uuid.UUID, db: DB):
    return [
        CommentRead(id=c.id, username=c.user.username, text=c.text, created_at=c.created_at)
        for c in get_item(db, item_id).comments
    ]


@app.post("/music-items/{item_id}/comments", response_model=CommentRead, status_code=201,
          tags=["Kommentare & Bewertungen"], summary="Kommentar schreiben")
def add_comment(item_id: uuid.UUID, body: CommentCreate, db: DB):
    item, user = get_item(db, item_id), get_user(db, body.username)
    comment = Comment(user=user, music_item=item, text=body.text)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return CommentRead(id=comment.id, username=user.username, text=comment.text, created_at=comment.created_at)


@app.get("/music-items/{item_id}/rating", response_model=RatingSummary,
         tags=["Kommentare & Bewertungen"], summary="Bewertungen eines Items (Durchschnitt)")
def get_rating(item_id: uuid.UUID, db: DB):
    item = get_item(db, item_id)
    stars = {r.user.username: r.stars for r in item.ratings}
    average = round(sum(stars.values()) / len(stars), 2) if stars else None
    return RatingSummary(music_item_id=item.id, average=average, count=len(stars), ratings=stars)


@app.put("/music-items/{item_id}/rating", response_model=RatingSummary,
         tags=["Kommentare & Bewertungen"], summary="1–5 Sterne vergeben (überschreibt eigene Bewertung)")
def set_rating(item_id: uuid.UUID, body: RatingSet, db: DB):
    item, user = get_item(db, item_id), get_user(db, body.username)
    rating = db.scalar(select(Rating).where(Rating.user_id == user.id, Rating.music_item_id == item.id))
    if rating:
        rating.stars = body.stars
    else:
        db.add(Rating(user=user, music_item=item, stars=body.stars))
    db.commit()
    db.expire(item, ["ratings"])
    return get_rating(item_id, db)


# ===========================================================================
# Technisch
# ===========================================================================
@app.get("/health/db", tags=["Health"], summary="Datenbankverbindung prüfen")
def health_db(db: DB) -> dict:
    try:
        version = db.execute(text("SELECT version()")).scalar_one()
        users = db.scalar(select(func.count()).select_from(User))
        items = db.scalar(select(func.count()).select_from(MusicItem))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(503, f"Datenbank nicht erreichbar: {exc}") from exc
    return {"status": "ok", "database": version, "users": users, "music_items": items}
