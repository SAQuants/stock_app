# region imports
import pandas as pd
from AlgorithmImports import *
from datetime import datetime
import json
import os
LEAN_RESULTS_DIR ='/Results'
LEAN_BASE_DIR = '/LeanCLI/'
# endregion

class SpyBB(QCAlgorithm):

    def Initialize(self):

        # self.Log(f'getcwd: {os.getcwd()}')
        # dir_obj = os.scandir('/')
        # sub_dir = [ files.name for files in dir_obj if files.is_dir()]
        # self.Log(f'Initialize scandir(/) results:\n {sub_dir}')
        # for current_path, folders, files in os.walk('/LeanCLI'):
        #    self.Log(f'current_path, folders, files\n '
        #             f'{current_path}, {folders}, {files}')
        # Convert JSON string to Pandas DataFrame
        # Retrieve JSON data from the file
        start_date_str = "20190101"
        end_date_str = "20220101"
        trade_symbol = "SPY"
        self.benchmark_symbol = "SPY"
        #with open("config.json", "r") as file:
        strategy_config = LEAN_BASE_DIR + "strategy_config/sconfig.json"
        with open(strategy_config, "r") as file:
            self.Log(f'reading {strategy_config}')
            json_obj = json.load(file)
            self.Log(json.dumps(json_obj, indent=4))
            start_date_str = json_obj["start_date"] if "start_date" in json_obj else start_date_str
            end_date_str = json_obj["end_date"] if "end_date" in json_obj else end_date_str
            trade_symbol = json_obj["trade_symbol"] if "trade_symbol" in json_obj else trade_symbol
            self.benchmark_symbol = json_obj["benchmark_symbol"] if "benchmark_symbol" in json_obj else self.benchmark_symbol

        start_date = datetime.strptime(start_date_str, "%Y%m%d")
        end_date = datetime.strptime(end_date_str, "%Y%m%d")

        self.Log(f"Environment Info: "
                 f"start_date={start_date},end_date={end_date},trade_symbol={trade_symbol},"
                 f"benchmark_symbol={self.benchmark_symbol}")

        self.SetStartDate(start_date.year, start_date.month, start_date.day)
        self.SetEndDate(end_date.year, end_date.month, end_date.day)  # (2022, 1, 1)  # Set End Date
        self.SetCash(100000)  # Set Strategy Cash

        length = 30
        self.symbol = self.AddEquity(trade_symbol, Resolution.Hour).Symbol
        self.bb = self.BB(self.symbol, length, 2, MovingAverageType.Simple, Resolution.Daily)
        self.rsi = self.RSI(self.symbol, length, resolution=Resolution.Daily)
        # self.sma = self.SMA(self.spy, length, Resolution.Daily)
        # History warm up for shortcut helper BollingerBand & SMA indicator
        self.WarmUpIndicator(self.symbol, self.bb)
        self.WarmUpIndicator(self.symbol, self.rsi)
        # long method to warm the indicator
        # closing_prices = self.History(self.spy, length, Resolution.Hour)["close"]
        # for time, price in closing_prices.loc[self.spy].items():
        #    self.bb.Update(time, price)
        # self.sma.Update(time, price)

        self.SetBenchmark(self.benchmark_symbol)
        self.initialPortfolioValue = self.Portfolio.TotalPortfolioValue
        self.initialBenchmarkPrice = None

        self.df_order_plot = pd.DataFrame(columns=['Time',
                                                   'OrderID', 'Symbol',
                                                   'Status', 'Quantity',
                                                   'FillQuantity', 'FillPrice',
                                                   'OrderFee'])
        self.df_timeseries = pd.DataFrame(columns=['Time', 'Price', 'bb-MiddleBand',
                                                   'bb-UpperBand', 'bb-LowerBand',
                                                   'Benchmark'])

        stockPlot = Chart('Trade Plot')
        stockPlot.AddSeries(Series('Buy', SeriesType.Scatter, '$',
                                   Color.Green, ScatterMarkerSymbol.Triangle))
        stockPlot.AddSeries(Series('Sell', SeriesType.Scatter, '$',
                                   Color.Red, ScatterMarkerSymbol.TriangleDown))
        stockPlot.AddSeries(Series('Liquidate', SeriesType.Scatter, '$',
                                   Color.Blue, ScatterMarkerSymbol.Diamond))
        self.AddChart(stockPlot)
        returnPlot = Chart('Cumulative Return Comparison')
        self.AddChart(returnPlot)

    def OnData(self, slice: Slice):
        """OnData event is the primary entry point for your algorithm.
            Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        """
        if not self.bb.IsReady:
            return

        # if slice.ContainsKey(self.symbol) and slice[self.symbol] is not None:
        if not slice.ContainsKey(self.symbol) or slice[self.symbol] is None:
            return

        # data = slice[self.spy]
        price = slice[self.symbol].Price
        # sym_obj = slice[self.symbol]
        # self.Debug(f'Symbol: {sym_obj.Symbol}, Time: {sym_obj.Time}, Price:{sym_obj.Price}, '
        #           f'Open: {sym_obj.Open}, High: {sym_obj.High}, '
        #           f'Low: {sym_obj.Low}, Close: {sym_obj.Close}')
        # self.Debug(f'{self.Time}, {price},'
        #            f'{self.bb.MiddleBand.Current.Value}, {self.bb.UpperBand.Current.Value},'
        #            f'{self.bb.LowerBand.Current.Value},'
        #            f'{self.Benchmark.Evaluate(self.Time)}')

        self.Plot("Trade Plot", "Price", price)
        self.Plot("Trade Plot", "bb-MiddleBand", self.bb.MiddleBand.Current.Value)
        self.Plot("Trade Plot", "bb-UpperBand", self.bb.UpperBand.Current.Value)
        self.Plot("Trade Plot", "bb-LowerBand", self.bb.LowerBand.Current.Value)
        self.Plot("Trade Plot", "Benchmark", self.Benchmark.Evaluate(self.Time))
        # self.Plot("Trade Plot", "SMA", self.sma.Current.Value)
        self.df_timeseries.loc[len(self.df_timeseries)] = [self.Time,price,
                                                           self.bb.MiddleBand.Current.Value,
                                                           self.bb.UpperBand.Current.Value,
                                                           self.bb.LowerBand.Current.Value,
                                                           self.Benchmark.Evaluate(self.Time)]

        currentBenchmarkPrice = self.Benchmark.Evaluate(self.Time)
        if self.initialBenchmarkPrice is None:
            self.initialBenchmarkPrice = currentBenchmarkPrice
        benchmarkReturn = (currentBenchmarkPrice / self.initialBenchmarkPrice) - 1
        self.Plot("Cumulative Return Comparison", "Benchmark Return", benchmarkReturn)
        strategyReturn = (self.Portfolio.TotalPortfolioValue / self.initialPortfolioValue) - 1
        self.Plot("Cumulative Return Comparison", "Strategy Return", strategyReturn)

        # The current value of self.rsi is represented by self.rsi.Current.Value
        # self.Plot("RSI Plot", "rsi", self.rsi.Current.Value)
        # Plot all attributes of self.rsi
        # self.Plot("RSI Plot", "rsi-averageloss", self.rsi.AverageLoss.Current.Value)
        # self.Plot("RSI Plot", "rsi-averagegain", self.rsi.AverageGain.Current.Value)

        if self.Portfolio.Invested == False:
            if price < self.bb.LowerBand.Current.Value and self.rsi.Current.Value < 30:
                self.SetHoldings(self.symbol, 1)
                self.Plot("Trade Plot", "Buy", price)
            elif price > self.bb.UpperBand.Current.Value and self.rsi.Current.Value > 70:
                self.SetHoldings(self.symbol, -1)
                self.Plot("Trade Plot", "Sell", price)
        else:
            if self.Portfolio[self.symbol].IsLong:
                # if price > self.bb.MiddleBand.Current.Value and self.rsi.Current.Value > 50:
                if price > self.bb.UpperBand.Current.Value:
                    self.Liquidate()
                    self.Plot("Trade Plot", "Liquidate", price)
            # elif price < self.bb.MiddleBand.Current.Value and self.rsi.Current.Value < 50:
            elif price < self.bb.LowerBand.Current.Value:
                self.Liquidate()
                self.Plot("Trade Plot", "Liquidate", price)

    def OnOrderEvent(self, order_event: OrderEvent) -> None:
        order = self.Transactions.GetOrderById(order_event.OrderId)
        if order_event.Status == OrderStatus.Filled:
            # self.Debug(f"Order filled: {orderEvent.Symbol}")
            self.Debug(f"order.Type: {order.Type} OrderEvent: {order_event}")
            self.df_order_plot.loc[len(self.df_order_plot)] = [self.Time,
                                                               order_event.OrderId,
                                                               order_event.Symbol,
                                                               order_event.Status,
                                                               order_event.Quantity,
                                                               order_event.FillQuantity,
                                                               order_event.FillPrice,
                                                               order_event.OrderFee
                                                               ]

    def OnEndOfAlgorithm(self) -> None:
        self.df_order_plot.to_csv(f'{LEAN_RESULTS_DIR}/df_order_plot.csv')
        self.df_timeseries.to_csv(f'{LEAN_RESULTS_DIR}/df_timeseries.csv')
        #self.Log(self.df_timeseries)
        self.Debug("Algorithm done")
