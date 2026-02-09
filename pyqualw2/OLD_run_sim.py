# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 15:48:22 2022
Inherited Novemeber 2023
Last update: Feb 2025

@author: jcohen
@editor: jHawkins
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import subprocess
import glob, os, shutil
import time
import sys

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Modules.DataVis import QAQC_plot

def backup_w2_con():
    """Backup w2_con.csv file"""
    try:
        shutil.copy2('w2_con.csv', 'w2_con.csv.backup')
        print("Backed up w2_con.csv")
    except Exception as e:
        print(f"Error backing up w2_con.csv: {str(e)}")
        raise

def restore_w2_con():
    """Restore w2_con.csv from backup"""
    try:
        shutil.copy2('w2_con.csv.backup', 'w2_con.csv')
        print("Restored w2_con.csv from backup")
    except Exception as e:
        print(f"Error restoring w2_con.csv: {str(e)}")
        raise

def read_and_filter_data(start_date, end_date):
    """Read and filter flow and temperature data"""
    df_flow = pd.read_csv('flow_data/flow_data_base.csv', index_col=0, parse_dates=True)
    df_temp = pd.read_csv('flow_data/flow_data_temp.csv', index_col=0, parse_dates=True)
    
    print("\nOriginal data shapes:")
    print(f"Flow data shape: {df_flow.shape}")
    print(f"Temp data shape: {df_temp.shape}")
    
    df_flow.index = pd.to_datetime(df_flow.index)
    start_date_inclusive = pd.Timestamp(start_date).floor('D')
    end_date_inclusive = pd.Timestamp(end_date).ceil('D')
    
    # Calculate Julian days for start and end dates
    start_jday = (start_date_inclusive - pd.Timestamp('1921-01-01')).days + 1
    end_jday = (end_date_inclusive - pd.Timestamp('1921-01-01')).days + 1
    
    print(f"\nDate Range Information:")
    print(f"Start date: {start_date_inclusive}")
    print(f"End date: {end_date_inclusive}")
    print(f"Start Julian day: {start_jday}")
    print(f"End Julian day: {end_jday}")
    
    # Print the actual date range in the data
    print("\nData date ranges:")
    print(f"Flow data range: {df_flow.index.min()} to {df_flow.index.max()}")
    print(f"Temp data range: {df_temp.index.min()} to {df_temp.index.max()}")
    
    df_flow = df_flow[(df_flow.index >= start_date_inclusive) & (df_flow.index <= end_date_inclusive)]
    df_temp = df_temp[(df_temp.index >= start_date_inclusive) & (df_temp.index <= end_date_inclusive)]
    
    print(f"\nFiltered data shapes:")
    print(f"Flow data shape: {df_flow.shape}")
    print(f"Temp data shape: {df_temp.shape}")
    
    # Print the first and last few rows of the filtered data
    print("\nFirst few rows of filtered flow data:")
    print(df_flow.head())
    print("\nLast few rows of filtered flow data:")
    print(df_flow.tail())
    
    return df_flow, df_temp

def create_julian_days(df_flow, start_date):
    """Create Julian day array for the simulation period"""
    JDAY_init = (pd.Timestamp(start_date) - pd.Timestamp('1-1-1921')).days + 1
    JDAYS = np.arange(JDAY_init, JDAY_init + len(df_flow.index))
    df_flow['JDAY'] = JDAYS
    return JDAYS

def format_data_for_model(df_flow, df_temp, analog_year):
    """Format data for model input files"""
    SPL_OUT = df_flow.SPL_OUT.values * 0.028316847
    FKC_OUT = df_flow.FKC_OUT.values * 0.028316847
    MC_OUT = df_flow.MC_OUT.values * 0.028316847
    SJR_OUT = df_flow.SJR_OUT.values * 0.028316847
    M_IN = np.abs(df_flow.M_IN.values * 0.028316847)
    MIL_EVAP = df_flow.MIL_EVAP.values * 0.028316847
    JDAY = df_flow.JDAY.values * 1.000
    Temp_predicted = df_temp[f'{analog_year}_Temp'].values * 1.000
    zero_filler = np.zeros(len(df_flow.index)) * 1.000
    
    return {
        'SPL_OUT': SPL_OUT,
        'FKC_OUT': FKC_OUT,
        'MC_OUT': MC_OUT,
        'SJR_OUT': SJR_OUT,
        'M_IN': M_IN,
        'MIL_EVAP': MIL_EVAP,
        'JDAY': JDAY,
        'Temp_predicted': Temp_predicted,
        'zero_filler': zero_filler
    }

def create_input_files(data, analog_year):
    """Create all required input files for the model"""
    # Format all values to 2 decimal places
    for key in data:
        if key != 'zero_filler':
            data[key] = [f'{x:0.2f}' for x in data[key]]
        else:
            data[key] = [f'{x:0.2f}' for x in data[key]]
    
    # Create mqot_br1.npt
    with open('initial_files/mqot_br1_init.npt', "r") as f:
        lines = f.readlines()
    for i in range(len(data['JDAY'])):
        lines.append(f"\n{data['JDAY'][i]:>8}{data['SPL_OUT'][i]:>8}{data['FKC_OUT'][i]:>8}{data['MC_OUT'][i]:>8}{data['SJR_OUT'][i]:>8}")
    with open('mqot_br1.npt', "w") as update:
        update.writelines(lines)
    
    # Create mqdt_br1.npt
    with open('initial_files/mqdt_br1_init.npt', "r") as f:
        lines = f.readlines()
    for i in range(len(data['JDAY'])):
        lines.append(f"\n{data['JDAY'][i]:>8}{data['MIL_EVAP'][i]:>8}")
    with open('mqdt_br1.npt', "w") as update:
        update.writelines(lines)
    
    # Create mqin_br1.npt
    with open('initial_files/mqin_br1_init.npt', "r") as f:
        lines = f.readlines()
    for i in range(len(data['JDAY'])):
        lines.append(f"\n{data['JDAY'][i]:>8}{data['M_IN'][i]:>8}")
    with open('mqin_br1.npt', "w") as update:
        update.writelines(lines)
    
    # Create mqin_br2-4.npt files
    for branch in ['2', '3', '4']:
        with open(f'initial_files/mqin_br{branch}_init.npt', "r") as f:
            lines = f.readlines()
        for i in range(len(data['JDAY'])):
            lines.append(f"\n{data['JDAY'][i]:>8}{data['zero_filler'][i]:>8}")
        with open(f'mqin_br{branch}.npt', "w") as update:
            update.writelines(lines)
    
    # Create mtin_br1-4.npt files
    for branch in ['1', '2', '3', '4']:
        with open(f'initial_files/mtin_br{branch}_init.npt', "r") as f:
            lines = f.readlines()
        for i in range(len(data['JDAY'])):
            lines.append(f"\n{data['JDAY'][i]:>8}{data['Temp_predicted'][i]:>8}")
        with open(f'mtin_br{branch}.npt', "w") as update:
            update.writelines(lines)

def process_met_data(analog_year, JDAY_init, JDAYS, start_date):
    """Process meteorological data for the simulation"""
    # Read met data from start date year to get the JDAY values
    start_year = str(start_date.year)
    df_met_base = pd.read_csv(f'met_data/{start_year}_CEQUAL_met_inputs.csv', index_col=0, parse_dates=True)
    
    # Read met data from analog year
    df_met = pd.read_csv(f'met_data/{analog_year}_CEQUAL_met_inputs.csv', index_col=0, parse_dates=True)
    
    # print("\nDataframe lengths before trimming:")
    # print(f"Base year ({start_year}) length: {len(df_met_base)}")
    # print(f"Analog year ({analog_year}) length: {len(df_met)}")
    
    # Ensure both dataframes have the same length
    min_length = min(len(df_met_base), len(df_met))
    df_met_base = df_met_base.iloc[:min_length]
    df_met = df_met.iloc[:min_length]
    
    # print("\nDataframe lengths after trimming:")
    # print(f"Base year ({start_year}) length: {len(df_met_base)}")
    # print(f"Analog year ({analog_year}) length: {len(df_met)}")
    
    # print("\nBase year met data (first 5 rows):")
    # print(df_met_base.head())
    # print("\nAnalog year met data (first 5 rows):")
    # print(df_met.head())
    
    # Replace the first two columns of analog year data with start year data
    df_met.iloc[:, 0] = df_met_base.iloc[:, 0]  # Replace JDAY column
    
    # print("\nAnalog year met data after replacing JDAY (first 5 rows):")
    # print(df_met.head())
    
    # Calculate the exact JDAY range we need
    start_jday = JDAY_init
    end_jday = JDAYS[-1]
    
    # print("\nJDAY Range Information:")
    # print(f"JDAY_init: {JDAY_init}")
    # print(f"JDAYS array length: {len(JDAYS)}")
    # print(f"JDAYS first value: {JDAYS[0]}")
    # print(f"JDAYS last value: {JDAYS[-1]}")
    # print(f"Start JDAY for filtering: {start_jday}")
    # print(f"End JDAY for filtering: {end_jday}")
    
    # Filter met data to match the time period
    df_met = df_met[(df_met.JDAY >= start_jday) & (df_met.JDAY <= end_jday)]
    
    # Add debug prints to verify we have all days
    # print("\nMet data range:")
    # print(f"Base year: {start_year}")
    # print(f"Analog year: {analog_year}")
    # print(f"Number of met records: {len(df_met)}")
    # print(f"Start JDAY: {start_jday}")
    # print(f"End JDAY: {end_jday}")
    
    if len(df_met) > 0:
        # print(f"First met date: {df_met.index[0]}")
        # print(f"Last met date: {df_met.index[-1]}")
        # print(f"First JDAY: {df_met.JDAY.iloc[0]}")
        # print(f"Last JDAY: {df_met.JDAY.iloc[-1]}")
        pass
    else:
        print("WARNING: No met data found for the specified JDAY range!")
        print("This might indicate a problem with the JDAY values or the filtering.")
    
    # Use the met data with the replaced JDAY values
    data = {
        'JDAY': df_met.JDAY.values * 1.000,
        'TAIR': df_met.TAIR.values * 1.000,
        'TDEW': df_met.TDEW.values * 1.000,
        'WIND': df_met.WIND.values * 1.000,
        'PHI': df_met.PHI.values * 1.000,
        'CLOUD': df_met.CLOUD.values * 1.000,
        'SRO': df_met.SRO.values * 1.000
    }
    
    # Format all values to 2 decimal places
    for key in data:
        data[key] = [f'{x:0.2f}' for x in data[key]]
    
    # Create mmet3.npt
    with open('initial_files/mmet3_init.npt', "r") as f:
        lines = f.readlines()
    for i in range(len(data['JDAY'])):
        lines.append(f"\n{data['JDAY'][i]:>8}{data['TAIR'][i]:>8}{data['TDEW'][i]:>8}{data['WIND'][i]:>8}{data['PHI'][i]:>8}{data['CLOUD'][i]:>8}{data['SRO'][i]:>8}")
    lines.append("\n")
    with open('mmet3.npt', "w") as update:
        update.writelines(lines)
    print(f"Created mmet3.npt with {len(data['JDAY'])} lines of hourly data")

def check_file_activity(file_path, timeout=10):
    """Check if a file has been modified within the timeout period"""
    try:
        if not os.path.exists(file_path):
            return False
            
        # Get the current time and file's last modification time
        current_time = time.time()
        file_mtime = os.path.getmtime(file_path)
        
        # Check if the file has been modified within the timeout period
        time_since_mod = current_time - file_mtime
        #print(f"File {file_path} last modified {time_since_mod:.1f} seconds ago")
        return time_since_mod < timeout
    except Exception as e:
        print(f"Error checking file activity: {str(e)}")
        return False

def run_model(wait_time):
    """Run the CEQUAL model executable"""
    try:
        if os.name == 'nt':  # Windows
            process = subprocess.Popen(['w2_v45_64.exe'], 
                                    creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Linux/Unix
            process = subprocess.Popen(['./w2_v45_64.exe'],
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
        
        print("Starting model execution...")
        
        # List of output files to monitor
        output_files = ['two_31.csv', 'qwo_31.csv', 'tsr_1_seg31.csv']
        
        # Wait for the process to complete or timeout
        start_time = time.time()
        
        # Wait 20 seconds before starting to check file activity
        #print("Waiting 20 seconds before monitoring file activity...")
        time.sleep(10)
        
        # Track the last time any file was modified
        last_activity_time = time.time()
        
        while process.poll() is None and (time.time() - start_time) < wait_time:
            # Check if any file has been modified recently
            any_file_active = False
            for file in output_files:
                if os.path.exists(file) and check_file_activity(file):
                    any_file_active = True
                    last_activity_time = time.time()
                    break
            
            if any_file_active:
                #print("File activity detected, continuing...")
                time.sleep(5)
            else:
                # If no files have been modified for 10 seconds, consider it complete
                if time.time() - last_activity_time > 10:
                    print("No file activity detected for 10 seconds. Model completed successfully.")
                    # Close the model window
                    if os.name == 'nt':
                        subprocess.run(['taskkill', '/F', '/IM', 'w2_v45_64.exe'])
                    else:
                        process.kill()
                    return
                else:
                    print(f"Waiting for file activity... ({int(time.time() - last_activity_time)}s since last activity)")
                    time.sleep(5)
        
        if process.poll() is None:
            print(f"Model execution timed out after {wait_time} seconds")
            if os.name == 'nt':
                subprocess.run(['taskkill', '/F', '/IM', 'w2_v45_64.exe'])
            else:
                process.kill()
            raise Exception("Simulation timed out")
            
        print("Model execution completed")
            
    except subprocess.TimeoutExpired:
        print(f"Model execution timed out after {wait_time} seconds")
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/IM', 'w2_v45_64.exe'])
        else:
            process.kill()
        raise
    except Exception as e:
        print(f"Error running executable: {str(e)}")
        raise

def create_run_details_file(run_dir, run_name, start_date, end_date, analog_year, temp_profile_year):
    """Create a text file with details of the model run"""
    try:
        details_file = os.path.join(run_dir, 'run_details.txt')
        with open(details_file, 'w') as f:
            f.write(f"Model Run Details\n")
            f.write(f"================\n\n")
            f.write(f"Run Name: {run_name}\n")
            f.write(f"Start Date: {start_date.strftime('%m/%d/%Y %H:%M')}\n")
            f.write(f"End Date: {end_date.strftime('%m/%d/%Y %H:%M')}\n")
            # Create temperature profile date by replacing the year in start_date with temp_profile_year
            temp_profile_date = start_date.replace(year=temp_profile_year)
            f.write(f"Temperature Profile Date: {temp_profile_date.strftime('%m/%d/%Y')}\n")
            f.write(f"Flow Data Year: {start_date.year}\n")
            f.write(f"Meteorological Data Year: {analog_year}\n")
            f.write(f"\nRun Date: {datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')}\n")
        print(f"Run details saved to: {details_file}")
    except Exception as e:
        print(f"Error creating run details file: {str(e)}")

def save_model_outputs(analog_year, run_name, start_date, end_date, temp_profile_year):
    """Save model output files and input files"""
    try:
        base_dir = '../CEQUAL_outputs'
        year_dir = os.path.join(base_dir, str(analog_year))
        run_dir = os.path.join(year_dir, run_name)
        inputs_dir = os.path.join(run_dir, 'inputs')
        
        # Create directories if they don't exist
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)
        if not os.path.exists(run_dir):
            os.makedirs(run_dir)
        if not os.path.exists(inputs_dir):
            os.makedirs(inputs_dir)
        
        # Save output files
        shutil.copy2('two_31.csv', os.path.join(run_dir, f'two_31_{analog_year}_{run_name}.csv'))
        shutil.copy2('qwo_31.csv', os.path.join(run_dir, f'qwo_31_{analog_year}_{run_name}.csv'))
        shutil.copy2('tsr_1_seg31.csv', os.path.join(run_dir, f'tsr_1_seg31_{analog_year}_{run_name}.csv'))
        
        # Save input files
        npt_files = glob.glob('*.npt')
        for npt_file in npt_files:
            shutil.copy2(npt_file, os.path.join(inputs_dir, npt_file))
        
        # Save w2_con.csv
        shutil.copy2('w2_con.csv', os.path.join(inputs_dir, 'w2_con.csv'))
        
        # Create run details file
        create_run_details_file(run_dir, run_name, start_date, end_date, analog_year, temp_profile_year)
        
        print(f"Model outputs saved to: {run_dir}")
        print(f"Input files saved to: {inputs_dir}")
        print(f"Files saved with format: [filename]_{analog_year}_{run_name}.csv")
        
    except Exception as e:
        print(f"Error saving model output: {str(e)}")

def run_simulation(start_date, end_date, analog_year, wait_time, run_name, temp_profile_year):
    """Run a single simulation for a given analog year"""
    print(f"\nProcessing analog year: {analog_year}")
    
    backup_w2_con()
    
    # Read and process data
    df_flow, df_temp = read_and_filter_data(start_date, end_date)
    JDAYS = create_julian_days(df_flow, start_date)
    
    # Format data for model
    model_data = format_data_for_model(df_flow, df_temp, analog_year)
    
    # Create input files
    create_input_files(model_data, analog_year)
    
    # Process met data
    process_met_data(analog_year, JDAYS[0], JDAYS, start_date)
    
    # Restore w2_con.csv
    restore_w2_con()
    
    # Run model
    run_model(wait_time)
    
    # Save outputs
    save_model_outputs(analog_year, run_name, start_date, end_date, temp_profile_year)
    
    # Create QAQC plot after files are saved
    base_dir = '../CEQUAL_outputs'
    year_dir = os.path.join(base_dir, str(analog_year))
    run_dir = os.path.join(year_dir, run_name)
    csv_file = os.path.join(run_dir, f'two_31_{analog_year}_{run_name}.csv')
    QAQC_plot(csv_file, analog_year, run_name)

def main():
    """Main function that runs the simulation with predefined parameters"""
    # User defined variables
    start_date = '05/15/2018 1:00'  # start date of simulation (always start at 1:00)
    end_date = '12/30/2018 23:00'   # end date of simulation (always at at 23:00)
    temp_profile_year = 2022        # year of temperature profile
    #analog_years = [2022]           # available: [1988,1989,1990,1994,2002,2007,2008,2013,2020,2021,2022,2023,2024]
    analog_years = [2024,2023,2022,2021,2020,2019, 2018,2017]           # available: [1988,1989,1990,1994,2002,2007,2008,2013,2020,2021,2022,2023,2024]
    wait_time = 220                 # seconds between simulations
    
    # Convert dates to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Get run name from user
    run_name = input("Enter the name for this run: ")
    
    # Run simulations for each analog year
    for analog_year in analog_years:
        run_simulation(
            start_date=start_date,
            end_date=end_date,
            analog_year=analog_year,
            wait_time=wait_time,
            run_name=run_name,
            temp_profile_year=temp_profile_year
        )

if __name__ == "__main__":
    main()
