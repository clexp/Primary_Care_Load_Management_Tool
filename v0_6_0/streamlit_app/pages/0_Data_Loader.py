import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Initialize session state if it doesn't exist
if 'processed_data' not in st.session_state:
    st.session_state['processed_data'] = {
        'raw_df': None,
        'clean_df': None,
        'daily_pattern': None,
        'data_loaded': False,
        'daily_stats': None,
        'call_volume_model': None,
        'wait_time_model': None,
        'call_duration_model': None,
        'call_volume_forecast': None,
        'wait_time_forecast': None,
        'call_duration_forecast': None
    }

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
        
        # Create Daily Pattern Dataset
        st.header("Creating Daily Pattern Dataset")
        if 'Total Calls' in df.columns and 'Time' in df.columns and 'Day' in df.columns:
            try:
                # Extract time slots and day of week
                df['time_slot'] = pd.to_datetime(df['Time'], format='%H:%M').dt.time
                
                # Calculate mean and std for each day and time slot
                daily_pattern = df.groupby(['Day', 'time_slot']).agg({
                    'Total Calls': ['mean', 'std', 'count']
                }).reset_index()
                
                # Rename columns
                daily_pattern.columns = ['Day', 'Time Slot', 'Average', 'Standard Deviation', 'Sample Size']
                
                # Sort by day and time
                daily_pattern = daily_pattern.sort_values(['Day', 'Time Slot'])
                
                # Store in session state
                st.session_state['processed_data']['daily_pattern'] = daily_pattern
                
                st.success("Daily pattern dataset created successfully")
                
                # Show preview of daily pattern
                st.subheader("Daily Pattern Preview")
                st.dataframe(daily_pattern)
                
            except Exception as e:
                st.error(f"Error creating daily pattern: {str(e)}")
        else:
            st.warning("Required columns (Total Calls, Time, Day) not found in dataset")
        
        # Create Call Time Pattern Dataset
        st.header("Creating Call Time Pattern Dataset")
        if 'Avg Call Length (s)' in df.columns and 'Time' in df.columns and 'Day' in df.columns:
            try:
                # Extract time slots and day of week
                df['time_slot'] = pd.to_datetime(df['Time'], format='%H:%M').dt.time
                
                # Calculate mean and std for each day and time slot
                call_time_pattern = df.groupby(['Day', 'time_slot']).agg({
                    'Avg Call Length (s)': ['mean', 'std', 'count']
                }).reset_index()
                
                # Rename columns
                call_time_pattern.columns = ['Day', 'Time Slot', 'Average Call Time (s)', 'Standard Deviation (s)', 'Sample Size']
                
                # Sort by day and time
                call_time_pattern = call_time_pattern.sort_values(['Day', 'Time Slot'])
                
                # Store in session state
                st.session_state['processed_data']['call_time_pattern'] = call_time_pattern
                
                st.success("Call time pattern dataset created successfully")
                
                # Show preview of call time pattern
                st.subheader("Call Time Pattern Preview")
                st.dataframe(call_time_pattern)
                
                # Create visualization
                st.subheader("Call Time Pattern Visualization")
                fig = px.line(call_time_pattern, 
                            x='Time Slot', 
                            y='Average Call Time (s)',
                            color='Day',
                            error_y='Standard Deviation (s)',
                            title='Average Call Time by Time Slot and Day')
                st.plotly_chart(fig)
                
            except Exception as e:
                st.error(f"Error creating call time pattern: {str(e)}")
        else:
            st.warning("Required columns (Avg Call Length (s), Time, Day) not found in dataset")
        
        # Create Wait Time Pattern Dataset
        st.header("Creating Wait Time Pattern Dataset")
        if 'Avg Wait Time (s)' in df.columns and 'Time' in df.columns and 'Day' in df.columns:
            try:
                # Extract time slots and day of week
                df['time_slot'] = pd.to_datetime(df['Time'], format='%H:%M').dt.time
                
                # Calculate mean and std for each day and time slot
                wait_time_pattern = df.groupby(['Day', 'time_slot']).agg({
                    'Avg Wait Time (s)': ['mean', 'std', 'count']
                }).reset_index()
                
                # Rename columns
                wait_time_pattern.columns = ['Day', 'Time Slot', 'Average Wait Time (s)', 'Standard Deviation (s)', 'Sample Size']
                
                # Sort by day and time
                wait_time_pattern = wait_time_pattern.sort_values(['Day', 'Time Slot'])
                
                # Store in session state
                st.session_state['processed_data']['wait_time_pattern'] = wait_time_pattern
                
                st.success("Wait time pattern dataset created successfully")
                
                # Show preview of wait time pattern
                st.subheader("Wait Time Pattern Preview")
                st.dataframe(wait_time_pattern)
                
                # Create visualization
                st.subheader("Wait Time Pattern Visualization")
                fig = px.line(wait_time_pattern, 
                            x='Time Slot', 
                            y='Average Wait Time (s)',
                            color='Day',
                            error_y='Standard Deviation (s)',
                            title='Average Wait Time by Time Slot and Day')
                st.plotly_chart(fig)
                
                # Add a combined visualization of call time and wait time
                st.subheader("Combined Call and Wait Time Analysis")
                combined_data = pd.merge(
                    call_time_pattern,
                    wait_time_pattern,
                    on=['Day', 'Time Slot'],
                    suffixes=('_call', '_wait')
                )
                
                fig_combined = go.Figure()
                
                # Add call time traces
                for day in combined_data['Day'].unique():
                    day_data = combined_data[combined_data['Day'] == day]
                    fig_combined.add_trace(go.Scatter(
                        x=day_data['Time Slot'],
                        y=day_data['Average Call Time (s)'],
                        name=f'{day} - Call Time',
                        line=dict(dash='solid')
                    ))
                    
                    # Add wait time traces
                    fig_combined.add_trace(go.Scatter(
                        x=day_data['Time Slot'],
                        y=day_data['Average Wait Time (s)'],
                        name=f'{day} - Wait Time',
                        line=dict(dash='dot')
                    ))
                
                fig_combined.update_layout(
                    title='Call Time vs Wait Time by Time Slot and Day',
                    xaxis_title='Time Slot',
                    yaxis_title='Time (seconds)',
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_combined)
                
            except Exception as e:
                st.error(f"Error creating wait time pattern: {str(e)}")
        else:
            st.warning("Required columns (Avg Wait Time (s), Time, Day) not found in dataset")
        
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