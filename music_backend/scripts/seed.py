"""Befüllt die Datenbank mit Testdaten.  Aufruf:  python -m scripts.seed

Das Skript ist idempotent: existieren bereits User, wird nichts eingefügt.
"""

from sqlalchemy import func, select

from app.database import SessionLocal
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


def main() -> None:
    with SessionLocal() as db:
        if db.scalar(select(func.count()).select_from(User)):
            print("Datenbank enthält bereits Daten – Seed übersprungen.")
            return

        admin = User(username="admin", email="admin@example.com", role=UserRole.admin)
        anna = User(username="anna", email="anna@example.com", role=UserRole.user)
        ben = User(username="ben", email="ben@example.com", role=UserRole.user)
        db.add_all([admin, anna, ben])

        t1 = MusicItem(type=MusicItemType.track, title="Bohemian Rhapsody", artist="Queen",
                       album_name="A Night at the Opera", genre="Rock", release_year=1975,
                       duration_seconds=354, created_by=admin)
        t2 = MusicItem(type=MusicItemType.track, title="Love of My Life", artist="Queen",
                       album_name="A Night at the Opera", genre="Rock", release_year=1975,
                       duration_seconds=219, created_by=admin)
        t3 = MusicItem(type=MusicItemType.track, title="Blinding Lights", artist="The Weeknd",
                       genre="Synth-Pop", release_year=2019, duration_seconds=200, created_by=anna)
        t4 = MusicItem(type=MusicItemType.track, title="Levitating", artist="Dua Lipa",
                       genre="Pop", release_year=2020, duration_seconds=203, created_by=ben)

        album = MusicItem(type=MusicItemType.album, title="A Night at the Opera", artist="Queen",
                          genre="Rock", release_year=1975, created_by=admin)
        album.track_links = [
            MusicItemTrack(track=t1, position=1),
            MusicItemTrack(track=t2, position=2),
        ]

        playlist = MusicItem(type=MusicItemType.playlist, title="Annas Lernmusik",
                             description="Zum Konzentrieren", created_by=anna)
        playlist.track_links = [
            MusicItemTrack(track=t3, position=1),
            MusicItemTrack(track=t1, position=2),
            MusicItemTrack(track=t4, position=3),
        ]
        db.add_all([t1, t2, t3, t4, album, playlist])

        db.add_all([
            CollectionEntry(user=anna, music_item=playlist, is_favourite=True),
            CollectionEntry(user=anna, music_item=t3, reaction=Reaction.like),
            CollectionEntry(user=anna, music_item=album, reaction=Reaction.like, is_favourite=True),
            CollectionEntry(user=ben, music_item=t4, reaction=Reaction.like),
            CollectionEntry(user=ben, music_item=t3, reaction=Reaction.dislike),
            Comment(user=anna, music_item=album, text="Absoluter Klassiker!"),
            Comment(user=ben, music_item=album, text="Das Gitarrensolo in Bohemian Rhapsody 🔥"),
            Rating(user=anna, music_item=album, stars=5),
            Rating(user=ben, music_item=album, stars=4),
            Rating(user=ben, music_item=t3, stars=2),
        ])
        db.commit()
        print("Testdaten eingefügt: 3 User, 6 Music-Items, 5 Sammlungseinträge, 2 Kommentare, 3 Ratings.")


if __name__ == "__main__":
    main()
