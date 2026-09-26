"""Tests for the supported ticker universe."""

from app.market.seed_prices import (
    CORRELATION_GROUPS,
    SEED_PRICES,
    SUPPORTED_TICKERS,
    TICKER_PARAMS,
)
from app.market.simulator import GBMSimulator

DEFAULT_WATCHLIST = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "JPM", "V", "NFLX"]


class TestSupportedTickers:
    """The supported set is the seed-price keys, and every entry is fully configured."""

    def test_about_fifty_tickers(self):
        assert len(SUPPORTED_TICKERS) == 50

    def test_matches_seed_prices(self):
        assert SUPPORTED_TICKERS == set(SEED_PRICES)

    def test_includes_default_watchlist_and_mock_ticker(self):
        assert set(DEFAULT_WATCHLIST) <= SUPPORTED_TICKERS
        assert "PYPL" in SUPPORTED_TICKERS

    def test_every_ticker_has_params(self):
        assert set(TICKER_PARAMS) == SUPPORTED_TICKERS

    def test_groups_only_contain_supported_tickers(self):
        for group in CORRELATION_GROUPS.values():
            assert group <= SUPPORTED_TICKERS

    def test_simulator_handles_full_universe(self):
        sim = GBMSimulator(sorted(SUPPORTED_TICKERS))
        prices = sim.step()
        assert set(prices) == SUPPORTED_TICKERS
        assert all(p > 0 for p in prices.values())
