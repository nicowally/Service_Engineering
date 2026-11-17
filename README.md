# Music Collection Manager

Python FastAPI backend and a Svelte frontend for managing a personal music collection.

## Run both locally

Keep two terminals running, starting from this repository folder.

**Backend (terminal 1):**

```bash
cd music_backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload
```

For the initial setup, create `.venv` with Python 3.11 or newer, install `requirements.txt`, and configure `music_backend/.env` using `.env.example`. Select `music_backend/.venv/bin/python` as the interpreter in your IDE. See [backend setup](music_backend/README.md).

**Frontend (terminal 2):**

```bash
cd music_frontend
npm install
npm run dev
```

For real backend data, create `music_frontend/.env` with:

```dotenv
VITE_USE_DEMO_DATA=false
VITE_API_BASE_URL=/api
```

Open the frontend URL printed by Vite (normally http://localhost:5173). Vite forwards `/api` requests to FastAPI at `127.0.0.1:8000`. FastAPI reads and writes PostgreSQL on Supabase; the frontend never receives database credentials. Swagger is available at http://127.0.0.1:8000/docs.

Both real `.env` files and the Python environment are ignored by Git. Only the placeholder `.env.example` files are shared. Set `VITE_USE_DEMO_DATA=true` and restart Vite to use browser-local sample data instead. Browser sample collections are not uploaded to the database.

See the [frontend guide](music_frontend/README.md) for code structure and checks.
