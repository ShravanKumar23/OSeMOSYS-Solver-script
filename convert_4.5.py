import os
import pandas as pd
from openpyxl import load_workbook
import subprocess

def process_and_convert(input_file):
    # Define input and output directories
    inputDir = "data"
    outputdir = 'Input_Data'
    config_file = 'config_com_4.5.yaml'
    
    # Create the input data folder if it doesn't exist
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    
    # Generate output file name based on the input file name
    base = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join('Input_Data', f'{base}.xlsx')    
    
    # Step 7: Run the otoole convert command
    cmd = f"otoole convert datafile csv {input_file} data {config_file}"
    subprocess.run(cmd, shell=True)

    # Step 1: Initialize DataFrames
    df = pd.DataFrame()
    sets_df = pd.DataFrame()
    
    # Step 2: Define Setslist and load files
    Setslist = ["REGION", "REGION2", "DAYTYPE", "EMISSION", "FUEL", "DAILYTIMEBRACKET", "SEASON", "TIMESLICE", "STORAGE", "MODE_OF_OPERATION", "TECHNOLOGY", "YEAR"]
    files = os.listdir(inputDir)

    # Step 3: Process each file
    for i in files:
        if i.replace('.csv', '') not in Setslist:
            dftemp = pd.read_csv(os.path.join(inputDir, i))
            dftemp = dftemp.reindex(columns=["PARAM", "VALUE", "REGION", "REGION2", "DAYTYPE", "EMISSION", "FUEL", "DAILYTIMEBRACKET", "SEASON", "TIMESLICE", "STORAGE", "MODE_OF_OPERATION", "TECHNOLOGY", "YEAR"])
            dftemp['PARAM'] = i.replace('.csv', '')
            df = pd.concat([df, dftemp])
        elif i.replace('.csv', '') in Setslist:
            dftempsets = pd.read_csv(os.path.join(inputDir, i))
            if i.replace('.csv', '') == 'TIMESLICE':
                orgtslist = dftempsets['VALUE'].to_list()
                setslist = list(range(1, len(dftempsets['VALUE']) + 1))
            else:
                setslist = dftempsets['VALUE'].to_list()
            dftempsetsdup = pd.DataFrame()
            dftempsetsdup[str(i.replace('.csv', ''))] = setslist
            sets_df = pd.concat([sets_df, dftempsetsdup], axis=1)
    
    # Step 4: Mapping TIMESLICE values
    if 'orgtslist' in locals():  # Ensure orgtslist is defined
        mapping_dict = {j: i for i, j in enumerate(orgtslist, start=1)}
        df['TIMESLICE'] = df['TIMESLICE'].replace(mapping_dict)
    
    # Step 6: Append specific sheets from another workbook
    source_file = r'C:\Users\skpk\OneDrive - KTH\OSeMOSYS_PULP_Short\SRC\Input_Data\UTOPIA_BASE_TS.xlsx'
    source_workbook = load_workbook(source_file)
    sheet_names = ['PARAMETERS_DEFAULT', 'MCS', 'MCS_num', 'Introduction']

    # Step 5: Save to Excel
    with pd.ExcelWriter(output_file) as writer:
        sets_df.to_excel(writer, sheet_name='SETS', index=False)
        df.to_excel(writer, sheet_name='PARAMETERS', index=False)
        for sheet in sheet_names:
            df1 = pd.read_excel(source_file, sheet_name=sheet)
            df1.to_excel(writer, sheet_name=sheet, index=False)
    
    print("Process completed successfully.")

# Example of how to call the function from the command prompt
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script_name.py input_file.txt")
    else:
        input_file = sys.argv[1]
        process_and_convert(input_file)
