import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import io
import plotly.express as px
import plotly.graph_objects as go

# Add the root directory to Python path
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

from app.utils.data_processor import (
    create_call_data_template, 
    process_call_data, 
    load_and_combine_call_data,
    calculate_data_quality_metrics
)

def data_management_page():
    st.title("Data Management 📊")
    
    st.write("""
    ## Upload Call Data
    Upload your call center data files to analyze patterns and optimize staffing.
    """)
    
    # Add template download button
    st.write("""
    ### Need a template?
    Download a sample template to see the required format for your call data.
    """)
    
    template_bytes = create_call_data_template()
    st.download_button(
        label="Download Call Data Template",
        data=template_bytes,
        file_name="call_data_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload Call Data Files (CSV or Excel)",
        type=['csv', 'xlsx'],
        accept_multiple_files=True,
        help="Upload one or more files with your call data"
    )
    
    if uploaded_files:
        # Process each file
        processed_files = []
        file_status = []
        
        for file in uploaded_files:
            try:
                df = process_call_data(file)
                processed_files.append(df)
                
                # Calculate metrics for this file
                metrics = calculate_data_quality_metrics(df)
                
                # Add status information
                file_status.append({
                    'file_name': file.name,
                    'status': 'Success',
                    'records': metrics['total_records'],
                    'date_range': f"{metrics['date_range_start'].strftime('%Y-%m-%d')} to {metrics['date_range_end'].strftime('%Y-%m-%d')}"
                })
            except Exception as e:
                file_status.append({
                    'file_name': file.name,
                    'status': f'Error: {str(e)}',
                    'records': 0,
                    'date_range': 'N/A'
                })
        
        # Display file processing status
        st.subheader("File Processing Status")
        status_df = pd.DataFrame(file_status)
        st.dataframe(status_df, use_container_width=True)
        
        # Combine all processed files
        if processed_files:
            combined_df = pd.concat(processed_files, ignore_index=True)
            combined_df = combined_df.sort_values('Time')
            combined_df = combined_df.drop_duplicates(subset=['Time'])
            
            # Store in session state
            st.session_state['call_data'] = combined_df
            
            # Display summary statistics
            st.subheader("Combined Data Summary")
            
            # Calculate metrics for combined data
            combined_metrics = calculate_data_quality_metrics(combined_df)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", f"{combined_metrics['total_records']:,}")
            with col2:
                st.metric("Date Range", f"{combined_metrics['date_range_start'].strftime('%Y-%m-%d')} to {combined_metrics['date_range_end'].strftime('%Y-%m-%d')}")
            with col3:
                st.metric("Total Calls", f"{combined_metrics['total_calls']:,}")
            
            # Data quality checks
            st.subheader("Data Quality Checks")
            
            # Check for missing values
            missing_values = combined_df.isnull().sum().sum()
            if missing_values > 0:
                st.warning(f"Found {missing_values} missing values in the data")
            else:
                st.success("No missing values found in the data")
            
            # Check for outliers
            if 'outlier_count' in combined_metrics:
                st.info(f"Found {combined_metrics['outlier_count']} potential outliers in the data")
            
            # Visualizations
            st.subheader("Data Overview")
            
            # Call volume distribution
            fig1 = px.histogram(combined_df, x='Total Calls', 
                               title='Call Volume Distribution',
                               nbins=30)
            st.plotly_chart(fig1, use_container_width=True)
            
            # Average call volume by day of week
            combined_df['Day'] = combined_df['Time'].dt.day_name()
            avg_by_day = combined_df.groupby('Day')['Total Calls'].mean().reset_index()
            avg_by_day['Day'] = pd.Categorical(avg_by_day['Day'], 
                                              categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                                              ordered=True)
            avg_by_day = avg_by_day.sort_values('Day')
            
            fig2 = px.bar(avg_by_day, x='Day', y='Total Calls',
                         title='Average Call Volume by Day of Week')
            st.plotly_chart(fig2, use_container_width=True)
            
            # Download combined data
            st.subheader("Download Combined Data")
            csv = combined_df.to_csv(index=False)
            st.download_button(
                label="Download Combined Data as CSV",
                data=csv,
                file_name="combined_call_data.csv",
                mime="text/csv"
            )
        else:
            st.error("No files were successfully processed. Please check the file format and try again.")
    else:
        st.info("Please upload your call data files to begin analysis.")

if __name__ == "__main__":
    data_management_page()
