-- Alternative zu Alembic: diesen Inhalt im Supabase SQL Editor ausführen.
-- Generiert mit: alembic upgrade head --sql
BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 71ed65467578

CREATE TYPE user_role AS ENUM ('admin', 'user');

CREATE TABLE users (
    id UUID NOT NULL, 
    username VARCHAR(50) NOT NULL, 
    email VARCHAR(255) NOT NULL, 
    role user_role NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (email), 
    UNIQUE (username)
);

CREATE TYPE music_item_type AS ENUM ('track', 'album', 'playlist');

CREATE TABLE music_items (
    id UUID NOT NULL, 
    type music_item_type NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    artist VARCHAR(255), 
    album_name VARCHAR(255), 
    genre VARCHAR(100), 
    release_year SMALLINT, 
    duration_seconds INTEGER, 
    description TEXT, 
    external_url VARCHAR(1024), 
    created_by_id UUID, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_music_items_duration CHECK (duration_seconds IS NULL OR duration_seconds >= 0), 
    CONSTRAINT ck_music_items_year CHECK (release_year IS NULL OR release_year BETWEEN 1000 AND 9999), 
    FOREIGN KEY(created_by_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_music_items_artist ON music_items (artist);

CREATE INDEX ix_music_items_created_by_id ON music_items (created_by_id);

CREATE INDEX ix_music_items_title ON music_items (title);

CREATE INDEX ix_music_items_type ON music_items (type);

CREATE TYPE reaction AS ENUM ('like', 'dislike');

CREATE TABLE collection_entries (
    id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    music_item_id UUID NOT NULL, 
    reaction reaction, 
    is_favourite BOOLEAN DEFAULT 'false' NOT NULL, 
    added_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(music_item_id) REFERENCES music_items (id) ON DELETE CASCADE, 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
    CONSTRAINT uq_collection_user_item UNIQUE (user_id, music_item_id)
);

CREATE INDEX ix_collection_entries_music_item_id ON collection_entries (music_item_id);

CREATE INDEX ix_collection_entries_user_id ON collection_entries (user_id);

CREATE TABLE comments (
    id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    music_item_id UUID NOT NULL, 
    text TEXT NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(music_item_id) REFERENCES music_items (id) ON DELETE CASCADE, 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_comments_music_item_id ON comments (music_item_id);

CREATE INDEX ix_comments_user_id ON comments (user_id);

CREATE TABLE music_item_tracks (
    id SERIAL NOT NULL, 
    container_id UUID NOT NULL, 
    track_id UUID NOT NULL, 
    position INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_music_item_tracks_not_self CHECK (container_id <> track_id), 
    CONSTRAINT ck_music_item_tracks_position CHECK (position >= 1), 
    FOREIGN KEY(container_id) REFERENCES music_items (id) ON DELETE CASCADE, 
    FOREIGN KEY(track_id) REFERENCES music_items (id) ON DELETE CASCADE, 
    CONSTRAINT uq_music_item_tracks_position UNIQUE (container_id, position)
);

CREATE INDEX ix_music_item_tracks_container_id ON music_item_tracks (container_id);

CREATE INDEX ix_music_item_tracks_track_id ON music_item_tracks (track_id);

CREATE TABLE ratings (
    id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    music_item_id UUID NOT NULL, 
    stars SMALLINT NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT ck_rating_stars CHECK (stars BETWEEN 1 AND 5), 
    FOREIGN KEY(music_item_id) REFERENCES music_items (id) ON DELETE CASCADE, 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
    CONSTRAINT uq_rating_user_item UNIQUE (user_id, music_item_id)
);

CREATE INDEX ix_ratings_music_item_id ON ratings (music_item_id);

CREATE INDEX ix_ratings_user_id ON ratings (user_id);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

ALTER TABLE music_items ENABLE ROW LEVEL SECURITY;

ALTER TABLE music_item_tracks ENABLE ROW LEVEL SECURITY;

ALTER TABLE collection_entries ENABLE ROW LEVEL SECURITY;

ALTER TABLE comments ENABLE ROW LEVEL SECURITY;

ALTER TABLE ratings ENABLE ROW LEVEL SECURITY;

INSERT INTO alembic_version (version_num) VALUES ('71ed65467578') RETURNING alembic_version.version_num;

COMMIT;

