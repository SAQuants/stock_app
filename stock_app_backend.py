from fastapi import FastAPI, Request
# $ uvicorn stock_app_backend:app --reload
from fastapi.templating import Jinja2Templates

from market_data import get_supported_symbols, get_symbol_ts, get_symbol_info
from backtest_launcher import execute_backtest

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_response_type(request: Request):
    accept = request.headers["accept"]
    print(f'accept: {accept}, len(accept.split(",")): {len(accept.split(","))}')
    if len(accept.split(",")) > 1:
        print('get_response_type: html')
        return 'html'
    else:
        print('get_response_type: data')
        return 'data'


@app.get("/")
async def get_list(request: Request):
    # print(dir(request))
    # print(request.headers)
    symbol_info_list = get_supported_symbols()
    if get_response_type(request) == 'html':
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"supported_symbols": symbol_info_list})
    else:
        return symbol_info_list

@app.get("/symbol/{symbol}")
async def get_details(request: Request, symbol):
    # print(request.headers)

    backtest = request.query_params.get('backtest', False)
    # print(symbol, backtest)
    if backtest:
        return get_backtest_results(request, symbol, backtest)
    else:
        return get_symbol_data(request,symbol)

def get_symbol_data(request,symbol):
    symbol_info = get_symbol_info(symbol)
    stock_ts = get_symbol_ts(symbol)
    if get_response_type(request) == 'html':
        return templates.TemplateResponse(
            request=request,
            name="symbol_price.html",
            context={
                "time_series": stock_ts.to_dict('records'),
                "symbol_info": symbol_info
            }
        )
    else:
        return stock_ts.to_json()

def get_backtest_results(request, symbol, backtest_name):
    return execute_backtest(backtest_name, symbol)