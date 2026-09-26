"""Seed prices and per-ticker parameters for the market simulator.

The keys of SEED_PRICES define the supported ticker universe: the API rejects
any ticker outside SUPPORTED_TICKERS, in both simulator and Massive modes.
"""

# Realistic starting prices (as of project creation)
SEED_PRICES: dict[str, float] = {
    # Default watchlist
    "AAPL": 190.00,
    "GOOGL": 175.00,
    "MSFT": 420.00,
    "AMZN": 185.00,
    "TSLA": 250.00,
    "NVDA": 800.00,
    "META": 500.00,
    "JPM": 195.00,
    "V": 280.00,
    "NFLX": 600.00,
    # Tech
    "AMD": 160.00,
    "INTC": 35.00,
    "CRM": 290.00,
    "ORCL": 125.00,
    "ADBE": 520.00,
    "AVGO": 1300.00,
    "QCOM": 170.00,
    "CSCO": 50.00,
    "IBM": 185.00,
    "UBER": 70.00,
    "SHOP": 75.00,
    "PLTR": 25.00,
    # Finance
    "MA": 460.00,
    "BAC": 38.00,
    "GS": 450.00,
    "MS": 95.00,
    "WFC": 58.00,
    "C": 62.00,
    "PYPL": 65.00,
    "AXP": 230.00,
    "BLK": 800.00,
    "SCHW": 72.00,
    # Consumer
    "WMT": 60.00,
    "COST": 730.00,
    "KO": 62.00,
    "PEP": 170.00,
    "MCD": 290.00,
    "NKE": 95.00,
    "DIS": 110.00,
    "HD": 360.00,
    "PG": 160.00,
    # Healthcare
    "JNJ": 155.00,
    "PFE": 28.00,
    "UNH": 500.00,
    "LLY": 770.00,
    "MRK": 125.00,
    # Energy and industrials
    "XOM": 115.00,
    "CVX": 160.00,
    "BA": 185.00,
    "CAT": 340.00,
}

SUPPORTED_TICKERS: frozenset[str] = frozenset(SEED_PRICES)

# Per-ticker GBM parameters
# sigma: annualized volatility (higher = more price movement)
# mu: annualized drift / expected return
TICKER_PARAMS: dict[str, dict[str, float]] = {
    "AAPL": {"sigma": 0.22, "mu": 0.05},
    "GOOGL": {"sigma": 0.25, "mu": 0.05},
    "MSFT": {"sigma": 0.20, "mu": 0.05},
    "AMZN": {"sigma": 0.28, "mu": 0.05},
    "TSLA": {"sigma": 0.50, "mu": 0.03},  # High volatility
    "NVDA": {"sigma": 0.40, "mu": 0.08},  # High volatility, strong drift
    "META": {"sigma": 0.30, "mu": 0.05},
    "JPM": {"sigma": 0.18, "mu": 0.04},  # Low volatility (bank)
    "V": {"sigma": 0.17, "mu": 0.04},  # Low volatility (payments)
    "NFLX": {"sigma": 0.35, "mu": 0.05},
    "AMD": {"sigma": 0.45, "mu": 0.06},
    "INTC": {"sigma": 0.35, "mu": 0.01},
    "CRM": {"sigma": 0.30, "mu": 0.05},
    "ORCL": {"sigma": 0.25, "mu": 0.05},
    "ADBE": {"sigma": 0.30, "mu": 0.04},
    "AVGO": {"sigma": 0.35, "mu": 0.07},
    "QCOM": {"sigma": 0.30, "mu": 0.04},
    "CSCO": {"sigma": 0.20, "mu": 0.03},
    "IBM": {"sigma": 0.20, "mu": 0.03},
    "UBER": {"sigma": 0.40, "mu": 0.06},
    "SHOP": {"sigma": 0.50, "mu": 0.05},
    "PLTR": {"sigma": 0.55, "mu": 0.07},
    "MA": {"sigma": 0.18, "mu": 0.04},
    "BAC": {"sigma": 0.25, "mu": 0.04},
    "GS": {"sigma": 0.25, "mu": 0.04},
    "MS": {"sigma": 0.25, "mu": 0.04},
    "WFC": {"sigma": 0.25, "mu": 0.04},
    "C": {"sigma": 0.28, "mu": 0.03},
    "PYPL": {"sigma": 0.35, "mu": 0.03},
    "AXP": {"sigma": 0.22, "mu": 0.05},
    "BLK": {"sigma": 0.22, "mu": 0.05},
    "SCHW": {"sigma": 0.28, "mu": 0.04},
    "WMT": {"sigma": 0.15, "mu": 0.04},
    "COST": {"sigma": 0.18, "mu": 0.05},
    "KO": {"sigma": 0.13, "mu": 0.03},
    "PEP": {"sigma": 0.14, "mu": 0.03},
    "MCD": {"sigma": 0.16, "mu": 0.04},
    "NKE": {"sigma": 0.28, "mu": 0.03},
    "DIS": {"sigma": 0.28, "mu": 0.03},
    "HD": {"sigma": 0.20, "mu": 0.04},
    "PG": {"sigma": 0.13, "mu": 0.03},
    "JNJ": {"sigma": 0.14, "mu": 0.03},
    "PFE": {"sigma": 0.25, "mu": 0.01},
    "UNH": {"sigma": 0.22, "mu": 0.04},
    "LLY": {"sigma": 0.30, "mu": 0.08},
    "MRK": {"sigma": 0.18, "mu": 0.03},
    "XOM": {"sigma": 0.22, "mu": 0.03},
    "CVX": {"sigma": 0.22, "mu": 0.03},
    "BA": {"sigma": 0.35, "mu": 0.02},
    "CAT": {"sigma": 0.25, "mu": 0.05},
}

# Default parameters for tickers not in the list above (dynamically added)
DEFAULT_PARAMS: dict[str, float] = {"sigma": 0.25, "mu": 0.05}

# Correlation groups for the simulator's Cholesky decomposition
# Tickers in the same group have higher intra-group correlation
CORRELATION_GROUPS: dict[str, set[str]] = {
    "tech": {
        "AAPL", "GOOGL", "MSFT", "AMZN", "META", "NVDA", "NFLX",
        "AMD", "INTC", "CRM", "ORCL", "ADBE", "AVGO", "QCOM", "CSCO", "IBM",
        "UBER", "SHOP", "PLTR",
    },
    "finance": {"JPM", "V", "MA", "BAC", "GS", "MS", "WFC", "C", "PYPL", "AXP", "BLK", "SCHW"},
}

# Correlation coefficients
INTRA_TECH_CORR = 0.6  # Tech stocks move together
INTRA_FINANCE_CORR = 0.5  # Finance stocks move together
CROSS_GROUP_CORR = 0.3  # Between sectors / unknown tickers
TSLA_CORR = 0.3  # TSLA does its own thing
