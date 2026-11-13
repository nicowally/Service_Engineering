# Side A - Music Collection Manager frontend

Exercise 2 frontend using Svelte 5, SvelteKit 3, HTML, CSS and plain JavaScript. No TypeScript is required. FastAPI remains the backend.

## Run locally

Requirements: Node.js 24 LTS and npm. From this folder:

```bash
npm install
npm run dev
```

Open the Local URL printed by Vite (normally http://localhost:5173). Sample mode is on by default: no Python server, Supabase account or database is needed. Stop the server with Ctrl+C.

## What is implemented

- Catalog search by title/artist/album, type filters and title/year sorting.
- Detail pages with metadata and ordered album/playlist tracklists.
- User selector for admin, anna and ben in sample mode.
- Personal collections, add/remove, favourites and like/dislike.
- Browser-local sample persistence, responsive styling, loading/empty/error states.
- Separate service layer for the existing FastAPI endpoints.
- Client-rendered SPA with real URL routes and a static build.

This is the first frontend increment. Admin editing, comments, ratings and the all-users overview UI are still to be built. Real API integration needs validation against PostgreSQL once access is available.

## Structure and learning guide

```text
src/routes/+layout.svelte          Shared header, user selector, initial loading
src/routes/+layout.js              Disables SSR for the SPA
src/routes/+page.svelte            Home/catalog
src/routes/catalog/+page.svelte    Catalog route
src/routes/collection/+page.svelte  Personal collection route
src/routes/music/[id]/+page.svelte  Music detail and tracklist
src/lib/components/                Reusable .svelte components
src/lib/state/library.svelte.js    Shared reactive state and collection actions
src/lib/services/api.js            Request helper and FastAPI methods
src/lib/services/demo.js           Sample items and browser-local collection storage
src/app.css                       Shared responsive styles
vite.config.js                    SPA adapter and local API proxy
```

A `.svelte` component combines JavaScript (`<script>`), HTML markup and optional CSS (`<style>`). `$state` makes data reactive, `$derived` calculates values such as filtered lists, and `$props` accepts component inputs. The root layout uses `onMount` to initialize the library. Services keep requests separate from rendering. Shared state lives in a `.svelte.js` module, which allows Svelte runes in JavaScript.

The album-cover illustrations are original CSS artwork, not official album covers. There is no audio player or streaming integration.

## Connect to FastAPI later

1. Copy `.env.example` to `.env` in this frontend folder.
2. Set `VITE_USE_DEMO_DATA=false`.
3. Run the configured FastAPI backend on port 8000 in a separate terminal.
4. Restart Vite after changing environment variables.

During development and preview, `/api` is proxied to `http://127.0.0.1:8000` and the `/api` prefix is removed. This avoids cross-origin browser requests. User IDs come from `/users`; collection writes send the existing `X-Username` header. The user selector simulates identity; it is not authentication.

Only public frontend configuration belongs in `.env`. Never put `DATABASE_URL`, database passwords or Supabase service keys in frontend files. Sample IDs and collections are separate from the database and are not uploaded when switching modes.

For a separately hosted production frontend, configure an equivalent `/api` reverse proxy or set `VITE_API_BASE_URL` to the backend URL and configure FastAPI CORS. The local Vite proxy does not ship in the static build.

## Checks and production build

```bash
npm run check
npm test
npm run build
npm run preview
```

The production output is `build/`. A static host must serve `index.html` for unknown frontend paths so direct links such as `/music/bohemian-rhapsody` work. `npm run preview` handles the SPA fallback locally.

To reset sample collection changes, clear this site's browser storage. The `side-a-demo-collections-v1` key stores collections, and `side-a-selected-user` stores the selected user. Storage failure falls back to memory for the current tab.

Official guides: [Svelte tutorial](https://svelte.dev/tutorial/svelte/welcome-to-svelte), [Svelte runes](https://svelte.dev/docs/svelte/what-are-runes), [SvelteKit SPA](https://svelte.dev/docs/kit/single-page-apps).
