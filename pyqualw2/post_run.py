# This module contains functions to used immeadilbiy after model run of simulation

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
