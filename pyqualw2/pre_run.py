# This module contains function to run prior to runnning a simulation
# Assumes the model is already configured 
# (w2_con.csv, mbth.npt, and mvpr1.npt are all set)
#
# Function directory:
# 
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
