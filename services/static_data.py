supported_symbols = [
    {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "exchange": "AMEX"},
    {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
    {"symbol": "IBM", "name": "International Business Machines Corporations", "exchange": "NYSE"}
]

supported_backtests = [
    {"backtest": "strategy_bb_rsi", "description": " bollinger band 2 std_dev, rsi between 30 - 70"}
]


def get_supported_symbols():
    return supported_symbols


def get_supported_backtests():
    return supported_backtests


def get_symbol_info(symbol):
    symbols = get_supported_symbols()
    symbol_list = [dict_ for dict_ in symbols if dict_['symbol'] == symbol]
    symbol_info = symbol_list[0]
    return symbol_info
