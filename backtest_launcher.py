import os
import subprocess
import json
import re

lean_base_dir = 'lean_base/'
strategy_config_file = '/strategy_config/sconfig.json'


def get_lean_pathname():
    # print(f'CONDA_PREFIX:{os.getenv("CONDA_PREFIX")}, CONDA_DEFAULT_ENV:{os.getenv("CONDA_DEFAULT_ENV")}')
    lean_pathname = os.getenv('LEAN_PATH', '')
    if os.path.isfile(lean_pathname):
        print(f'lean installed: {lean_pathname}')
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


def execute_backtest(backtest_name,
                     trade_symbol="SPY", start_date="20220601",
                     end_date="20230101", benchmark_symbol="SPY"):
    lean_pathname = get_lean_pathname()
    if lean_pathname is None:
        return {"trade_symbol": trade_symbol,
                "backtest_name": backtest_name,
                "benchmark_symbol": benchmark_symbol,
                "backtest_result": "Lean not installed"}
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
    return {"symbol": trade_symbol, "backtest_name": backtest_name, "backtest_result": result.stdout}
    pass


if __name__ == "__main__":
    strategy = "strategy_bb_rsi"
    result = execute_backtest(strategy, "IBM",
                              "20180601", "20210101", "SPY")
    output_dir = re.findall('/backtests/(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})*', result['backtest_result'])
    output_path = lean_base_dir + strategy + '/backtests/' + output_dir[0] + '/'
    print(f'backtest_result location: {output_path}')
