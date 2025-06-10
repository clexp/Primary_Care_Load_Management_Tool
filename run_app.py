import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now run the Streamlit app
if __name__ == "__main__":
    import streamlit.web.bootstrap as bootstrap
    bootstrap.run("streamlit_app/app.py", "", [], flag_options={}) 