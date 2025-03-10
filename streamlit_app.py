import streamlit as st

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

# Add any getting started instructions or overview metrics here
if 'call_data' in st.session_state:
    st.success("Data is loaded! Navigate to 'Quick Insights' to see analysis.")
else:
    st.info("Start by uploading your call data in the 'Data Upload' page.") 