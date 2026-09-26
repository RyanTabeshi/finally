# FinAlly — AI Trading Workstation

## Project Specification

## 1. Vision

FinAlly (Finance Ally) is a visually stunning AI-powered trading workstation that streams live market data, lets users trade a simulated portfolio, and integrates an LLM chat assistant that can analyze positions and execute trades on the user's behalf. It looks and feels like a modern Bloomberg terminal with an AI copilot.

This is the capstone project for an agentic AI coding course. It is built entirely by Coding Agents demonstrating how orchestrated AI agents can produce a production-quality full-stack application. Agents interact through files in `planning/`.

## 2. User Experience

### First Launch

The user runs a single Docker command (or a provided start script). A browser opens to `http://localhost:8000`. No login, no signup. They immediately see:

- A watchlist of 10 default tickers with live-updating prices in a grid
- $10,000 in virtual cash
- A dark, data-rich trading terminal aesthetic
- An AI chat panel ready to assist

### What the User Can Do

- **Watch prices stream** — prices flash green (uptick) or red (downtick) with subtle CSS animations that fade
- **View sparkline mini-charts** — price action beside each ticker in the watchlist, seeded on page load from recent server-side price history (~2.5 minutes) and extended live from the SSE stream
- **Click a ticker** to see a larger detailed chart in the main chart area
- **Buy and sell shares** — market orders only, instant fill at current price, no fees, no confirmation dialog
- **Monitor their portfolio** — a heatmap (treemap) showing positions sized by weight and colored by P&L, plus a P&L chart tracking total portfolio value over time
- **View a positions table** — ticker, quantity, average cost, current price, unrealized P&L, % change
- **Chat with the AI assistant** — ask about their portfolio, get analysis, and have the AI execute trades and manage the watchlist through natural language
- **Manage the watchlist** — add/remove tickers manually or via the AI chat

### Visual Design

- **Dark theme**: backgrounds around `#0d1117` or `#1a1a2e`, muted gray borders, no pure black
- **Price flash animations**: brief green/red background highlight when the price changes at display precision (2 decimals), fading over ~500ms via CSS transitions. Unchanged displayed prices do not flash, so the grid does not strobe.
- **Connection status indicator**: a small colored dot (green = connected, yellow = reconnecting, red = disconnected) visible in the header
- **Professional, data-dense layout**: inspired by Bloomberg/trading terminals — every pixel earns its place
- **Responsive but desktop-first**: optimized for wide screens, functional on tablet

### Color Scheme
- Accent Yellow: `#ecad0a`
- Blue Primary: `#209dd7`
- Purple Secondary: `#753991` (submit buttons)

## 3. Architecture Overview

### Single Container, Single Port

```
┌─────────────────────────────────────────────────┐
│  Docker Container (port 8000)                   │
│                                                 │
│  FastAPI (Python/uv)                            │
│  ├── /api/*          REST endpoints             │
│  ├── /api/stream/*   SSE streaming              │
│  └── /*              Static file serving         │
│                      (Next.js export)            │
│                                                 │
│  SQLite database (bind-mounted from ./db)       │
│  Background task: market data polling/sim        │
└─────────────────────────────────────────────────┘
```

- **Frontend**: Next.js with TypeScript, built as a static export (`output: 'export'`), served by FastAPI as static files
- **Backend**: FastAPI (Python), managed as a `uv` project
- **Database**: SQLite, single file at `db/finally.db`, bind-mounted from the host `db/` directory for persistence
- **Real-time data**: Server-Sent Events (SSE) — simpler than WebSockets, one-way server→client push, works everywhere
- **AI integration**: LiteLLM → OpenRouter (Cerebras for fast inference), with structured outputs for trade execution
- **Market data**: Environment-variable driven — simulator by default, real data via Massive API if key provided

### Why These Choices

| Decision | Rationale |
|---|---|
| SSE over WebSockets | One-way push is all we need; simpler, no bidirectional complexity, universal browser support |
| Static Next.js export | Single origin, no CORS issues, one port, one container, simple deployment |
| SQLite over Postgres | No auth = no multi-user = no need for a database server; self-contained, zero config |
| Single Docker container | Students run one command; no docker-compose for production, no service orchestration |
| uv for Python | Fast, modern Python project management; reproducible lockfile; what students should learn |
| Market orders only | Eliminates order book, limit order logic, partial fills — dramatically simpler portfolio math |

---

## 4. Directory Structure

```
finally/
├── frontend/                 # Next.js TypeScript project (static export)
├── backend/                  # FastAPI uv project (Python)
│   └── db/                   # Schema definitions, seed data, migration logic
├── planning/                 # Project-wide documentation for agents
│   ├── PLAN.md               # This document
│   └── ...                   # Additional agent reference docs
├── scripts/
│   ├── start_mac.sh          # Launch Docker container (macOS/Linux)
│   ├── stop_mac.sh           # Stop Docker container (macOS/Linux)
│   ├── start_windows.ps1     # Launch Docker container (Windows PowerShell)
│   └── stop_windows.ps1      # Stop Docker container (Windows PowerShell)
├── test/                     # Playwright E2E tests (optional docker-compose.test.yml)
├── db/                       # Bind-mount target (SQLite file lives here at runtime)
│   └── .gitkeep              # Directory exists in repo; finally.db is gitignored
├── Dockerfile                # Multi-stage build (Node → Python)
├── docker-compose.yml        # Optional convenience wrapper
├── .env                      # Environment variables (gitignored, .env.example committed)
└── .gitignore
```

### Key Boundaries

- **`frontend/`** is a self-contained Next.js project. It knows nothing about Python. It talks to the backend via `/api/*` endpoints and `/api/stream/*` SSE endpoints. Internal structure is up to the Frontend Engineer agent.
- **`backend/`** is a self-contained uv project with its own `pyproject.toml`. It owns all server logic including database initialization, schema, seed data, API routes, SSE streaming, market data, and LLM integration. Internal structure is up to the Backend/Market Data agents.
- **`backend/db/`** contains schema SQL definitions and seed logic. The backend initializes the database at startup — creating tables and seeding default data if the SQLite file doesn't exist or is empty.
- **`db/`** at the top level is bind-mounted to `/app/db` in the container. The SQLite file (`db/finally.db`) is created here by the backend, is visible on the host, and persists across container restarts.
- **`planning/`** contains project-wide documentation, including this plan. All agents reference files here as the shared contract.
- **`test/`** contains Playwright E2E tests, run from the host against the running container (an optional `docker-compose.test.yml` may be added for CI). Unit tests live within `frontend/` and `backend/` respectively, following each framework's conventions.
- **`scripts/`** contains start/stop scripts that wrap Docker commands.

---

## 5. Environment Variables

```bash
# Required: OpenRouter API key for LLM chat functionality
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Optional: Massive (Polygon.io) API key for real market data
# If not set, the built-in market simulator is used (recommended for most users)
MASSIVE_API_KEY=

# Optional: Massive poll interval in seconds (free tier needs 15; paid tiers can go to 2)
MASSIVE_POLL_SECONDS=15

# Optional: Set to "true" for deterministic mock LLM responses (testing)
LLM_MOCK=false

# Optional: SQLite file location (container default shown; local dev uses ../db/finally.db)
DB_PATH=/app/db/finally.db
```

### Behavior

- If `MASSIVE_API_KEY` is set and non-empty → backend uses Massive REST API for market data
- If `MASSIVE_API_KEY` is absent or empty → backend uses the built-in market simulator
- `MASSIVE_POLL_SECONDS` is passed through `create_market_data_source()` to `MassiveDataSource`; ignored by the simulator
- If `LLM_MOCK=true` → backend returns deterministic mock LLM responses (see §9)
- `DB_PATH` sets the SQLite file; tests point it at a temp file

### Loading `.env`

- **In Docker**: `docker run --env-file .env` supplies the variables; no `.env` file exists inside the container.
- **Local dev** (`uv run` from `backend/`): the app calls `python-dotenv`'s `load_dotenv(find_dotenv())` at startup, which searches upward and finds the project-root `.env`. Existing environment variables win.

### Backend Dependencies Still To Add

`litellm` (LLM calls) and `python-dotenv` (local `.env` loading) — via `uv add`.

---

## 6. Market Data

### Two Implementations, One Interface

Both the simulator and the Massive client implement the same abstract interface. The backend selects which to use based on the environment variable. All downstream code (SSE streaming, price cache, frontend) is agnostic to the source.

### Simulator (Default)

- Generates prices using geometric Brownian motion (GBM) with configurable drift and volatility per ticker
- Updates at ~500ms intervals
- Correlated moves across tickers (e.g., tech stocks move together)
- Occasional random "events" — sudden 2-5% moves on a ticker for drama
- Starts from realistic seed prices (e.g., AAPL ~$190, GOOGL ~$175, etc.)
- Runs as an in-process background task — no external dependencies

### Massive API (Optional)

- REST API polling (not WebSocket) — simpler, works on all tiers
- Polls for all tracked tickers in a single call, every `MASSIVE_POLL_SECONDS`
- Free tier (5 calls/min): poll every 15 seconds
- Paid tiers: poll every 2-15 seconds depending on tier
- Parses REST response into the same format as the simulator

### Supported Tickers

The ticker universe is a fixed list of ~50 well-known US equities defined in `backend/app/market/seed_prices.py`, each with a seed price and GBM parameters. The same list applies in both simulator and Massive modes. Adding a ticker to the watchlist or trading a ticker outside this list is rejected with 400 (`"Unknown ticker: APPL"`). This stops typos, or tickers the LLM invents, from becoming tradeable stocks at random prices.

### Tracked Tickers

The market data source tracks **the watchlist plus every ticker with an open position**. A held position always needs a live price for valuation, even after it leaves the watchlist.

- On startup, the source is started with `watchlist ∪ position tickers`.
- Adding to the watchlist, or buying a ticker not yet tracked, calls `source.add_ticker()`.
- Removing from the watchlist calls `source.remove_ticker()` only if no position is held; selling a position to zero calls it only if the ticker is not on the watchlist.

### Shared Price Cache

- A single background task (simulator or Massive poller) writes to an in-memory price cache
- The cache holds the latest price, previous price, and timestamp for each ticker
- The cache also keeps a ring buffer of the last 300 ticks per ticker (~2.5 minutes in the simulator), served by `GET /api/prices/history/{ticker}` so charts are populated on page load and after a refresh
- SSE streams read from this cache and push updates to connected clients
- This architecture supports future multi-user scenarios without changes to the data layer

### SSE Streaming

- Endpoint: `GET /api/stream/prices`
- Long-lived SSE connection; client uses native `EventSource` API and handles messages with `onmessage` (events are unnamed)
- The first line is `retry: 1000` so the browser reconnects after 1 second
- The server checks the cache every ~500ms and sends an event only when prices have changed. Each event carries **all tracked tickers in one JSON object keyed by ticker**:

```
data: {"AAPL": {"ticker": "AAPL", "price": 190.52, "previous_price": 190.41, "timestamp": 1758873600.123, "change": 0.11, "change_percent": 0.0578, "direction": "up"}, "GOOGL": {...}}
```

- `change` / `change_percent` / `direction` are relative to the **previous tick**, not the previous close
- A `: keepalive` comment is sent every ~10 seconds with no price change (e.g. Massive mode between polls), so idle proxies do not drop the connection
- Client handles reconnection automatically (EventSource has built-in retry)

### Timestamps

SSE and price-history timestamps are Unix seconds (float). All REST and DB timestamps are ISO 8601 UTC strings.

### Required Changes to the Built Market Data Code

The market data subsystem is complete, but this plan adds the following, to be implemented by the backend agent:

1. `seed_prices.py`: expand to ~50 supported tickers; expose the supported set for validation
2. `PriceCache`: add the 300-tick per-ticker ring buffer and a `get_history(ticker)` method
3. `factory.py`: read `MASSIVE_POLL_SECONDS` and pass it to `MassiveDataSource`
4. `stream.py`: emit a `: keepalive` comment after ~10 seconds without an event

---

## 7. Database

### SQLite Initialized at Startup

The backend initializes the database in the FastAPI lifespan, before the market data source starts (the source needs the watchlist and position tickers to call `start()`). If the file at `DB_PATH` doesn't exist or tables are missing, it creates the schema and seeds default data. This means:

- No separate migration step
- No manual database setup
- A fresh (empty) `db/` directory starts with a clean, seeded database automatically

### Concurrency

The 30-second snapshot task writes while request handlers read. Enable WAL mode (`PRAGMA journal_mode=WAL`) at initialization and use a short-lived connection per operation.

### Schema

All tables include a `user_id` column defaulting to `"default"`. This is hardcoded for now (single-user) but enables future multi-user support without schema migration.

**users_profile** — User state (cash balance)
- `id` TEXT PRIMARY KEY (default: `"default"`)
- `cash_balance` REAL (default: `10000.0`)
- `created_at` TEXT (ISO timestamp)

**watchlist** — Tickers the user is watching
- `id` TEXT PRIMARY KEY (UUID)
- `user_id` TEXT (default: `"default"`)
- `ticker` TEXT
- `added_at` TEXT (ISO timestamp)
- UNIQUE constraint on `(user_id, ticker)`

**positions** — Current holdings (one row per ticker per user)
- `id` TEXT PRIMARY KEY (UUID)
- `user_id` TEXT (default: `"default"`)
- `ticker` TEXT
- `quantity` REAL (fractional shares supported)
- `avg_cost` REAL
- `updated_at` TEXT (ISO timestamp)
- UNIQUE constraint on `(user_id, ticker)`

**trades** — Trade history (append-only log)
- `id` TEXT PRIMARY KEY (UUID)
- `user_id` TEXT (default: `"default"`)
- `ticker` TEXT
- `side` TEXT (`"buy"` or `"sell"`)
- `quantity` REAL (fractional shares supported)
- `price` REAL
- `executed_at` TEXT (ISO timestamp)

**portfolio_snapshots** — Portfolio value over time (for P&L chart). Recorded every 30 seconds by a background task, and immediately after each trade execution.
- `id` TEXT PRIMARY KEY (UUID)
- `user_id` TEXT (default: `"default"`)
- `total_value` REAL
- `recorded_at` TEXT (ISO timestamp)

**chat_messages** — Conversation history with LLM
- `id` TEXT PRIMARY KEY (UUID)
- `user_id` TEXT (default: `"default"`)
- `role` TEXT (`"user"` or `"assistant"`)
- `content` TEXT
- `actions` TEXT (JSON — trades executed, watchlist changes made; null for user messages)
- `created_at` TEXT (ISO timestamp)

### Default Seed Data

- One user profile: `id="default"`, `cash_balance=10000.0`
- Ten watchlist entries: AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX

### Portfolio Rules

- **Fill price**: the price cache's current price at execution time. No cached price yet (e.g. just added, Massive mode awaiting its next poll) → 400 `"No price available for X yet"`.
- **Validation**: quantity must be > 0; buys require `cash >= quantity × price`; sells require `quantity <= held quantity`; the ticker must be supported (§6).
- **Buys** update `avg_cost` as the quantity-weighted average of the old cost and the fill price.
- **Sells** leave `avg_cost` unchanged. The `positions` row is deleted when quantity reaches zero.
- **Unrealized P&L** per position = `(price − avg_cost) × quantity`; **% change** = `(price − avg_cost) / avg_cost`.
- **Realized P&L is not tracked** — selling at a profit simply increases cash. The headline figure is **total return = total_value − 10,000**, where `total_value = cash + Σ(price × quantity)`.

---

## 8. API Endpoints

### Market Data
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/stream/prices` | SSE stream of live price updates (§6) |
| GET | `/api/prices/history/{ticker}` | Last ≤300 ticks for a ticker from the cache ring buffer: `[{price, timestamp}]`, oldest first |

### Portfolio
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/portfolio` | Current positions, cash balance, total value, unrealized P&L, total return |
| POST | `/api/portfolio/trade` | Execute a trade: `{ticker, quantity, side}`. Returns the executed trade including the fill `price` |
| GET | `/api/portfolio/history?limit=500` | Most recent portfolio value snapshots (default 500), returned oldest first for charting |

### Watchlist
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/watchlist` | Current watchlist tickers with latest prices (so the grid is populated on first paint, before the first SSE event) |
| POST | `/api/watchlist` | Add a supported ticker: `{ticker}` |
| DELETE | `/api/watchlist/{ticker}` | Remove a ticker |

### Chat
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat` | Send a message, receive complete JSON response (message + executed actions) |
| GET | `/api/chat/history?limit=50` | Recent chat messages with their actions, oldest first, so the panel is restored after a refresh |

### System
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check (for Docker/deployment) |

### Errors

All client errors use HTTP 400 with FastAPI's default shape, and the message is written to be shown to the user as-is:

```json
{"detail": "Insufficient cash: need $1,905.00, have $1,200.00"}
```

Cases: insufficient cash, insufficient shares, non-positive quantity, unknown ticker, duplicate watchlist ticker, no price available yet. These rules live in one shared trade/watchlist service, so manual and LLM-initiated actions fail with identical messages. An unreachable LLM returns 503 (§9). Malformed request bodies keep FastAPI's default 422.

---

## 9. LLM Integration

When writing code to make calls to LLMs, use cerebras-inference skill to use LiteLLM via OpenRouter to the `openrouter/openai/gpt-oss-120b` model with Cerebras as the inference provider. Structured Outputs should be used to interpret the results.

There is an OPENROUTER_API_KEY in the .env file in the project root.

### How It Works

When the user sends a chat message, the backend:

1. Loads the user's current portfolio context (cash, positions with P&L, watchlist with live prices, total portfolio value). This is rebuilt and re-sent on every turn, since prices move.
2. Loads the last 20 messages from the `chat_messages` table
3. Constructs a prompt with a system message, portfolio context, conversation history, and the user's new message
4. Calls the LLM via LiteLLM → OpenRouter, requesting structured output, using the cerebras-inference skill
5. Parses the complete structured JSON response
6. Auto-executes any trades or watchlist changes specified in the response
7. Stores the message and executed actions in `chat_messages`
8. Returns the complete JSON response to the frontend (no token-by-token streaming — Cerebras inference is fast enough that a loading indicator is sufficient)

### Structured Output Schema

The LLM is instructed to respond with JSON matching this schema:

```json
{
  "message": "Your conversational response to the user",
  "trades": [
    {"ticker": "AAPL", "side": "buy", "quantity": 10}
  ],
  "watchlist_changes": [
    {"ticker": "PYPL", "action": "add"}
  ]
}
```

- `message` (required): The conversational text shown to the user
- `trades` (optional): Array of trades to auto-execute. Each trade goes through the same validation as manual trades (sufficient cash for buys, sufficient shares for sells)
- `watchlist_changes` (optional): Array of watchlist modifications

### Auto-Execution

Trades specified by the LLM execute automatically — no confirmation dialog. This is a deliberate design choice:
- It's a simulated environment with fake money, so the stakes are zero
- It creates an impressive, fluid demo experience
- It demonstrates agentic AI capabilities — the core theme of the course

If a trade or watchlist change fails validation (e.g., insufficient cash), there is **no second LLM call**. The failure is recorded in the message's `actions` JSON with its error text, and the frontend renders it inline (e.g. "Trade failed: Insufficient cash: need $1,905.00, have $1,200.00"). This keeps chat fast, cheap, and deterministic for tests.

Each entry in `actions` records what was attempted and the outcome:

```json
{
  "trades": [
    {"ticker": "AAPL", "side": "buy", "quantity": 10, "status": "executed", "price": 190.52},
    {"ticker": "TSLA", "side": "buy", "quantity": 500, "status": "failed", "error": "Insufficient cash: need $124,500.00, have $8,094.80"}
  ],
  "watchlist_changes": [
    {"ticker": "PYPL", "action": "add", "status": "executed"}
  ]
}
```

### Failure Handling

If OpenRouter is unreachable, the key is missing, or the response cannot be parsed, `POST /api/chat` returns 503 with a displayable `detail` message and writes nothing to `chat_messages`.

### System Prompt Guidance

The LLM should be prompted as "FinAlly, an AI trading assistant" with instructions to:
- Analyze portfolio composition, risk concentration, and P&L
- Suggest trades with reasoning
- Execute trades when the user asks or agrees
- Manage the watchlist proactively
- Be concise and data-driven in responses
- Always respond with valid structured JSON

### LLM Mock Mode

When `LLM_MOCK=true`, the backend returns deterministic mock responses instead of calling OpenRouter. This enables:
- Fast, free, reproducible E2E tests
- Development without an API key
- CI/CD pipelines

The mock produces the same structured output as the real LLM, and its actions go through normal auto-execution. Rules, matched case-insensitively on the user message in this order:

| Message contains | Mock response |
|---|---|
| `buy` | Buy 1 share of the first supported ticker mentioned (else AAPL) |
| `sell` | Sell 1 share of the first supported ticker mentioned (else AAPL) |
| `watch` | Add the first supported ticker mentioned (else PYPL) to the watchlist |
| anything else | A fixed analysis message with no actions |

---

## 10. Frontend Design

### Layout

The frontend is a single-page application with a dense, terminal-inspired layout. The specific component architecture and layout system is up to the Frontend Engineer, but the UI should include these elements:

- **Watchlist panel** — grid/table of watched tickers with: ticker symbol, current price (flashing green/red on change), session change % (from the oldest price in the ticker's loaded history to the current price — there is no previous-close data), and a sparkline mini-chart
- **Main chart area** — larger chart for the currently selected ticker, with at minimum price over time. Clicking a ticker in the watchlist selects it here.
- **Chart data** — sparklines and the main chart are seeded from `GET /api/prices/history/{ticker}` on load, then extended from the SSE stream (frontend keeps at most ~300 points per ticker)
- **Portfolio heatmap** — treemap visualization where each rectangle is a position, sized by portfolio weight, colored by P&L (green = profit, red = loss)
- **P&L chart** — line chart showing total portfolio value over time, using data from `portfolio_snapshots`
- **Positions table** — tabular view of all positions: ticker, quantity, avg cost, current price, unrealized P&L, % change
- **Trade bar** — simple input area: ticker field, quantity field, buy button, sell button. Market orders, instant fill.
- **AI chat panel** — docked/collapsible sidebar. Message input, scrolling conversation history (restored from `GET /api/chat/history` on load), loading indicator while waiting for LLM response. Executed and failed trades and watchlist changes shown inline.
- **Header** — portfolio total value (updating live), connection status indicator, cash balance

### Technical Notes

- Use `EventSource` for SSE connection to `/api/stream/prices` (payload shape in §6)
- Canvas-based charting library preferred (Lightweight Charts or Recharts) for performance
- Price flash effect: when the displayed (2-decimal) price changes, briefly apply a CSS class with background color transition, then remove it
- All API calls go to the same origin (`/api/*`) — no CORS configuration needed
- Show API error `detail` messages to the user as-is (§8)
- Tailwind CSS for styling with a custom dark theme
- **Static export constraints**: `output: 'export'` rules out Next.js route handlers, middleware, server-side rendering, server actions and the default Image optimization loader. Everything is client-side; data comes only from `/api/*`.

---

## 11. Docker & Deployment

### Multi-Stage Dockerfile

```
Stage 1: Node 22 slim (current LTS)
  - Copy frontend/
  - npm install && npm run build (produces static export)

Stage 2: Python 3.12 slim
  - Install uv
  - Copy backend/
  - uv sync (install Python dependencies from lockfile)
  - Copy frontend build output into a static/ directory
  - Expose port 8000
  - CMD: uvicorn serving FastAPI app
```

FastAPI serves the static frontend files and all API routes on port 8000.

### Database Persistence (Bind Mount)

The project-root `db/` directory is bind-mounted into the container, so `finally.db` is visible on the host and easy for students to inspect or delete:

```bash
# macOS/Linux
docker run -v "$(pwd)/db:/app/db" -p 8000:8000 --env-file .env finally

# Windows PowerShell
docker run -v "${PWD}/db:/app/db" -p 8000:8000 --env-file .env finally
```

The backend writes `finally.db` to `/app/db` (the `DB_PATH` default). To reset all data, stop the container and delete `db/finally.db`.

### Start/Stop Scripts

**`scripts/start_mac.sh`** (macOS/Linux):
- Builds the Docker image if not already built (or if `--build` flag passed)
- Runs the container with the `db/` bind mount, port mapping, and `.env` file
- Prints the URL to access the app
- Optionally opens the browser

**`scripts/stop_mac.sh`** (macOS/Linux):
- Stops and removes the running container
- Does NOT touch `db/` (data persists)

**`scripts/start_windows.ps1`** / **`scripts/stop_windows.ps1`**: PowerShell equivalents for Windows.

All scripts should be idempotent — safe to run multiple times.

### Optional Cloud Deployment

The container is designed to deploy to AWS App Runner, Render, or any container platform. A Terraform configuration for App Runner may be provided in a `deploy/` directory as a stretch goal, but is not part of the core build.

---

## 12. Testing Strategy

### Unit Tests (within `frontend/` and `backend/`)

**Backend (pytest)**:
- Market data: simulator generates valid prices, GBM math is correct, Massive API response parsing works, both implementations conform to the abstract interface
- Portfolio: trade execution logic, P&L calculations, edge cases (selling more than owned, buying with insufficient cash, selling at a loss)
- LLM: structured output parsing handles all valid schemas, graceful handling of malformed responses, trade validation within chat flow, mock-mode rules
- API routes: correct status codes, response shapes, error handling (§8 error contract)

**Frontend (Vitest + React Testing Library)**:
- Component rendering with mock data
- Price flash animation triggers correctly on price changes
- Watchlist CRUD operations
- Portfolio display calculations
- Chat message rendering and loading state

### E2E Tests (in `test/`)

**Infrastructure**: Playwright runs from the host (`npx playwright test` in `test/`) against the app container on `localhost:8000`. Browser dependencies stay out of the production image. A `docker-compose.test.yml` that adds a Playwright container is optional, only for CI environments without browsers.

**Environment**: The app container runs with `LLM_MOCK=true` for speed and determinism, and a fresh `db/` directory so each run starts from the seed data.

**Key Scenarios**:
- Fresh start: default watchlist appears, $10k balance shown, prices are streaming
- Add and remove a ticker from the watchlist
- Buy shares: cash decreases, position appears, portfolio updates
- Sell shares: cash increases, position updates or disappears
- Portfolio visualization: heatmap renders with correct colors, P&L chart has data points
- AI chat (mocked): send a message, receive a response, trade execution appears inline
- SSE resilience: disconnect and verify reconnection
