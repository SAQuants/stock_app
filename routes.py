from fastapi import FastAPI, Request, HTTPException
# local start -->$ uvicorn --app-dir ./ routes:app --reload
from fastapi.templating import Jinja2Templates
import os
import fastapi
import signal

from services.static_data import get_supported_symbols, get_symbol_info, get_supported_backtests
from services.market_data import get_symbol_ts
from services.backtest_launcher import execute_backtest

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_response_type(request: Request):
    accept = request.headers["accept"]
    # print(f'accept: {accept}, len(accept.split(",")): {len(accept.split(","))}')
    if len(accept.split(",")) > 1:
        print('response_type: html')
        return 'html'
    else:
        print('response_type: data')
        return 'data'


@app.get("/shutdown")
def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return fastapi.Response(status_code=200, content='shutdown: Server shutting down...')

@app.on_event('shutdown')
def on_shutdown():
    print('on_shutdown: Server shutting down...')

@app.get("/")
@app.get("/symbols")
def get_symbol_list(request: Request):
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


@app.get("/backtests")
def get_backtest_list(request: Request):
    # print(dir(request))
    # print(request.headers)
    backtest_list = get_supported_backtests()
    if get_response_type(request) == 'html':
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"supported_backtest": backtest_list})
    else:
        return backtest_list


@app.get("/symbol/{symbol}")
def get_details(request: Request, symbol):
    # print(request.headers)

    backtest = request.query_params.get('backtest', None)
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    print(f'get_details params: {symbol}, {backtest}, {start_date}, {end_date}')
    if backtest is None:
        return get_symbol_data(request, symbol, start_date, end_date)
    else:
        return get_backtest_results(request, symbol, backtest, start_date, end_date)


def get_symbol_data(request, symbol, start_date, end_date):
    symbol_info = get_symbol_info(symbol)
    stock_ts = get_symbol_ts(symbol,start_date, end_date)
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


def get_backtest_results(request, symbol, backtest_name, start_date, end_date):
    backtest_results = execute_backtest(symbol, backtest_name,  start_date, end_date)
    # print(f'get_backtest_results::{backtest_results}')
    if backtest_results["status"] != 200:
        print(f'get_backtest_results --> HTTPException')
        raise HTTPException(status_code=backtest_results["status"],
                            detail=backtest_results)
    else:
        print(f'get_backtest_results --> Success')
        return backtest_results
