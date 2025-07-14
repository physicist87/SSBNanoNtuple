import os
import shutil
import argparse
import socket # socket 

def create_crab_config(sub_dir, short_name, input_dataset, run_period, file_type, user_id, work_name):
    """
    Create a CRAB configuration file for Data or MC in the specified directory.
    """
    is_data = file_type == "Data"

    lumi_mask_urls = {
        "2016": "https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions16/13TeV/Legacy_2016/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt",
        "2017": "https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt",
        "2018": "https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt"
    }

    lumi_mask = lumi_mask_urls.get(run_period[:4], "Unknown") if is_data else ""
    splitting = "LumiBased" if is_data else "FileBased"
    units_per_job = 10 if is_data else 1
    branchlist_file = f"branchlist_Run2_{file_type}.txt"
    # Include WorkName in the output directory path
    out_lfn_dir = f"/store/user/{user_id}/UL20NanoAOD/{work_name}/{run_period}/{file_type}/"

    # --- Add server detection logic ---
    hostname = socket.gethostname()
    hostname_lower = hostname.lower()

    if "sdfarm.kr" in hostname_lower or "ui10" in hostname_lower: # KISTI server detection based on hostname
        storage_site = "T3_KR_KISTI"
        print(f"Detected KISTI server ({hostname}). Setting storage site to {storage_site}")
    elif "knu.ac.kr" in hostname_lower or "knu" in hostname_lower: # KNU server detection based on hostname
        storage_site = "T3_KR_KNU"
        print(f"Detected KNU server ({hostname}). Setting storage site to {storage_site}")
    else: # Default or unknown server
        storage_site = "T3_KR_KNU" # You might want to make this configurable or raise an error for unknown
        print(f"Detected unknown server ({hostname}). Defaulting storage site to {storage_site}. Please verify if this is correct.")
    # --- End of server detection logic ---

    config_content = f"""from WMCore.Configuration import Configuration

config = Configuration()

config.section_("General")
config.General.requestName = '{short_name}'  # short name
config.General.transferLogs = True

config.section_("JobType")
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'PSet.py'
config.JobType.scriptExe = 'crab_script.sh'
config.JobType.inputFiles = ['crab_script.py', '{branchlist_file}']

config.section_("Data")
config.Data.inputDataset = '{input_dataset}'
config.Data.inputDBS = 'global'
config.Data.splitting = '{splitting}'
{"config.Data.lumiMask = '" + lumi_mask + "'" if is_data else ""}
config.Data.unitsPerJob = {units_per_job}
config.Data.outLFNDirBase = '{out_lfn_dir}'
config.Data.publication = False
config.Data.outputDatasetTag = '{short_name}'  # short name

config.section_("Site")
config.Site.storageSite = "{storage_site}" # Use dynamically determined storage_site
"""
    config_file_path = os.path.join(sub_dir, "crab_config.py")
    with open(config_file_path, 'w') as f:
        f.write(config_content)
    print(f"Created CRAB config file: {config_file_path}")

def copy_support_files(sub_dir, file_type):
    """
    Copy support files (crab_script.sh, PSet.py, crab_script.py, and branchlist).
    """
    support_files = ["crab_script.sh", "PSet.py"]
    branchlist_file = f"BranchList/branchlist_Run2_{file_type}.txt"

    # Dynamically modify and copy crab_script.py
    crab_script_src = "crab_script.py"
    crab_script_dst = os.path.join(sub_dir, "crab_script.py")

    with open(crab_script_src, 'r') as src_file:
        content = src_file.read()

    # Replace 'branchlist.txt' with the dynamic branchlist file name
    content = content.replace("branchlist.txt", os.path.basename(branchlist_file))

    with open(crab_script_dst, 'w') as dst_file:
        dst_file.write(content)

    print(f"Modified and copied {crab_script_src} to {crab_script_dst}")

    # Copy other support files
    for file in support_files:
        src = file
        dst = os.path.join(sub_dir, os.path.basename(file))
        shutil.copy(src, dst)
        print(f"Copied {src} to {dst}")

    # Copy the branchlist file with its original name
    branchlist_dst = os.path.join(sub_dir, f"branchlist_Run2_{file_type}.txt")
    shutil.copy(branchlist_file, branchlist_dst)
    print(f"Copied {branchlist_file} to {branchlist_dst}")

def process_file(file_path, work_name, user_id):
    """
    Process the input file and create CRAB configuration files.
    """
    file_name = os.path.basename(file_path)
    run_period = determine_run_period(file_name)

    is_data = "Data" in file_name or "DATA" in file_name
    base_dir = os.path.join(work_name, run_period, "Data" if is_data else "MC")
    file_type = "Data" if is_data else "MC"

    os.makedirs(base_dir, exist_ok=True)

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                columns = line.split(',')
                short_name = columns[0].strip()
                input_dataset = columns[1].strip()
                sub_dir = os.path.join(base_dir, short_name)
                os.makedirs(sub_dir, exist_ok=True)
                create_crab_config(sub_dir, short_name, input_dataset, run_period, file_type, user_id, work_name)
                copy_support_files(sub_dir, file_type)

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
    parser = argparse.ArgumentParser(description="Generate CRAB config files.")
    parser.add_argument("--inputList", required=True, help="Path to the input list file")
    parser.add_argument("--WorkName", required=True, help="Working directory name")
    parser.add_argument("--UserID", required=True, help="User ID for output directory")

    args = parser.parse_args()

    input_file = args.inputList
    work_name = args.WorkName
    user_id = args.UserID

    if not os.path.exists(work_name):
        os.makedirs(work_name)
        print(f"Created working directory: {work_name}")

    process_file(input_file, work_name, user_id)
