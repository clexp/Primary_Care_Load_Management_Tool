import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.title("Data Loader 📂")
st.write("Upload and clean your call center data")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        # Read the CSV file
        df = pd.read_csv(uploaded_file)
        
        # Store raw data in session state
        st.session_state['processed_data']['raw_df'] = df
        st.session_state['processed_data']['clean_df'] = df.copy()  # Initialize clean_df with raw data
        st.session_state['processed_data']['data_loaded'] = True
        
        # Display raw data summary
        st.header("Raw Data Summary")
        st.write(f"Number of records: {len(df)}")
        st.write(f"Number of columns: {len(df.columns)}")
        
        # Show raw data preview
        st.subheader("Raw Data Preview")
        st.dataframe(df.head())
        
        # Data Cleaning Section
        st.header("Data Cleaning")
        
        # Date and Time Processing
        st.subheader("Date and Time Processing")
        if 'Date' in df.columns and 'Time' in df.columns:
            try:
                # Convert Date column to datetime
                df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
                
                # Create datetime column
                df['datetime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'])
                
                # Update clean_df in session state
                st.session_state['processed_data']['clean_df'] = df
                
                st.success("Date and time processing completed successfully")
            except Exception as e:
                st.error(f"Error processing dates: {str(e)}")
        
        # Null Value Handling
        st.subheader("Null Value Handling")
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            st.write("Columns with null values:")
            st.write(null_counts[null_counts > 0])
            
            # Select columns to check for nulls
            columns_with_nulls = null_counts[null_counts > 0].index.tolist()
            selected_columns = st.multiselect(
                "Select columns to check for null values",
                columns_with_nulls,
                default=columns_with_nulls
            )
            
            if selected_columns:
                # Show impact of removing nulls
                rows_to_remove = df[selected_columns].isnull().any(axis=1).sum()
                st.write(f"Number of rows that would be removed: {rows_to_remove}")
                
                if st.button("Remove rows with nulls in selected columns"):
                    df = df.dropna(subset=selected_columns)
                    st.session_state['processed_data']['clean_df'] = df
                    st.success(f"Removed {rows_to_remove} rows with null values")
        else:
            st.success("No null values found in the dataset")
        
        # Cleaned Data Summary
        st.header("Cleaned Data Summary")
        clean_df = st.session_state['processed_data']['clean_df']
        st.write(f"Number of records: {len(clean_df)}")
        st.write(f"Number of columns: {len(clean_df.columns)}")
        
        # Show cleaned data preview
        st.subheader("Cleaned Data Preview")
        st.dataframe(clean_df.head())
        
        # Export Options
        st.header("Export Options")
        if st.button("Export Cleaned Data"):
            csv = clean_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="cleaned_call_center_data.csv",
                mime="text/csv"
            )
            
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
else:
    st.info("Please upload a CSV file to begin")
    
    # Add sample data format information
    st.markdown("""
    ### Expected Data Format
    The CSV file should contain the following columns:
    - Month: Month of the data
    - Day: Day of the week
    - Time: Time interval (HH:MM)
    - Date: Date in DD/MM/YYYY format
    - Total Calls: Total number of calls
    - Connected Calls: Number of connected calls
    - Calls Not Connected: Number of unconnected calls
    - Availability (%): Agent availability percentage
    - Avg Call Length (s): Average call duration in seconds
    - Avg Wait Time (s): Average wait time in seconds
    - And other relevant metrics...
    """) 