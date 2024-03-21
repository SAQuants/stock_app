
import yfinance as yf
from datetime import datetime

supported_symbols = [
    {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "exchange": "AMEX"},
    {"symbol": "VUG", "name": "US large-cap growth stocks", "exchange": "AMEX"},
    {"symbol": "VTV", "name": "Developed-market large-cap stocks", "exchange": "AMEX"}
]

def get_supported_symbols():
    return supported_symbols

def get_symbol_info(symbol):
    symbols =  get_supported_symbols()
    symbol_list = [ dict_ for dict_ in symbols if dict_['symbol'] == symbol]
    symbol_info = symbol_list[0]
    return symbol_info

def get_symbol_ts(symbol,
                  start_date=datetime.strptime("2023-01-01", "%Y-%m-%d"),
                  end_date=datetime.strptime("2024-01-01", "%Y-%m-%d")):

    ts = yf.download(symbol, start=start_date, end=end_date)
    ts = ts.reset_index()
    ts['Date'] = ts['Date'].dt.date
    ts[['Open', 'High', 'Low', 'Close']] = ts[['Open', 'High', 'Low', 'Close']].round(2)
    # print(ts.head(2))
    # return ts.to_dict('records')
    return ts