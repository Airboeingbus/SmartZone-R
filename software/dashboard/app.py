import streamlit as st
from pages import analytics, runway_maps, alerts
import sys
sys.path.append(".")

# Modified CSS to only hide specific elements while keeping content visible
hide_elements_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stSidebarNav"] {visibility: hidden;}
        section[data-testid="stSidebar"] > div > div:first-child {display: none;}
        div[data-testid="stToolbar"] {visibility: hidden;}
        div[data-testid="stStatusWidget"] {visibility: hidden;}
        </style>
"""
st.markdown(hide_elements_style, unsafe_allow_html=True)

# Configuration should be set before other Streamlit commands
st.set_page_config(
    page_title="SmartZone-R Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define pages before using them
PAGES = {
    "Analytics": analytics,
    "Runway Maps": runway_maps,
    "Alerts": alerts
}

# Navigation in sidebar
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

# Create a main content area
main_container = st.container()
with main_container:
    # Get and display the selected page
    page = PAGES[selection]
    page.app()
