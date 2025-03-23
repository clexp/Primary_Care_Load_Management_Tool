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

# Data Upload Section
st.header("Data Upload 📊")
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
        try:
            # Read the CSV file
            df = pd.read_csv(file)
            
            # Remove the "Total" row before processing
            df = df[df['Time'] != "Total"].copy()
            
            # Convert Time column to datetime
            df['Time'] = pd.to_datetime(df['Time'])
            all_data.append(df)
            
            st.success(f"Successfully processed {file.name}")
        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")
            st.error("Debug info:")
            if 'df' in locals():
                st.write("Columns in file:", df.columns.tolist())
                st.write("First few Time values:", df['Time'].head())
    
    if all_data:
        # Combine all dataframes
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Sort by time to ensure chronological order
        combined_df = combined_df.sort_values('Time')
        
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
else:
    st.info("Please upload your call data files to begin analysis.")

# Add any getting started instructions or overview metrics here
if 'call_data' in st.session_state:
    st.success("Data is loaded! Navigate to 'Quick Insights' to see analysis.")
else:
    st.info("Start by uploading your call data in the 'Data Upload' page.") 