import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_demo_data():
    """Generate synthetic call center data"""
    # Create date range for one month
    start_date = datetime(2024, 4, 1)
    dates = []
    times = []
    total_calls = []
    connected_calls = []
    wait_times = []
    
    # Generate data for each half hour between 8 AM and 6 PM
    for day in range(30):
        current_date = start_date + timedelta(days=day)
        if current_date.weekday() < 5:  # Monday to Friday only
            for hour in range(8, 18):
                for minute in [0, 30]:
                    dates.append(current_date.strftime('%d/%m/%Y'))
                    times.append(f"{hour:02d}:{minute:02d}")
                    
                    # Generate realistic call volumes
                    base_calls = 50 if 9 <= hour <= 15 else 30
                    total = int(np.random.normal(base_calls, 10))
                    connected = int(total * np.random.uniform(0.7, 0.9))
                    wait_time = np.random.exponential(180)  # average 3 minutes
                    
                    total_calls.append(max(0, total))
                    connected_calls.append(max(0, min(connected, total)))
                    wait_times.append(max(0, wait_time))
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Time': times,
        'Total Calls': total_calls,
        'Connected Calls': connected_calls,
        'Calls Not Connected': [t - c for t, c in zip(total_calls, connected_calls)],
        'Avg Wait Time (s)': wait_times,
        'Longest Wait Time (s)': [w * 1.5 for w in wait_times]
    })
    
    return df

def data_upload_page():
    st.title("Upload Call Center Data 📊")
    
    st.write("""
    ### Upload your call center data
    You can upload CSV files exported from your phone system. The file should contain:
    - Time information
    - Total number of calls
    - Connected and disconnected calls
    - Wait times
    """)
    
    # File upload section
    st.subheader("Upload Data")
    uploaded_file = st.file_uploader(
        "Choose a CSV file", 
        type=['csv'], 
        help="Upload a CSV file containing your call center data"
    )
    
    # Demo data section
    st.subheader("Or Use Demo Data")
    use_demo = st.checkbox("Use demo data instead", 
                          help="Generate synthetic data to try out the tool")
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Remove the "Total" row before processing
            df = df[df['Time'] != "Total"].copy()
            
            # Convert Time column to datetime
            df['DateTime'] = pd.to_datetime(df['Time'])
            
            st.session_state['call_data'] = df
            st.success("✅ Data loaded successfully!")
            
            # Preview the data
            st.subheader("Data Preview")
            st.dataframe(df.head())
            
            # Show basic statistics
            st.subheader("Basic Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                st.metric("Date Range", 
                         f"{df['DateTime'].min().date()} to {df['DateTime'].max().date()}")
            with col3:
                st.metric("Total Calls", df['Total Calls'].sum())
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            st.error("Debug info:")
            if 'df' in locals():
                st.write("Columns in file:", df.columns.tolist())
                st.write("First few Time values:", df['Time'].head())
            
    elif use_demo:
        df = generate_demo_data()
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], 
                                      format='%d/%m/%Y %H:%M',
                                      dayfirst=True)
        st.session_state['call_data'] = df
        st.success("✅ Demo data loaded!")
        
        # Preview the demo data
        st.subheader("Demo Data Preview")
        st.dataframe(df.head())
        
        st.info("""
        ℹ️ This is synthetic data generated for demonstration purposes. 
        It simulates a typical call center pattern with:
        - Higher volumes during business hours
        - Random variations in call volumes
        - Realistic wait times and connection rates
        """)

if __name__ == "__main__":
    data_upload_page()
