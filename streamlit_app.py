import streamlit as st
import sys
import pandas as pd
from pathlib import Path

# Add the root directory to Python path
root_path = Path(__file__).parent
sys.path.append(str(root_path))

st.set_page_config(
    page_title="Primary Care Load Management Tool",
    page_icon="📞",
    layout="wide"
)

st.title("Primary Care Load Management Tool 📞")
st.write("""
Welcome to the Primary Care Load Management Tool. This tool helps you:
- Analyze your call center data
- Predict call volumes
- Plan staffing levels
- Optimize waiting times
""")

# Data Upload Instructions Section
st.header("Getting Started 📊")
st.write("""
## Data Upload Instructions

To begin using this tool, please navigate to the "Data Upload" page in the sidebar.

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
    
    st.success("Data has been successfully uploaded. You can now use the other pages to analyze your data.")
else:
    st.info("No data has been uploaded yet. Please navigate to the 'Data Upload' page to upload your call data files.") 