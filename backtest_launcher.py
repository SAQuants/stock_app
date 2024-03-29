import os
import subprocess
import json
import sys

base_dir = 'lean_base/'
lean_config = 'lean.json'


def get_lean_pathname():
    #print(f'CONDA_PREFIX:{os.getenv("CONDA_PREFIX")}, CONDA_DEFAULT_ENV:{os.getenv("CONDA_DEFAULT_ENV")}')
    lean_pathname = os.getenv('LEAN_PATH','')
    if os.path.isfile(lean_pathname):
        print(f'lean installed: {lean_pathname}')
        return lean_pathname
    else:
        print(f'lean NOT installed')
        return None


def update_lean_json(lean_config_file, symbol, start_date, end_date):
    with open(lean_config_file, "r") as file_obj:  # Open the JSON file for reading
        json_data = json.load(file_obj)  # Read the JSON into the buffer
        file_obj.close()  # Close the JSON file
    json_data["symbol"] = symbol
    json_data["start_date"] = start_date
    json_data["end_date"] = end_date
    with open(lean_config_file, "w") as file_obj: # Open the JSON file for reading
        json.dump(json_data, file_obj, indent=2)  # Write the JSON into the buffer
        file_obj.close()  # Close the JSON file

def execute_backtest(backtest_name, symbol="SPY", start_date="20220601", end_date="20230101"):
    lean_pathname = get_lean_pathname()
    if lean_pathname is None:
        return {"symbol": symbol,
                "backtest_name": backtest_name,
                "backtest_result": "Lean not installed"}
    lean_config_file = base_dir + lean_config
    update_lean_json(lean_config_file, symbol, start_date, end_date)
    args = [lean_pathname, 'backtest', backtest_name]
    result = subprocess.run(args,
                            cwd=base_dir,
                            env={"symbol": symbol, "start_date": start_date, "end_date": end_date},
                            capture_output=True,
                            text=True)
    print(f'args={result.args}, '
          f'return code={result.returncode}, '
          f'stdout={result.stdout}, '
          f'stderr={result.stderr}')
    return {"symbol": symbol, "backtest_name": backtest_name, "backtest_result": result.stdout}
    pass


if __name__ == "__main__":
    # print(sys.path)
    #for k, v in os.environ.items():
    #    print("{0}: {1}".format(k, v))
    execute_backtest("strategy_bb_rsi", "AAPL", "20190101", "20210101")
