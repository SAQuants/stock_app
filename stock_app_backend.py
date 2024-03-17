from fastapi import FastAPI, Request
# $ uvicorn stock_app_backend:app --reload
from fastapi.templating import Jinja2Templates
import yfinance as yf
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_supported_symbols():
    supported_symbols = [
        {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust"},
        {"symbol": "VUG", "name": "US large-cap growth stocks"},
        {"symbol": "VTV", "name": "Developed-market large-cap stocks"}
    ]
    return supported_symbols

def get_stock_data(symbol,
                   start_date=datetime.strptime("2023-01-01", "%Y-%m-%d"),
                   end_date=datetime.strptime("2024-01-01", "%Y-%m-%d")):
    stock_data = yf.download(symbol, start=start_date, end=end_date)
    return stock_data

@app.get("/")
async def get_list(request: Request):
    # print(dir(request))
    # print(request.headers)
    supported_symbols = get_supported_symbols()
    # return {"Supported List": supported_symbols}
    accept = request.headers["accept"]
    print(f'accept: {accept}, len(accept.split(",")): {len(accept.split(","))}')
    if len(accept.split(",")) > 1:
        print('get_list: returning html')
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"supported_symbols": supported_symbols})
    else:
        print('get_list: returning data')
        return supported_symbols

@app.get("/symbol/{symbol}")
async def get_price(request: Request, symbol):
    # print(symbol)
    # print(request.headers)
    ts = get_stock_data(symbol).reset_index()
    ts['Date'] = ts['Date'].dt.date
    ts[['Open','High', 'Low', 'Close']] = ts[['Open','High', 'Low', 'Close']].round(2)
    # print(ts.head(2))
    # return ts.to_dict('records')
    accept = request.headers["accept"]
    print(f'accept: {accept}, len(accept.split(",")): {len(accept.split(","))}')
    if len(accept.split(",")) > 1:
        print('get_price: returning html')
        return templates.TemplateResponse(
            request=request,
            name="symbol_price.html",
            context={
                "time_series" : ts.to_dict('records'),
                "symbol": symbol
            }
        )
    else:
        print('get_price: returning data')
        return ts.to_json()
    pass