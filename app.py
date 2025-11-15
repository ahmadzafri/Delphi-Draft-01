import streamlit as st
from pages.main_page import main_page
from pages.builder_page import builder_page
from pages.reporting_page import reporting_page

# Configure page
st.set_page_config(
    page_title="Delphi: CO₂ Emission Simulator",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'
if 'current_project' not in st.session_state:
    st.session_state.current_project = None
if 'facilities_config' not in st.session_state:
    st.session_state.facilities_config = {}
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None
if 'canvas_equipment' not in st.session_state:
    st.session_state.canvas_equipment = []
if 'selected_equipment' not in st.session_state:
    st.session_state.selected_equipment = None
if 'facility_scale' not in st.session_state:
    st.session_state.facility_scale = {"acres": 1, "meters": 4047}
if 'project_saved' not in st.session_state:
    st.session_state.project_saved = True

def main():
    # Hide streamlit style
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Navigation logic
    if st.session_state.current_page == 'main':
        main_page()
    elif st.session_state.current_page == 'builder':
        builder_page()
    elif st.session_state.current_page == 'reporting':
        reporting_page()

if __name__ == "__main__":
    main()