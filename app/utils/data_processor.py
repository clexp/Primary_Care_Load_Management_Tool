import pandas as pd
import glob
import os
import numpy as np

# Define the directory path relative to the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "Attachments-call data")

def load_and_combine_call_data(directory=DATA_DIR):
    # Check if directory exists
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    # Get all CSV files in the directory that match the pattern
    csv_files = glob.glob(os.path.join(directory, "csv-queue-report*.csv"))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {directory}")
    
    # List to store individual dataframes
    dfs = []
    
    # Read each CSV file
    for file in csv_files:
        print(f"Reading file: {os.path.basename(file)}")
        # Read CSV file
        df = pd.read_csv(file)
        
        # Remove the "Total" row
        df = df[df['Time'] != 'Total']
        
        # Convert Time column to datetime
        df['Time'] = pd.to_datetime(df['Time'])
        
        # Add to list of dataframes
        dfs.append(df)
    
    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Sort by time
    combined_df = combined_df.sort_values('Time')
    
    # Remove duplicates if any
    combined_df = combined_df.drop_duplicates(subset=['Time'])
    
    return combined_df

def process_call_data(file):
    """Process uploaded call data file"""
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        df = pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format")
    
    # Your existing data processing code here
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], 
                                  format='%d/%m/%Y %H:%M',
                                  dayfirst=True)
    
    return df

def load_demo_data():
    """Load synthetic demo data"""
    # Create synthetic data similar to your real data
    # This can be based on your current dataset
    return demo_df

if __name__ == "__main__":
    try:
        # Load and combine the data
        combined_data = load_and_combine_call_data()
        
        # Print basic information about the combined dataset
        print(f"\nTotal number of records: {len(combined_data)}")
        print(f"\nDate range: from {combined_data['Time'].min()} to {combined_data['Time'].max()}")
        print(f"\nColumns in the dataset:")
        for col in combined_data.columns:
            print(f"- {col}")
    except Exception as e:
        print(f"Error: {e}") 