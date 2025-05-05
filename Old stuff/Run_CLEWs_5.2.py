import subprocess
import os
import argparse
from datetime import datetime

def log_with_timestamp(message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def main(input_file, solver):
    # Derive other filenames based on the input file
    base_name = os.path.splitext(input_file)[0]
    preprocessed_file = f'{base_name}_preprocessed.txt'
    converted_file = f'{base_name}_converted.txt'
    lp_file = 'model.lp'
    solution_file = f'{base_name}.sol'
    results_dir = 'results'
    csv_output_dir = 'data/'
    config_file = 'config_com.yaml'

    # Define the commands with solver-specific commands
    commands = [
        f'otoole convert datafile csv {input_file} {base_name} {config_file}',
        f'otoole convert csv datafile {base_name} {converted_file} {config_file}',
        f'python preprocess_data.py otoole {converted_file} {preprocessed_file}',
        f'glpsol -d {preprocessed_file} -m model.v.5.2.txt --wlp {lp_file} --check'
    ]
    
    if solver == 'cplex':
        solve_command = f'cplex -c "read {lp_file}" "optimize" "write {solution_file}"'
    elif solver == 'gurobi':
        solve_command = f'gurobi_cl ResultFile={solution_file} {lp_file}'
    elif solver == 'glpk':
        solve_command = f'glpsol -m {lp_file} -o {solution_file}'
    elif solver == 'cbc':
        solve_command = f'cbc {lp_file} solve solu {solution_file}'
    else:
        raise ValueError(f"Unsupported solver: {solver}")

    commands.append(solve_command)
    commands.append(f'otoole results {solver} csv {solution_file} {results_dir} csv {base_name} {config_file}')

    for command in commands:
        log_with_timestamp(f"Starting command: {command}")
        start_time = datetime.now()

        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        end_time = datetime.now()
        duration = end_time - start_time
        log_with_timestamp(f"Command finished: {command} (Duration: {duration})")
        
        if result.returncode != 0:
            log_with_timestamp(f"Command failed: {command}")
            log_with_timestamp(f"Error: {result.stderr}")
            break
        else:
            log_with_timestamp(f"Command succeeded: {command}")
            log_with_timestamp(f"Output: {result.stdout}")
        
    
    # Cleanup: Delete generated files except the results folder
    # files_to_cleanup = [converted_file, preprocessed_file, lp_file, solution_file]
    # for file in files_to_cleanup:
    #     if os.path.exists(file):
    #         try:
    #             os.remove(file)
    #             log_with_timestamp(f"Deleted generated file: {file}")
    #         except Exception as e:
    #             log_with_timestamp(f"Error deleting file {file}: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a series of commands with dynamic inputs based on the provided input file and solver.')
    parser.add_argument('input_file', type=str, help='The input file for preprocessing.')
    parser.add_argument('solver', type=str, choices=['cplex', 'gurobi', 'glpk', 'cbc'], help='The solver to use (cplex, gurobi, glpk, or cbc).')
    args = parser.parse_args()
    main(args.input_file, args.solver)