import os
import unittest

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost/test")
os.environ["SQL_ECHO"] = "false"

from pydantic import ValidationError
from app.main import AlbumCreate, CollectionMark, MusicItemUpdate, TrackCreate


class ValidationTests(unittest.TestCase):
    def test_favourite_rejects_explicit_null_but_allows_false(self):
        with self.assertRaises(ValidationError):
            CollectionMark(is_favourite=None)
        self.assertFalse(CollectionMark(is_favourite=False).is_favourite)

    def test_reaction_can_be_removed_without_changing_favourite(self):
        value = CollectionMark(reaction=None)
        self.assertEqual(value.model_dump(exclude_unset=True), {"reaction": None})

    def test_database_string_limits_are_validated_before_sql(self):
        for model, data in [
            (TrackCreate, {"title": "Track", "artist": "x" * 256}),
            (TrackCreate, {"title": "Track", "album_name": "x" * 256}),
            (AlbumCreate, {"title": "Album", "track_ids": ["00000000-0000-0000-0000-000000000001"], "genre": "x" * 101}),
            (MusicItemUpdate, {"external_url": "x" * 1025}),
        ]:
            with self.subTest(model=model.__name__, data=list(data)):
                with self.assertRaises(ValidationError):
                    model(**data)


if __name__ == "__main__":
    unittest.main()
