import os
import argparse
import subprocess

def check_voms_proxy():
    """
    Check if a valid VOMS proxy exists. If not, attempt to generate one.
    """
    try:
        result = subprocess.run(["voms-proxy-info", "--timeleft"], check=True, capture_output=True, text=True)
        time_left = int(result.stdout.strip())
        if time_left > 0:
            print(f"VOMS proxy is valid. Time left: {time_left} seconds.")
        else:
            raise ValueError("VOMS proxy expired.")
    except (subprocess.CalledProcessError, ValueError):
        print("VOMS proxy is missing or expired. Attempting to generate a new one...")
        try:
            subprocess.run(["voms-proxy-init", "--voms", "cms"], check=True)
            print("VOMS proxy successfully created.")
        except subprocess.CalledProcessError:
            print("Error: Failed to generate VOMS proxy. Please run 'voms-proxy-init' manually.")
            exit(1)

def execute_crab_command(base_dir, command, log_file):
    """
    Navigate to each directory and execute the specified CRAB command.
    """
    if not os.path.exists(base_dir):
        print(f"Error: Directory {base_dir} does not exist!")
        return
    
    original_dir = os.getcwd()  # Save the original directory
    
    with open(log_file, "a") as log:
        for root, dirs, files in os.walk(base_dir):
            if command == "submit" and "crab_config.py" in files:
                crab_dirs = [d for d in dirs if d.startswith("crab_")]
                if crab_dirs:
                    print(f"CRAB working directory already exists in {root}. Skipping submission.")
                    continue
                try:
                    os.chdir(root)
                    print(f"Executing 'crab submit' in directory: {root}")
                    result = subprocess.run(["crab", "submit", "-c", "crab_config.py"], check=True, capture_output=True, text=True)
                    log.write(result.stdout + "\n" + result.stderr + "\n")
                except subprocess.CalledProcessError as e:
                    log.write(f"Error executing 'crab submit' in {root}: {e.stderr}\n")
                finally:
                    os.chdir(original_dir)
            elif command == "status" or command == "resubmit":
                crab_dirs = [d for d in dirs if d.startswith("crab_")]
                for crab_dir in crab_dirs:
                    crab_dir_path = os.path.join(root, crab_dir)
                    print(f"Checking status for CRAB directory: {crab_dir_path}")
                    try:
                        result = subprocess.run(["crab", "status", "-d", crab_dir_path], check=True, capture_output=True, text=True)
                        log.write(result.stdout + "\n" + result.stderr + "\n")
                        if "FAILED" in result.stdout or "FAILED" in result.stderr:
                            print(f"Resubmitting failed job in {crab_dir_path}")
                            subprocess.run(["crab", "resubmit", "-d", crab_dir_path], check=True)
                    except subprocess.CalledProcessError as e:
                        log.write(f"Error executing 'crab status' in {crab_dir_path}: {e.stderr}\n")

def process_input_list(input_list, work_name, crab_command, log_file):
    """
    Process the input list to determine the base directories and execute CRAB commands.
    """
    file_name = os.path.basename(input_list)
    run_period = determine_run_period(file_name)
    is_data = "Data" in file_name or "DATA" in file_name
    base_dir = os.path.join(work_name, run_period, "Data" if is_data else "MC")
    execute_crab_command(base_dir, crab_command, log_file)

def determine_run_period(file_name):
    """
    Determine the Run Period from the file name.
    """
    if "2016PreVFP" in file_name:
        return "2016PreVFP"
    elif "2016PostVFP" in file_name:
        return "2016PostVFP"
    elif "2017" in file_name:
        return "2017"
    elif "2018" in file_name:
        return "2018"
    elif "2022" in file_name:
        return "2022"
    else:
        return "Unknown"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-submit, check, or resubmit CRAB jobs.")
    parser.add_argument("--inputList", required=True, help="Path to the input list file")
    parser.add_argument("--WorkName", required=True, help="Working directory name")
    parser.add_argument("--crabCommand", required=True, choices=["submit", "status", "resubmit"], help="CRAB command to execute")
    parser.add_argument("--logFile", default="log.txt", help="Log file to save output")
    
    args = parser.parse_args()
    input_list = args.inputList
    work_name = args.WorkName
    crab_command = args.crabCommand
    log_file = args.logFile
    
    check_voms_proxy()
    process_input_list(input_list, work_name, crab_command, log_file)

