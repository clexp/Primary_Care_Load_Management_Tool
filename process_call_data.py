import pandas as pd
import glob
import os

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