# region imports
from AlgorithmImports import *
from datetime import datetime
import json

LEAN_RESULTS_DIR = '/Results'
LEAN_BASE_DIR = '/LeanCLI/'


# endregion

class SpyBB(QCAlgorithm):

    def initialize(self):

        # self.log(f'getcwd: {os.getcwd()}')
        # dir_obj = os.scandir('/')
        # sub_dir = [ files.name for files in dir_obj if files.is_dir()]
        # self.log(f'Initialize scandir(/) results:\n {sub_dir}')
        # for current_path, folders, files in os.walk('/LeanCLI'):
        #    self.log(f'current_path, folders, files\n '
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
            self.log(f'reading {strategy_config}')
            json_obj = json.load(file)
            self.log(json.dumps(json_obj, indent=4))
            start_date_str = json_obj["start_date"] if "start_date" in json_obj else start_date_str
            end_date_str = json_obj["end_date"] if "end_date" in json_obj else end_date_str
            trade_symbol = json_obj["trade_symbol"] if "trade_symbol" in json_obj else trade_symbol
            self.benchmark_symbol = json_obj[
                "benchmark_symbol"] if "benchmark_symbol" in json_obj else self.benchmark_symbol

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        self.log(f"Environment Info: "
                 f"start_date={start_date},end_date={end_date},trade_symbol={trade_symbol},"
                 f"benchmark_symbol={self.benchmark_symbol}")

        self.set_start_date(start_date.year, start_date.month, start_date.day)
        self.set_end_date(end_date.year, end_date.month, end_date.day)  # (2022, 1, 1)  # Set End Date
        self.set_cash(100000)  # Set Strategy Cash

        length = 30
        self.symbol = self.add_equity(trade_symbol, Resolution.HOUR).symbol
        self.bb_ = self.bb(self.symbol, length, 2, MovingAverageType.SIMPLE, Resolution.DAILY)
        self.rsi_ = self.rsi(self.symbol, length, resolution=Resolution.DAILY)
        # self.sma = self.SMA(self.spy, length, Resolution.Daily)
        # History warm up for shortcut helper BollingerBand & SMA indicator
        self.warm_up_indicator(self.symbol, self.bb_)
        self.warm_up_indicator(self.symbol, self.rsi_)
        # long method to warm the indicator
        # closing_prices = self.History(self.spy, length, Resolution.Hour)["close"]
        # for time, price in closing_prices.loc[self.spy].items():
        #    self.bb_.Update(time, price)
        # self.sma.Update(time, price)

        self.set_benchmark(self.benchmark_symbol)
        self.initial_portfolio_value = self.portfolio.total_portfolio_value
        self.initial_benchmark_price = None

        # Schedule an event to fire at the end of each trading day
        self.schedule.on(self.date_rules.every_day(trade_symbol),
                         self.time_rules.before_market_close(trade_symbol),
                         self.get_eod_stats)

        self.df_order_plot = pd.DataFrame(columns=['Time',
                                                   'OrderID', 'Symbol',
                                                   'Status', 'Quantity',
                                                   'FillQuantity', 'FillPrice',
                                                   'OrderFee'])
        self.df_timeseries = pd.DataFrame(columns=['Time', 'Price', 'bb-MiddleBand',
                                                   'bb-UpperBand', 'bb-LowerBand',
                                                   'Benchmark'])

        stock_plot = Chart('Trade Plot')
        stock_plot.add_series(Series('Buy', SeriesType.SCATTER, '$',
                                     Color.GREEN, ScatterMarkerSymbol.TRIANGLE))
        stock_plot.add_series(Series('Sell', SeriesType.SCATTER, '$',
                                     Color.RED, ScatterMarkerSymbol.TRIANGLE_DOWN))
        stock_plot.add_series(Series('Liquidate', SeriesType.SCATTER, '$',
                                     Color.BLUE, ScatterMarkerSymbol.DIAMOND))
        self.add_chart(stock_plot)
        returnPlot = Chart('Cumulative Return Comparison')
        self.add_chart(returnPlot)

    def on_data(self, slice: Slice):
        """OnData event is the primary entry point for your algorithm.
            Each new data point will be pumped in here.
            Arguments:
                slice: Slice object keyed by symbol containing the stock data
        """
        if not self.bb_.IsReady:
            return

        # if slice.ContainsKey(self.symbol) and slice[self.symbol] is not None:
        if not slice.ContainsKey(self.symbol) or slice[self.symbol] is None:
            return

        # data = slice[self.spy]
        price = slice[self.symbol].Price
        # sym_obj = slice[self.symbol]
        # self.debug(f'Symbol: {sym_obj.Symbol}, Time: {sym_obj.Time}, Price:{sym_obj.Price}, '
        #           f'Open: {sym_obj.Open}, High: {sym_obj.High}, '
        #           f'Low: {sym_obj.Low}, Close: {sym_obj.Close}')
        # self.debug(f'{self.Time}, {price},'
        #            f'{self.bb_.MiddleBand.Current.Value}, {self.bb_.UpperBand.Current.Value},'
        #            f'{self.bb_.LowerBand.Current.Value},'
        #            f'{self.Benchmark.Evaluate(self.Time)}')

        self.plot("Trade Plot", "Price", price)
        self.plot("Trade Plot", "bb-MiddleBand", self.bb_.MiddleBand.Current.Value)
        self.plot("Trade Plot", "bb-UpperBand", self.bb_.UpperBand.Current.Value)
        self.plot("Trade Plot", "bb-LowerBand", self.bb_.LowerBand.Current.Value)
        self.plot("Trade Plot", "Benchmark", self.benchmark.evaluate(self.time))
        # self.Plot("Trade Plot", "SMA", self.sma.Current.Value)
        self.df_timeseries.loc[len(self.df_timeseries)] = [self.time, price,
                                                           self.bb_.MiddleBand.Current.Value,
                                                           self.bb_.UpperBand.Current.Value,
                                                           self.bb_.LowerBand.Current.Value,
                                                           self.benchmark.evaluate(self.time)]

        current_benchmark_price = self.benchmark.evaluate(self.time)
        if self.initial_benchmark_price is None:
            self.initial_benchmark_price = current_benchmark_price
        benchmark_return = (current_benchmark_price / self.initial_benchmark_price) - 1
        self.plot("Cumulative Return Comparison", "Benchmark Return", benchmark_return)
        strategy_return = (self.portfolio.total_portfolio_value / self.initial_portfolio_value) - 1
        self.plot("Cumulative Return Comparison", "Strategy Return", strategy_return)

        # The current value of self.rsi_ is represented by self.rsi_.Current.Value
        # self.Plot("RSI Plot", "rsi", self.rsi_.Current.Value)
        # Plot all attributes of self.rsi_
        # self.Plot("RSI Plot", "rsi-averageloss", self.rsi_.AverageLoss.Current.Value)
        # self.Plot("RSI Plot", "rsi-averagegain", self.rsi_.AverageGain.Current.Value)

        if self.portfolio.invested == False:
            if price < self.bb_.LowerBand.Current.Value and self.rsi_.Current.Value < 30:
                self.set_holdings(self.symbol, 1)
                self.plot("Trade Plot", "Buy", price)
            elif price > self.bb_.UpperBand.Current.Value and self.rsi_.Current.Value > 70:
                self.set_holdings(self.symbol, -1)
                self.plot("Trade Plot", "Sell", price)
        else:
            if self.portfolio[self.symbol].is_long:
                # if price > self.bb_.MiddleBand.Current.Value and self.rsi_.Current.Value > 50:
                if price > self.bb_.UpperBand.Current.Value:
                    self.liquidate()
                    self.plot("Trade Plot", "Liquidate", price)
            # elif price < self.bb_.MiddleBand.Current.Value and self.rsi_.Current.Value < 50:
            elif price < self.bb_.LowerBand.Current.Value:
                self.liquidate()
                self.plot("Trade Plot", "Liquidate", price)

    def on_order_event(self, order_event: OrderEvent) -> None:
        order = self.transactions.get_order_by_id(order_event.order_id)
        if order_event.status == OrderStatus.FILLED:
            # self.debug(f"Order filled: {orderEvent.Symbol}")
            self.debug(f"order.Type: {order.type} OrderEvent: {order_event}")
            self.df_order_plot.loc[len(self.df_order_plot)] = [self.time,
                                                               order_event.order_id,
                                                               order_event.symbol,
                                                               order_event.status,
                                                               order_event.quantity,
                                                               order_event.fill_quantity,
                                                               order_event.fill_price,
                                                               order_event.order_fee
                                                               ]

    def on_end_of_algorithm(self) -> None:
        self.df_order_plot.to_csv(f'{LEAN_RESULTS_DIR}/df_order_plot.csv', index=False)
        self.df_timeseries.to_csv(f'{LEAN_RESULTS_DIR}/df_timeseries.csv', index=False)
        #self.log(self.df_timeseries)
        self.debug("Algorithm done")

    def get_eod_stats(self):
        # log the total equity, realized and unrealized profit
        self.debug(f"Time: {self.time}, "
                   f"total_profit: {self.portfolio.total_profit}, "
                   f"total_net_profit: {self.portfolio.total_net_profit}, "
                   f"Total total_portfolio_value: {self.portfolio.total_portfolio_value}, "
                   f"Unrealized Profit: {self.portfolio.total_unrealised_profit}, "
                   f"TotalFees: {self.portfolio.total_fees}, "
                   f"Cash: {self.portfolio.cash}"
                   )
