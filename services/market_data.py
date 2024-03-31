from datetime import datetime

import yfinance as yf


def get_symbol_ts(symbol, start_date, end_date):
    start_date=datetime.strptime(start_date, "%Y-%m-%d")
    end_date=datetime.strptime(end_date, "%Y-%m-%d")
    ts = yf.download(symbol, start=start_date, end=end_date)
    ts = ts.reset_index()
    ts['Date'] = ts['Date'].dt.date
    ts[['Open', 'High', 'Low', 'Close']] = ts[['Open', 'High', 'Low', 'Close']].round(2)
    # print(ts.head(2))
    # return ts.to_dict('records')
    return ts
