import streamlit as st
import pandas as pd
from pathlib import Path
import glob

def data_upload_page():
    st.title("Data Upload 📊")
    
    st.write("""
    ## Data Upload Instructions
    
    Please use the upload function on the main page to upload your call data files.
    
    ### Data Requirements:
    - Files should be in CSV format
    - Each file should contain a 'Time' column with datetime values
    - Each file should contain a 'Total Calls' column with call volume data
    - Files should have the same structure
    
    ### After Uploading:
    - Your data will be processed and combined
    - You can view summary statistics and data quality metrics
    - You can download the combined dataset
    """)
    
    # Check if data has been uploaded
    if 'call_data' in st.session_state:
        df = st.session_state['call_data']
        
        # Display data summary
        st.subheader("Current Data Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", len(df))
        with col2:
            st.metric("Date Range", 
                     f"{df['Time'].min().strftime('%Y-%m-%d')} to {df['Time'].max().strftime('%Y-%m-%d')}")
        with col3:
            st.metric("Total Calls", df['Total Calls'].sum())
        
        # Show sample of the data
        st.subheader("Sample Data")
        st.dataframe(df.head())
        
        # Show data quality metrics
        st.subheader("Data Quality")
        missing_data = df.isnull().sum()
        if missing_data.any():
            st.warning("Missing Data:")
            st.write(missing_data[missing_data > 0])
        else:
            st.success("No missing data found!")
        
        # Add download button for combined data
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Combined Data",
            data=csv,
            file_name="combined_call_data.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data has been uploaded yet. Please use the upload function on the main page.")

if __name__ == "__main__":
    data_upload_page()
