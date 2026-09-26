"""Factory for creating market data sources."""

from __future__ import annotations

import logging
import os

from .cache import PriceCache
from .interface import MarketDataSource
from .massive_client import MassiveDataSource
from .simulator import SimulatorDataSource

logger = logging.getLogger(__name__)


def create_market_data_source(price_cache: PriceCache) -> MarketDataSource:
    """Create the appropriate market data source based on environment variables.

    - MASSIVE_API_KEY set and non-empty → MassiveDataSource (real market data),
      polling every MASSIVE_POLL_SECONDS (default 15)
    - Otherwise → SimulatorDataSource (GBM simulation)

    Returns an unstarted source. Caller must await source.start(tickers).
    """
    api_key = os.environ.get("MASSIVE_API_KEY", "").strip()

    if api_key:
        poll_interval = float(os.environ.get("MASSIVE_POLL_SECONDS", "15"))
        logger.info("Market data source: Massive API (real data), %.1fs poll", poll_interval)
        return MassiveDataSource(
            api_key=api_key, price_cache=price_cache, poll_interval=poll_interval
        )
    else:
        logger.info("Market data source: GBM Simulator")
        return SimulatorDataSource(price_cache=price_cache)
