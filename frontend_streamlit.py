# pip list --format=freeze > requirements.txt
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests
import io

backend_url = 'http://127.0.0.1:8000'
# streamlit run frontend_streamlit.py


def get_stock_data(ticker, params):
    # stock_data = yf.download(ticker, start=start_date, end=end_date)
    # stock_data = pd.read_json(io.StringIO(json_str))
    res = requests.get(f"{backend_url}/symbol/{ticker}", params=params)
    # print(f'res: {res}, res.json(): {res.json()}')
    if res.status_code != 200:
        print(res, res.text)
        return res.text

    response_dict = res.json()
    if 'backtest' not in params:
        stock_data = pd.read_json(io.StringIO(response_dict)) #pd.read_json(res.json())#
        stock_data['Date'] = stock_data['Date'].dt.date
        stock_data.set_index('Date', inplace=True)
    else:
        response_dict = res.json()
        order_plot_path = response_dict['output_dir'] + '/df_order_plot.csv'
        stock_data = pd.read_csv(order_plot_path)
        # stock_data = pd.read_json(response_dict['df_order_plot'])

    return stock_data


def main():
    st.title("Stock Time Series Data App")

    # User input for stock ticker
    res = requests.get(backend_url)
    if res.status_code != 200:
        print(res, res.text)
        return

    df_symbol = pd.DataFrame(res.json())
    print(df_symbol['symbol'].values)

    ticker = st.selectbox("Enter Stock Ticker:", df_symbol['symbol'])

    # User input for date range
    date_format = "%Y-%m-%d"
    start_date = st.date_input("Start Date", datetime.strptime("2023-01-01", date_format))
    end_date = st.date_input("End Date", datetime.strptime("2023-12-31", date_format))

    # Button to fetch data
    if st.button("Get Time Series Data"):
        st.write(f"Fetching data for {ticker}...")

        # Get stock data
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        stock_data = get_stock_data(ticker, params)
        # Display the data
        # st.write("Time Series Data:")
        # st.write(stock_data)
        # Plot the closing price using Plotly
        fig = px.line(stock_data, x=stock_data.index, y='Close', title=f'{ticker} Stock Price')
        st.plotly_chart(fig)

    if st.button("Perform BackTest"):
        st.write(f"Performing backtest for {ticker}...")
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'backtest': 'strategy_bb_rsi'
        }
        backtest_results = get_stock_data(ticker, params)
        # Display the data
        st.write("Backtest Results:")
        st.write(backtest_results)


if __name__ == "__main__":
    main()
