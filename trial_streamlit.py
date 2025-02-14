import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="My First Streamlit App",
    page_icon="👋",
    layout="wide"
)

# Add a title
st.title("Welcome to My First Streamlit App! 👋")

# Add some text
st.write("This is a simple Streamlit app demonstration.")

# Add a sidebar
with st.sidebar:
    st.header("Sidebar")
    name = st.text_input("What's your name?")
    age = st.slider("How old are you?", 0, 100, 25)

# Main content
st.header("Main Content")

# Display input from sidebar
if name:
    st.write(f"Hello, {name}! 👋")
    st.write(f"You are {age} years old.")

# Add some interactive elements
if st.button("Click me!"):
    st.balloons()

# Add two columns
col1, col2 = st.columns(2)

with col1:
    st.header("Column 1")
    st.write("This is the first column")
    
with col2:
    st.header("Column 2")
    st.write("This is the second column") 