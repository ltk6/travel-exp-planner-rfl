# N16 Web UI Module (Next.js)

N16 is the primary frontend for Travel Experience Planner. It is a Next.js 15 / React 19 web application built with the App Router, Tailwind CSS, and shadcn/ui. It communicates exclusively with the N18 FastAPI backend.

## Responsibilities

- Provide the main user-facing interface for travel planning
- Collect user input through a multi-step Wizard (questionnaire + free-text + image upload)
- Call N18 API endpoints and progressively render ranked results
- Lazy-load location images independently of the main data response
- Manage global session state (auth, results, activity lists) via Zustand
- Provide an Explore mode (`/explore`) to browse all available locations
- Provide a Profile page (`/profile`) for registration, login, and recommendation history
- Handle feedback loops: refine recommendations and activity lists via N18 feedback endpoints

## Tech Stack

| Layer            | Technology                             |
| ---------------- | -------------------------------------- |
| Framework        | Next.js 15 (App Router)                |
| UI Library       | React 19                               |
| Styling          | Tailwind CSS + shadcn/ui               |
| State management | Zustand (`src/store/planner-store.ts`) |
| Language         | TypeScript                             |
| Testing          | Vitest                                 |

---

## Getting Started

Install dependencies and start the development server:

```bash
npm install
npm run dev
```

The app runs at [http://127.0.0.1:3000](http://127.0.0.1:3000).

For a full-stack startup (backend + frontend together), use the project's Docker Compose stack from the root directory:

```bash
docker compose up -d
```

---

## Directory Structure

```
frontend/n16_web_ui/src/
├── app/
│   ├── (planner)/          # Main planner flow
│   │   ├── page.tsx        # Input Wizard (questionnaire + prompt + image upload)
│   │   └── results/        # Results page (ranked locations + activity drawers)
│   ├── explore/            # Explore Grid — browse all locations
│   ├── profile/            # Auth (register/login) + recommendation history
│   ├── feedback/           # Feedback page
│   ├── about/              # About page
│   └── api/                # Next.js API Routes (proxy / auth / images)
│       ├── activities/
│       ├── auth/
│       ├── feedback/
│       ├── images/
│       ├── locations/
│       ├── profile/
│       └── recommend/
├── components/
│   ├── app-shell/          # Layout shell and navigation
│   ├── auth/               # Login / register forms
│   ├── explore/            # Explore grid cards
│   ├── header/             # Top nav
│   ├── input/              # Wizard steps, tag chips, image uploader
│   ├── map/                # Map view component
│   ├── result/             # Location cards, activity drawers, feedback panels
│   └── ui/                 # shadcn/ui primitives
├── hooks/                  # Custom React hooks
├── lib/                    # API client functions, utility helpers
└── store/
    └── planner-store.ts    # Zustand store — global app state
```

---

## User Flows

### Planner Flow

| Action | Description |
| :--- | :--- |
| **1. Input** | User enters preferences and optional images via the Wizard Slider. |
| **2. Request** | App calls POST /recommend through the Next.js API proxy. |
| **3. Loading** | UI displays skeleton loaders during AI ranking. |
| **4. Results** | Browser lazy-loads images for ranked location cards. |
| **5. Activities** | User opens activity drawers for specific locations on-demand. |
| **6. Feedback** | User refines results via global or local feedback panels. |

### Auxiliary Flows

| Action | Description |
| :--- | :--- |
| **Explore** | Loads all locations as slim cards via GET /locations. |
| **Auth** | Handles user registration and login through standard endpoints. |
| **History** | Fetches and reloads past recommendation sessions for the user. |

---

## State Management

All cross-page state lives in the Zustand store at `src/store/planner-store.ts`:

| State key              | Purpose                                           |
| ---------------------- | ------------------------------------------------- |
| `payload`              | Captured recommendation payload                   |
| `results`              | Ranked location results from `/recommend`         |
| `activityResults`      | Per-location activity lists from `/activities` |
| `currentSessionId`     | Current history ID for saving updates             |

---

## API Communication

N16 communicates with N18 through **Next.js API Routes** (`src/app/api/`). These routes act as a proxy layer that:

- Attaches the `X-Internal-Key` header (kept server-side, never exposed to the browser)
- Forwards request bodies to the FastAPI backend
- Streams or returns JSON responses to the client

This keeps the internal API key out of client-side bundles.

Backend base URL is configured via `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
INTERNAL_API_KEY=your_secret_key
```

---

## Image Loading Strategy

N16 uses a pure lazy-loading model for location images:

1. `/recommend` returns only image URL strings: `/api/images/{location_id}_{idx}.jpg`
2. Next.js `<Image>` components use those URLs with `loading="lazy"`
3. Each image is fetched from the Next.js image proxy → N18 → PostgreSQL only when the card enters the viewport
4. Missing images return a 1×1 transparent PNG fallback — no broken image icons

This eliminates the need to wait for large image blobs before rendering the results page.

---

## Running Tests

```bash
npm run test
```

Tests use Vitest. Configuration is in `vitest.config.ts`.

---

## Runtime Notes

- `next.config.ts` configures image domains and any rewrites needed for the backend proxy
- `components.json` holds shadcn/ui component configuration
- Husky pre-commit hooks run Prettier formatting checks (`.husky/`)
- Service worker registered via `src/app/sw.ts` for offline/caching support
- `CLAUDE.md` and `AGENTS.md` contain brief notes for AI coding assistants working in this repo
