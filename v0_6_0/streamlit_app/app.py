import streamlit as st

# Initialize session state if it doesn't exist
if 'processed_data' not in st.session_state:
    st.session_state['processed_data'] = {
        'raw_df': None,
        'clean_df': None,
        'daily_pattern': None,
        'data_loaded': False,
        'daily_stats': None
    }

# Page configuration
st.set_page_config(
    page_title="Call Center Analytics",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("Call Center Analytics")
st.write("""
This application provides tools for analyzing call center data, forecasting call volumes, 
and optimizing staffing levels. Use the sidebar to navigate between different features.
""")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    st.write("Version: 0.6.0")
    st.write("Last Updated: 2024-03-19")
    st.write("Status: In Development")
    
    st.header("Getting Started")
    st.write("""
    1. Start with the Data Loader to upload your data
    2. Use Quick Insights to explore patterns
    3. Try the Forecasting tools to predict future volumes
    4. Use the Staffing Calculator to optimize resources
    """)

# Main content
st.header("Features")

# Create three columns for features
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Data Analysis")
    st.write("""
    - Upload and clean your data
    - View daily patterns and trends
    - Analyze key metrics
    - Export processed data
    """)

with col2:
    st.subheader("Forecasting")
    st.write("""
    - Predict future call volumes
    - Analyze seasonal patterns
    - Generate forecasts with confidence intervals
    - Export forecast results
    """)

with col3:
    st.subheader("Optimization")
    st.write("""
    - Calculate optimal staffing levels
    - Simulate different scenarios
    - Analyze service level impacts
    - Generate staffing recommendations
    """)

# Data Status
st.header("Data Status")
if st.session_state['processed_data']['data_loaded']:
    st.success("Data is loaded and ready for analysis")
    if st.session_state['processed_data']['clean_df'] is not None:
        st.write(f"Number of records: {len(st.session_state['processed_data']['clean_df'])}")
else:
    st.warning("No data loaded. Please use the Data Loader page to upload your data.") 