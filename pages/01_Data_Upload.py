import streamlit as st
import pandas as pd
from pathlib import Path
import glob

def load_and_process_csv(file):
    """Load and process a single CSV file"""
    try:
        df = pd.read_csv(file)
        # Convert Time column to datetime
        df['Time'] = pd.to_datetime(df['Time'])
        return df
    except Exception as e:
        st.error(f"Error processing {file.name}: {str(e)}")
        return None

def data_upload_page():
    st.title("Data Upload 📊")
    
    # File uploader for multiple files
    uploaded_files = st.file_uploader(
        "Upload Call Data Files (CSV)",
        type=['csv'],
        accept_multiple_files=True,
        help="Upload multiple CSV files with call data. Files should have the same structure."
    )
    
    if uploaded_files:
        # Process each file
        all_data = []
        for file in uploaded_files:
            df = load_and_process_csv(file)
            if df is not None:
                all_data.append(df)
        
        if all_data:
            # Combine all dataframes
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Store in session state
            st.session_state['call_data'] = combined_df
            
            # Show summary statistics
            st.success(f"Successfully loaded {len(uploaded_files)} files!")
            
            # Display data summary
            st.subheader("Data Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Records", len(combined_df))
            with col2:
                st.metric("Date Range", 
                         f"{combined_df['Time'].min().strftime('%Y-%m-%d')} to {combined_df['Time'].max().strftime('%Y-%m-%d')}")
            with col3:
                st.metric("Total Calls", combined_df['Total Calls'].sum())
            
            # Show sample of the data
            st.subheader("Sample Data")
            st.dataframe(combined_df.head())
            
            # Show data quality metrics
            st.subheader("Data Quality")
            missing_data = combined_df.isnull().sum()
            if missing_data.any():
                st.warning("Missing Data:")
                st.write(missing_data[missing_data > 0])
            else:
                st.success("No missing data found!")
            
            # Add download button for combined data
            csv = combined_df.to_csv(index=False)
            st.download_button(
                label="Download Combined Data",
                data=csv,
                file_name="combined_call_data.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    data_upload_page()
