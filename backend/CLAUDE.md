# Backend — Developer Guide

## Project Setup

```bash
cd backend
uv sync --extra dev   # Install all dependencies including test/lint tools
```

## Market Data API

The market data subsystem lives in `app/market/`. Use these imports:

```python
from app.market import (
    PriceCache, PriceUpdate, MarketDataSource, create_market_data_source, SUPPORTED_TICKERS,
)
```

### Core Types

- **`PriceUpdate`** — Immutable dataclass: `ticker`, `price`, `previous_price`, `timestamp`, plus properties `change`, `change_percent`, `direction` ("up"/"down"/"flat"), and `to_dict()` for JSON serialization.

- **`PriceCache`** — Thread-safe in-memory store. Key methods:
  - `update(ticker, price, timestamp=None) -> PriceUpdate`
  - `get(ticker) -> PriceUpdate | None`
  - `get_price(ticker) -> float | None`
  - `get_all() -> dict[str, PriceUpdate]`
  - `get_history(ticker) -> list[PriceUpdate]` — last 300 updates (constructor `history_size`), oldest first
  - `remove(ticker)` — also clears the ticker's history
  - `version` property — monotonic counter, increments on every update (for SSE change detection)

- **`MarketDataSource`** — Abstract interface implemented by `SimulatorDataSource` and `MassiveDataSource`. Lifecycle: `start(tickers)` -> `add_ticker()` / `remove_ticker()` -> `stop()`.

- **`create_market_data_source(cache)`** — Factory. Returns `MassiveDataSource` if `MASSIVE_API_KEY` is set (polling every `MASSIVE_POLL_SECONDS`, default 15), otherwise `SimulatorDataSource`.

### SSE Streaming

```python
from app.market import create_stream_router

router = create_stream_router(price_cache)  # Returns FastAPI APIRouter
# Endpoint: GET /api/stream/prices (text/event-stream)
```

Each event is one `data:` line holding all tracked tickers keyed by ticker. A `: keepalive` comment is sent after 10 seconds without an event.

### Seed Data

`SUPPORTED_TICKERS` is the universe of 50 tickers the API accepts — the keys of `SEED_PRICES`. Seed prices, per-ticker volatility/drift params and correlation groups are in `app/market/seed_prices.py`. Default watchlist: AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX.

## Running Tests

```bash
uv run --extra dev pytest -v              # All tests
uv run --extra dev pytest --cov=app       # With coverage
uv run --extra dev ruff check app/ tests/ # Lint
```

## Demo

```bash
uv run market_data_demo.py   # Live terminal dashboard with simulated prices
```
