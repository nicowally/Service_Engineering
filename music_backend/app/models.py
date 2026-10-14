"""
ORM-Datenmodell der Music Collection (SQLAlchemy 2.0, typisierte Mappings).

Übersicht:
  users                – Benutzer mit Rolle (admin / user). Login & User-Management
                         sind nicht Teil von Übung 1, die Tabelle wird aber für
                         Besitz, Kommentare und Bewertungen benötigt.
  music_items          – Ein Musik-Eintrag: einzelner Track, Album oder Playlist.
                         Es werden nur Metadaten gespeichert; der eigentliche Track
                         wird über external_url referenziert (z. B. Spotify-Link).
  music_item_tracks    – Zuordnung Album/Playlist -> enthaltene Tracks (mit Position).
                         Dadurch kann eine Playlist beliebig lang sein.
  collection_entries   – Persönliche Sammlung: welcher User hat welches Item,
                         inkl. Reaktion (like/dislike) und Favorit-Markierung.
  comments             – Kommentare von Usern zu einem Item.
  ratings              – 1–5-Sterne-Bewertung, max. eine pro User und Item.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class MusicItemType(str, enum.Enum):
    track = "track"
    album = "album"
    playlist = "playlist"


class Reaction(str, enum.Enum):
    like = "like"
    dislike = "dislike"


def _pg_enum(enum_cls: type[enum.Enum], name: str) -> Enum:
    """Postgres-ENUM, das die *Werte* (nicht die Python-Namen) speichert."""
    return Enum(enum_cls, name=name, values_callable=lambda e: [m.value for m in e])


# ---------------------------------------------------------------------------
# Mixins
# ---------------------------------------------------------------------------
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


# ---------------------------------------------------------------------------
# Tabellen
# ---------------------------------------------------------------------------
class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        _pg_enum(UserRole, "user_role"), default=UserRole.user, nullable=False
    )

    collection: Mapped[list["CollectionEntry"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    ratings: Mapped[list["Rating"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    created_items: Mapped[list["MusicItem"]] = relationship(back_populates="created_by")

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role.value})>"


class MusicItem(TimestampMixin, Base):
    __tablename__ = "music_items"
    __table_args__ = (
        CheckConstraint("duration_seconds IS NULL OR duration_seconds >= 0", name="ck_music_items_duration"),
        CheckConstraint(
            "release_year IS NULL OR release_year BETWEEN 1000 AND 9999", name="ck_music_items_year"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[MusicItemType] = mapped_column(
        _pg_enum(MusicItemType, "music_item_type"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    artist: Mapped[str | None] = mapped_column(String(255), index=True)  # bei Playlists optional
    album_name: Mapped[str | None] = mapped_column(String(255))  # für einzelne Tracks
    genre: Mapped[str | None] = mapped_column(String(100))
    release_year: Mapped[int | None] = mapped_column(SmallInteger)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    # Referenz auf den eigentlichen Track/das Album (Spotify-, YouTube-, Deezer-Link, ISRC …)
    external_url: Mapped[str | None] = mapped_column(String(1024))

    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    created_by: Mapped[User | None] = relationship(back_populates="created_items")

    # Für Alben/Playlists: enthaltene Tracks in Reihenfolge
    track_links: Mapped[list["MusicItemTrack"]] = relationship(
        foreign_keys="MusicItemTrack.container_id",
        back_populates="container",
        cascade="all, delete-orphan",
        order_by="MusicItemTrack.position",
    )
    collection_entries: Mapped[list["CollectionEntry"]] = relationship(
        back_populates="music_item", cascade="all, delete-orphan"
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="music_item", cascade="all, delete-orphan", order_by="Comment.created_at"
    )
    ratings: Mapped[list["Rating"]] = relationship(
        back_populates="music_item", cascade="all, delete-orphan"
    )

    @property
    def tracks(self) -> list["MusicItem"]:
        return [link.track for link in self.track_links]

    def __repr__(self) -> str:
        return f"<MusicItem {self.type.value}: {self.title}>"


class MusicItemTrack(Base):
    """Verknüpfungstabelle: Album/Playlist (container) enthält Track an Position."""

    __tablename__ = "music_item_tracks"
    __table_args__ = (
        UniqueConstraint("container_id", "position", name="uq_music_item_tracks_position"),
        CheckConstraint("container_id <> track_id", name="ck_music_item_tracks_not_self"),
        CheckConstraint("position >= 1", name="ck_music_item_tracks_position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    container_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("music_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    track_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("music_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    container: Mapped[MusicItem] = relationship(
        foreign_keys=[container_id], back_populates="track_links"
    )
    track: Mapped[MusicItem] = relationship(foreign_keys=[track_id])


class CollectionEntry(Base):
    """Ein Item in der persönlichen Sammlung eines Users."""

    __tablename__ = "collection_entries"
    __table_args__ = (
        UniqueConstraint("user_id", "music_item_id", name="uq_collection_user_item"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    music_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("music_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reaction: Mapped[Reaction | None] = mapped_column(_pg_enum(Reaction, "reaction"))
    is_favourite: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="collection")
    music_item: Mapped[MusicItem] = relationship(back_populates="collection_entries")


class Comment(TimestampMixin, Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    music_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("music_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped[User] = relationship(back_populates="comments")
    music_item: Mapped[MusicItem] = relationship(back_populates="comments")


class Rating(TimestampMixin, Base):
    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("user_id", "music_item_id", name="uq_rating_user_item"),
        CheckConstraint("stars BETWEEN 1 AND 5", name="ck_rating_stars"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    music_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("music_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    stars: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    user: Mapped[User] = relationship(back_populates="ratings")
    music_item: Mapped[MusicItem] = relationship(back_populates="ratings")
