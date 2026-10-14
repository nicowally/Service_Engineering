# Music Collection Manager – Backend (FastAPI + Supabase)

KV Service Engineering WS 2026/27, Übung 1 – Topic 6: Python FastAPI.

## Technologie

| Bereich        | Technologie                                     |
|----------------|-------------------------------------------------|
| Web-Framework  | FastAPI (OpenAPI/Swagger automatisch unter `/docs`) |
| Datenbank      | PostgreSQL, gehostet auf Supabase               |
| ORM            | SQLAlchemy 2.0 (typisierte `Mapped[...]`-Modelle) |
| DB-Treiber     | psycopg 3                                       |
| Migrationen    | Alembic                                         |
| Konfiguration  | pydantic-settings (`.env`)                      |

## Projektstruktur

```
app/
  config.py        Einstellungen aus .env (DATABASE_URL …)
  database.py      Engine, Session, Base, get_db()-Dependency
  models.py        ORM-Datenmodell (alle Tabellen)
  main.py          FastAPI-App (vorerst nur /health/db)
migrations/        Alembic-Migrationen (0001_initial_schema.py)
scripts/
  check_db.py      Verbindungstest
  seed.py          Testdaten einfügen
schema.sql         Gleiches Schema als reines SQL (Alternative zu Alembic)
```

## Datenmodell

```
users ─────────────┬──< collection_entries >──┬───── music_items
 id, username,     │    reaction (like/dislike)│      id, type (track|album|playlist),
 email, role       │    is_favourite           │      title, artist, album_name, genre,
 (admin|user)      ├──< comments >─────────────┤      release_year, duration_seconds,
                   │    text                   │      description, external_url,
                   └──< ratings >──────────────┤      created_by_id → users
                        stars 1–5              │
                                               └──< music_item_tracks >── (track_id → music_items)
                                                    container_id, track_id, position
```

- **music_items** – ein Eintrag ist Track, Album oder Playlist. Es werden nur Metadaten gespeichert, `external_url` referenziert den eigentlichen Track (z. B. Spotify-Link).
- **music_item_tracks** – Alben/Playlists bestehen aus Tracks mit Position → Playlists beliebiger Länge, ein Track kann in vielen Playlists vorkommen.
- **collection_entries** – persönliche Sammlung; pro User und Item max. ein Eintrag (Unique-Constraint). Like/Dislike und Favorit sind getrennt, d. h. ein Item kann „like“ und Favorit zugleich sein.
- **ratings** – 1–5 Sterne (Check-Constraint), max. eine Bewertung pro User und Item.
- Löschen eines Items löscht automatisch Sammlungseinträge, Kommentare, Ratings und Playlist-Zuordnungen (`ON DELETE CASCADE`).

---

## Einrichtung (jedes Teammitglied einmal)

### 1. Voraussetzungen
- **Python 3.11 oder neuer** (`python --version`)
- **IntelliJ IDEA** mit dem **Python-Plugin** (*Settings → Plugins → Marketplace → „Python“*; in Ultimate heißt es „Python“, in Community „Python Community Edition“). Alternativ PyCharm.

### 2. Projekt öffnen und virtuelle Umgebung anlegen
1. Projektordner in IntelliJ öffnen (*File → Open*).
2. *File → Project Structure → SDKs → + → Add Python SDK → Virtualenv Environment → New*, Speicherort `.venv` im Projektordner, Basis-Interpreter Python 3.11+.
3. Unter *Project → SDK* diese neue SDK auswählen.
4. Im IntelliJ-Terminal (das nutzt dann automatisch die `.venv`):
   ```bash
   pip install -r requirements.txt
   ```

### 3. Supabase-Verbindungsdaten eintragen
1. Im Supabase-Dashboard oben auf **Connect** klicken → **Connection String** → Typ **URI** → **Session pooler** wählen.
   (Die „Direct connection“ funktioniert nur über IPv6 – in vielen Heim- und Uni-Netzen klappt das nicht, der Session Pooler läuft über IPv4.)
2. `.env.example` nach `.env` kopieren und `DATABASE_URL` durch diesen String ersetzen:
   - `postgresql://` → **`postgresql+psycopg://`** ändern
   - `[YOUR-PASSWORD]` durch das DB-Passwort ersetzen (Passwort vergessen? *Project Settings → Database → Reset database password*)
   - Sonderzeichen im Passwort URL-kodieren (`@`→`%40`, `#`→`%23`, `/`→`%2F`) oder einfach ein Passwort ohne Sonderzeichen setzen.
3. `.env` **nie** committen – steht bereits in `.gitignore`. Jeder im Team legt seine eigene an.

### 4. Verbindung testen
```bash
python -m scripts.check_db
```
Erwartet: `Verbunden mit: PostgreSQL 17…` und `Tabellen im Schema public: (noch keine)`.

### 5. Tabellen anlegen (nur **einmal** fürs ganze Team, die DB ist geteilt)
```bash
alembic upgrade head
python -m scripts.seed        # optional: Testdaten
```
Danach siehst du die Tabellen im Supabase-Dashboard unter **Table Editor**.

*Alternative ohne Alembic:* Inhalt von `schema.sql` im Supabase **SQL Editor** ausführen.

### 6. Server starten
```bash
uvicorn app.main:app --reload
```
- http://127.0.0.1:8000/health/db → Status der DB-Verbindung
- http://127.0.0.1:8000/docs → Swagger UI (OpenAPI, für die Präsentation)

**Run-Konfiguration in IntelliJ:** *Run → Edit Configurations → + → Python* → statt „Script path“ auf **Module name** umstellen: `uvicorn`, Parameters: `app.main:app --reload`, Working directory: Projektordner.

### 7. Datenbank in IntelliJ ansehen (nur IntelliJ **Ultimate**)
*View → Tool Windows → Database → + → Data Source → PostgreSQL*, Werte aus dem Supabase-„Connect“-Dialog (Session pooler):
- Host: `aws-…pooler.supabase.com`, Port `5432`, Database `postgres`
- User: `postgres.pjqnjwkofoaerjwbocsy`, Password: euer DB-Passwort
- Reiter *SSH/SSL* → **Use SSL** aktivieren, Mode `require`

In der Community Edition gibt es kein Database-Fenster – dann einfach den Table Editor im Supabase-Dashboard verwenden.

---

## Datenmodell ändern

1. Modell in `app/models.py` anpassen.
2. `alembic revision --autogenerate -m "kurze beschreibung"` – erzeugt eine neue Datei in `migrations/versions/`. Kurz durchlesen!
3. `alembic upgrade head` – wendet sie auf Supabase an.
4. Migrationsdatei committen, damit das Team denselben Stand hat.

Rückgängig machen: `alembic downgrade -1`.

## Hinweis zu Supabase-Sicherheit

Supabase stellt alle Tabellen im Schema `public` zusätzlich über eine eigene, öffentliche REST-API bereit. Die Migration aktiviert daher **Row Level Security** (ohne Policies) auf allen Tabellen: Diese öffentliche API kommt damit nicht an die Daten, unser Backend verbindet sich aber als Owner (`postgres`) und ist nicht eingeschränkt. Zugriffsrechte (Admin/User) setzen wir selbst im FastAPI-Backend um.
