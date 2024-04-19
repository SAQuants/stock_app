import os
import subprocess
import json
import re
import pandas as pd

lean_base_dir = 'lean_base/'
strategy_config_file = '/strategy_config/sconfig.json'


def get_lean_pathname():
    # print(f'CONDA_PREFIX:{os.getenv("CONDA_PREFIX")}, CONDA_DEFAULT_ENV:{os.getenv("CONDA_DEFAULT_ENV")}')
    lean_pathname = os.getenv('LEAN_PATH', '')
    print(f'LEAN_PATH: {lean_pathname}')
    if os.path.isfile(lean_pathname):
        return lean_pathname
    else:
        print(f'lean NOT installed')
        return None


def update_lean_json(lean_config_file, trade_symbol, start_date, end_date, benchmark_symbol):
    with open(lean_config_file, "r") as file_obj:  # Open the JSON file for reading
        json_data = json.load(file_obj)  # Read the JSON into the buffer
        file_obj.close()  # Close the JSON file
    json_data["trade_symbol"] = trade_symbol
    json_data["start_date"] = start_date
    json_data["end_date"] = end_date
    json_data["benchmark_symbol"] = benchmark_symbol
    with open(lean_config_file, "w") as file_obj:  # Open the JSON file for reading
        json.dump(json_data, file_obj, indent=4)  # Write the JSON into the buffer
        file_obj.close()  # Close the JSON file


def execute_backtest(trade_symbol="SPY",
                     backtest_name ="strategy_bb_rsi",
                     start_date="2022-06-01", end_date="2023-01-01",
                     benchmark_symbol="SPY"):
    print(f'execute_backtest::getcwd() {os.getcwd()}')

    lean_pathname = get_lean_pathname()
    if lean_pathname is None:
        return {"status": 418,
                "trade_symbol": trade_symbol,
                "backtest_name": backtest_name,
                "start_date": start_date,
                "end_date": end_date,
                "benchmark_symbol": benchmark_symbol,
                "backtest_result": "Lean not installed"
                }
    ## Uncomment after Testing -BEGIN##
    strategy_config_file_path = lean_base_dir + backtest_name + strategy_config_file
    update_lean_json(strategy_config_file_path, trade_symbol, start_date, end_date, benchmark_symbol)
    args = [lean_pathname, 'backtest', backtest_name]
    result = subprocess.run(args,
                            cwd=lean_base_dir,
                            capture_output=True,
                            text=True)
    print(f'args={result.args}, '
          f'return code={result.returncode}, '
          f'stdout={result.stdout}, '
          f'stderr={result.stderr}')

    output_dir = re.findall('/backtests/(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})*', result.stdout)
    output_dir = lean_base_dir + backtest_name + '/backtests/' + output_dir[0] + '/'
    ## Uncomment after Testing -END##
    ## Comment after Testing -BEGIN##
    # output_dir = lean_base_dir + backtest_name + '/backtests/' + 'aapl_example/'
    ## Comment after Testing -BEGIN##
    # order_plot_path = output_dir + 'df_order_plot.csv'
    # df_order_plot = pd.read_csv(order_plot_path)
    # print(df_order_plot)

    order_plot_path = output_dir + '/df_order_plot.csv'
    df_op = pd.read_csv(order_plot_path)
    df_op.set_index('Time', inplace=True)
    timeseries_path = output_dir + '/df_timeseries.csv'
    df_ts = pd.read_csv(timeseries_path)
    df_ts.set_index('Time', inplace=True)
    df_res = pd.concat([df_ts,df_op], axis=1)
    df_res.drop(columns=['OrderID', 'Status', 'Quantity', 'OrderFee', 'FillPrice'], inplace=True)
    df_res.reset_index(inplace=True)
    df_res.to_csv(output_dir + '/df_results.csv')


    return {"status": 200,
            "trade_symbol": trade_symbol,
            "backtest_name": backtest_name,
            "start_date": start_date,
            "end_date": end_date,
            "benchmark_symbol": benchmark_symbol,
            "output_dir": output_dir,
            "df_order_plot": df_res.to_json(orient="records")
            }


if __name__ == "__main__":
    # print(os.getcwd())
    backtest_name = "strategy_bb_rsi"
    result = execute_backtest("IBM", backtest_name,
                              "2019-06-01", "2021-01-01", "SPY")
    print(f'backtest_result output_dir: {result["output_dir"]}')
    print(f'result: {result}')
