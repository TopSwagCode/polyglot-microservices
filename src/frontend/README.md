## Polyglot Microservices Frontend

This SvelteKit (v5) application is a minimalistic dark UI for exercising the polyglot microservices in this repository:

* API Gateway (.NET / YARP – planned)
* Auth Service (.NET)
* Task Service (Go)
* Analytics Service (Python / FastAPI)

Currently the UI uses mocked data (no real network calls yet) so you can iterate on UX without backends running. Replace mocks with real gateway endpoints under `src/lib/api.ts` as services come online.

### Tech & Styling
* SvelteKit + Vite
* Dark theme with custom design tokens in `src/app.css`
* Basic responsive navigation component `src/lib/components/Navbar.svelte`
* Local auth store with fake login (`src/lib/stores/auth.ts`)

### Key Routes
| Route | Purpose |
|-------|---------|
| `/` | Public marketing style landing page (redirects to `/dashboard` if logged in) |
| `/login` | Demo login (accepts any credentials) |
| `/dashboard` | Lists mock projects with open/completed task counts |
| `/projects/[id]` | Shows mock task list; toggle completion & add new tasks locally |
| `/analytics` | Displays mocked metrics summary cards |

### Environment Configuration
Copy `.env.example` to `.env` and adjust values:

```
cp .env.example .env
```

Key variable:
* `VITE_API_BASE` – API Gateway base URL (reverse proxy). Example: `http://localhost:8080`
If not set, a fallback `http://localhost:8080` is used with a console warning in dev.

### Navbar Behavior
Navigation links adapt to authentication state:
* Logged OUT: `Login`, `Register`
* Logged IN: `Dashboard`, `Analytics`, `Dev Tools`, Username, `Logout`

`Dev Tools` points to `/devtools` which documents local database/message queue UIs.

### Developing
Install dependencies then start the dev server:

```sh
cd frontend
npm install
npm run dev
```

Environment variable `VITE_API_BASE` can be set to point to the API gateway once implemented. (Defaults to `http://localhost:8080`).

```sh
VITE_API_BASE=http://localhost:8080 npm run dev
```

### Building / Preview
```sh
npm run build
npm run preview
```

### Replacing Mocks with Real APIs
The UI is now wired to real endpoints when available:

| Feature | Endpoint (via gateway) | Code reference |
|---------|------------------------|----------------|
| Login | `POST /auth/login` | `src/lib/stores/auth.ts` |
| Current user | `GET /auth/me` | `auth.store` after login |
| Projects list | `GET /projects` | `dashboard/+page.svelte` |
| Create project | `POST /projects` | `dashboard/+page.svelte` (optimistic) |
| Tasks by project | `GET /tasks?project_id=...` or `GET /projects/{id}` | `projects/[id]/+page.svelte` |
| Create task | `POST /tasks` | `projects/[id]/+page.svelte` |
| Toggle status | `PUT /tasks/{id}` | `projects/[id]/+page.svelte` |
| Analytics dashboard | `GET /analytics/dashboard` | `analytics/+page.svelte` |
| Task summary | `GET /analytics/tasks/summary` | `analytics/+page.svelte` |
| Productivity | `GET /analytics/productivity` | `analytics/+page.svelte` |

Steps if running locally:
1. Start all backend services + API gateway (ensure it listens on port 8080 or set `VITE_API_BASE`).
2. Register a user (`/auth/register`) or use an existing user.
3. Login through `/login` in the UI (token persisted in localStorage).
4. Create a project via API (UI create-project flow not yet added) then view it in the dashboard.

To customize base URL: `VITE_API_BASE=http://localhost:8080 npm run dev`.

### Project Creation UI
On the dashboard you can create a project inline:
1. Enter a name.
2. Submit — a provisional project appears immediately (optimistic update) and is replaced when the server responds.
3. On failure it rolls back and shows an error message.

### Analytics Page Details
The analytics page now performs 3 parallel requests when you open or refresh it:
* `GET /analytics/dashboard` – high level totals & recent activity
* `GET /analytics/tasks/summary` – task completion distribution & recent completions
* `GET /analytics/productivity` – daily completions, weekly summary, recommendations

Displayed sections:
* KPI cards (Total Tasks, Completed Tasks, Active Projects, Productivity Score)
* Recent Activity event table
* Recent Completions list
* Daily Completions mini-grid + most productive day
* Recommendations list

A refresh button re-runs all requests concurrently. Failures surface a red error card without crashing the page.

### Auth Store Details
The local auth store (`src/lib/stores/auth.ts`) now attempts a real backend login first (`POST /auth/login`). If the request fails (service down or not yet implemented) it transparently falls back to a mock session so the rest of the UI remains usable. A token and user object are persisted in `localStorage` under `auth_token` and `auth_user`.

Available functions:
* `auth.login(username, password)` – real or mock login
* `auth.logout()` – clears session
* `auth.loadUser()` – fetches current user from `/auth/me` if a token exists

If you later enable strict mode (no mocks) remove the fallback branch in `login()`.

### API Client
The file `src/lib/api.ts` exports a singleton `apiClient` with helper methods: `get, post, put, patch, delete`. Usage example:

```ts
import { apiClient } from '$lib/api';
const projects = await apiClient.get('/projects', { auth: true });
```
Pass `{ auth: true }` to automatically attach the `Authorization` header if a token is present in the auth store or localStorage. Configure base URL via `VITE_API_BASE` (defaults to `http://localhost:8080`).

### Reactive Stores Note
When accessing the auth store inside Svelte components, prefer `$auth.token` / `$auth.user` for reactivity instead of reading properties directly off the `auth` object. Direct (`auth.token`) access will not trigger updates and can cause stale or unauthenticated states in UI logic.

### Markdown Pages (mdsvex)
The project is configured with `mdsvex` to allow `.md`, `.svx`, and `.mdx` files as routable Svelte pages.

Key points:
* Global markdown layout: `src/lib/components/MarkdownLayout.svelte` (applies typography & frontmatter title)
* Add a `+page.md` inside any route directory to create a content-driven page.
* Frontmatter `title:` is surfaced automatically as the page heading.

Example frontmatter:
```md
---
title: Developer Tools
---
# Content
...
```

Developer tools page lives at `/devtools` via `src/routes/devtools/+page.md`.

### Next Ideas
* Connect real WebSocket or SSE stream for live analytics.
* Add optimistic UI updates for task create/complete.
* Add toast notifications component.
* Integrate OpenTelemetry trace ID display per request.

---
Enjoy exploring the platform! PRs/feedback welcome.
