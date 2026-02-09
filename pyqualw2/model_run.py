# This module contains functions to used during model run
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
ef run_model(wait_time):
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
