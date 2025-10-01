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

### Developing
Install dependencies then start the dev server:

```sh
cd frontend
npm install
npm run dev
```

Environment variable `VITE_API_BASE` can be set to point to the API gateway once implemented. (Defaults to `http://localhost:5089`).

```sh
VITE_API_BASE=http://localhost:5089 npm run dev
```

### Building / Preview
```sh
npm run build
npm run preview
```

### Replacing Mocks with Real APIs
1. Implement gateway routes for auth, tasks, analytics.
2. Update `src/lib/api.ts` if base path changes.
3. Swap mock `setTimeout` + hard-coded arrays with `apiClient.get('/tasks/projects')` etc.
4. Extend the auth store `login()` to post to real auth endpoint and store JWT.

### Next Ideas
* Connect real WebSocket or SSE stream for live analytics.
* Add optimistic UI updates for task create/complete.
* Add toast notifications component.
* Integrate OpenTelemetry trace ID display per request.

---
Enjoy exploring the platform! PRs/feedback welcome.
