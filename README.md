# SSBNanoNtuple

This repository contains scripts and configurations for working with NanoAOD files in the CMS software framework. The following instructions describe how to set up the environment, execute the `script.py`, and generate necessary directories and configuration files.

---

## **Installation Instructions**

### **1. Load CMS Environment**
Load the CMS default environment:
```bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
```

### **2. Check CMSSW Compatibility**
Verify the compatibility of your gcc version with the desired CMSSW version:
```bash
scram list CMSSW_13_3_0
```

### **3. Set Architecture**
Set the appropriate architecture for your system:
- **For KNU**:
  ```bash
  export SCRAM_ARCH=slc7_amd64_gcc12
  ```
- **For lxplus or KISTI**:
  ```bash
  export SCRAM_ARCH=el9_amd64_gcc12
  ```

### **4. Create and Initialize CMSSW Environment**
Create a new CMSSW release area and navigate to the `src` directory:
```bash
cmsrel CMSSW_13_3_0
cd CMSSW_13_3_0/src/
cmsenv
```

### **5. Initialize Git for CMS**
Initialize the CMS Git environment:
```bash
git cms-init
```

### **6. Add the Necessary CMS Package**
Add the `PhysicsTools/NanoAODTools` package to your environment:
```bash
git cms-addpkg PhysicsTools/NanoAODTools
```

### **7. Clone the SSBNanoNtuple Repository**
Clone this repository into the appropriate directory:
```bash
cd PhysicsTools/NanoAODTools
git clone https://github.com/physicist87/SSBNanoNtuple.git -b Production_v1
```

---

## **Usage Instructions**

### **1. Running `script.py`**
Use the `script.py` to generate directory structures, configuration files, and copy support files for CRAB submission.

#### **Basic Command**
```bash
python3 script.py --inputList DataAndMCList/UL2016PreVFP_MC_Test.txt --WorkName TestV1 --UserID sha 
```

- **Options:**
  - `--inputList`: Path to the file containing the NanoAOD dataset list.
  - `--WorkName`: Name of the working directory.
  - `--UserID`: Your user ID for output paths.

#### **Example Input List File**
A sample `DataAndMCList/UL2016PreVFP_MC_Test.txt` file:
```plaintext
TTTo2L2Nu_TuneCP5_powheg, /TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL16NanoAODAPVv9-106X_mcRun2_asymptotic_preVFP_v11-v1/NANOAODSIM
TTToHadronic_TuneCP5_powheg, /TTToHadronic_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL16NanoAODAPVv9-106X_mcRun2_asymptotic_preVFP_v11-v1/NANOAODSIM
TTToSemiLeptonic_TuneCP5_powheg, /TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL16NanoAODAPVv9-106X_mcRun2_asymptotic_preVFP_v11-v1/NANOAODSIM
```

#### **Results**
- The script will create a directory structure like this:
  ```plaintext
  TestV1/
    ├── 2016PreVFP/
    │   ├── MC/
    │   │   ├── TTTo2L2Nu_TuneCP5_powheg/
    │   │   │   ├── crab_config.py
    │   │   │   ├── crab_script.py
    │   │   │   ├── crab_script.sh
    │   │   │   └── branchlist_Run2_MC.txt
    │   │   ├── TTToHadronic_TuneCP5_powheg/
    │   │   ├── TTToSemiLeptonic_TuneCP5_powheg/
    │   └── Data/
  ```

- Each subdirectory contains necessary files for CRAB submission, such as `crab_config.py` and support scripts.

#### **Other Examples**
1. **Running for 2016 PreVFP Data:**
   ```bash
   python3 script.py --inputList DataAndMCList/UL2016PreVFP_Data.txt --WorkName TestRun --UserID myuser
   ```
   This will create the directory: `TestRun/2016PreVFP/Data`.

2. **Running for 2017 MC:**
   ```bash
   python3 script.py --inputList DataAndMCList/UL2017_MC.txt --WorkName TestRun --UserID sha 
   ```
   This will create the directory: `TestRun/2017/MC`.

---

### **2. Running `crabAutosubmit.py`**
Use the `crabAutosubmit.py` script to automate CRAB job submission or status checking across all directories created by `script.py`.

#### **Basic Command for Submission**
```bash
python3 crabAutosubmit.py --inputList DataAndMCList/UL2016PreVFP_MC_Test.txt --WorkName TestV1 --crabCommand submit
```

- **Options:**
  - `--inputList`: Path to the file containing the NanoAOD dataset list.
  - `--WorkName`: Name of the working directory.
  - `--crabCommand`: CRAB command to execute (`submit` or `status`).

#### **Command for Status Checking**
```bash
python3 crabAutosubmit.py --inputList DataAndMCList/UL2016PreVFP_MC_Test.txt --WorkName TestV1 --crabCommand status
```

- For each directory, the script checks if a CRAB working directory (e.g., `crab_<shortname>`) exists. If it does, it runs:
  ```bash
  crab status -d <crab_directory>
  ```

#### **Key Features**
1. **Automatic VOMS Proxy Check**:
   - Before executing CRAB commands, the script ensures that a valid VOMS proxy exists. If not, it prompts the user to create one using:
     ```bash
     voms-proxy-init
     ```

2. **CRAB Environment Setup**:
   - The script ensures the CRAB environment is properly sourced.

3. **Skipping Existing Submissions**:
   - For `submit`, if a CRAB working directory already exists, the script skips that directory to avoid duplicate submissions.

#### **Example Execution**
1. **Submit Jobs for 2016 PreVFP MC:**
   ```bash
   python3 crabAutosubmit.py --inputList DataAndMCList/UL2016PreVFP_MC_Test.txt --WorkName TestV1 --crabCommand submit
   ```

2. **Check Status for 2016 PreVFP MC:**
   ```bash
   python3 crabAutosubmit.py --inputList DataAndMCList/UL2016PreVFP_MC_Test.txt --WorkName TestV1 --crabCommand status
   ```

---

## **Summary**
By using `script.py` and `crabAutosubmit.py`, you can efficiently prepare and automate CRAB job submissions for NanoAOD-based analyses. Ensure that you have the correct VOMS proxy and CRAB environment setup before executing the scripts.

For additional help or issues, please contact the repository maintainer or open an issue on GitHub.



