import streamlit as st
import pandas as pd
import time
import datetime
import numpy as np
import os
import hashlib
import json

# Import page modules
from login_page import show_login_page
from equipment_page import show_equipment_page
from scenario_page import show_scenario_page
from guidelines_page import show_guidelines_page

# Page configuration - Auto full screen and disable everything initially
st.set_page_config(
    page_title="Troubleshooting Guide System",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
def init_session_state():
    defaults = {
        'logged_in': False,
        'username': '',
        'staff_id': '',
        'timer_start': None,
        'timer_running': False,
        'elapsed_time': 0,
        'timer_display': "00:00",
        'active_scenarios': [],
        'selected_equipment': [],
        'num_equipment_fail': 1,
        'alarm_status': {'ats': False, 'fscada': False, 'hmi': False},
        'mor_data': None,
        'scenario_start_time': None,
        'resolution_data': [],
        'current_page': 'equipment',  # equipment, scenario, guidelines
        'equipment_per_page': 12,
        'current_equipment_page': 0,
        'selected_scenarios': []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Enhanced CSS following the design specifications - Light mode with white and blue
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Light mode with white and blue theme */
    .stApp {
        background-color: #ffffff;
        font-family: 'Inter', sans-serif;
        color: #000000;
        height: 100vh;
    }
    
    /* Hide Streamlit elements - disable everything when we open system */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Full screen container - avoid scrolling */
    .main-container {
        height: 100vh;
        padding: 0;
        margin: 0;
        background: #ffffff;
    }
    
    /* Blue color scheme - #003b70 */
    .header-container {
        background: linear-gradient(135deg, #003b70, #0056a3);
        color: white;
        padding: 1rem;
        text-align: center;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        color: white;
    }
    
    .header-date {
        font-size: 1.4rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-weight: 600;
    }
    
    /* Login page styling */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        background: #ffffff;
    }
    
    .login-box {
        background: #f8f9fa;
        border: 2px solid #003b70;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,59,112,0.2);
    }
    
    .login-title {
        color: #000000;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .sidebar-container {
        background: #f8f9fa;
        border-right: 2px solid #dee2e6;
        height: 50px;
        padding: 1rem;
    }
    
    /* Fixed sidebar width */
    .css-1d391kg, .css-1lcbmhc, .css-17eq0hr {
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
    }
    
    section[data-testid="stSidebar"] {
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
    }
    
    section[data-testid="stSidebar"] > div {
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
    }
    
    .sidebar-welcome {
        background: linear-gradient(135deg, #003b70, #0056a3);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: 600;
    }
    
    /* Equipment selection boxes - based on wireframe */
    .equipment-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .equipment-box {
        background: #ffffff;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9rem;
        font-weight: 500;
        min-height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #000000;
    }
    
    .equipment-box:hover {
        border-color: #003b70;
        background: #f8f9fa;
        transform: translateY(-2px);
    }
    
    .equipment-box.selected {
        border-color: #003b70;
        background: linear-gradient(135deg, #003b70, #0056a3);
        color: white;
    }
    
    /* Failure scenario boxes - based on wireframe classification */
    .scenario-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .scenario-box {
        background: #ffffff;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        min-height: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        color: #000000;
    }
    
    .scenario-box.major {
        border-color: #dc3545;
        background: #fff5f5;
    }
    
    .scenario-box.major:hover {
        background: #ffe6e6;
        border-color: #c82333;
    }
    
    .scenario-box.minor {
        border-color: #fd7e14;
        background: #fff8f0;
    }
    
    .scenario-box.minor:hover {
        background: #ffe8d1;
        border-color: #e0690c;
    }
    
    /* Alarm indicators - based on wireframe */
    .alarm-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #dee2e6;
    }
    
    .alarm-indicator {
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 600;
        text-align: center;
        min-width: 80px;
    }
    
    .alarm-active {
        background: #dc3545;
        color: white;
        animation: blink 1s infinite;
    }
    
    .alarm-inactive {
        background: #28a745;
        color: white;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
    
    /* Guidelines table - based on wireframe */
    .guidelines-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        background: #ffffff;
    }
    
    .guidelines-table th {
        background: #003b70;
        color: white;
        padding: 0.75rem;
        text-align: center;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .guidelines-table td {
        padding: 0.75rem;
        border: 1px solid #dee2e6;
        vertical-align: top;
        font-size: 0.85rem;
        line-height: 1.4;
        color: #000000;
        background: #ffffff;
    }
    
    .guidelines-table .row-header {
        background: #f8f9fa;
        font-weight: 600;
        text-align: center;
        width: 50px;
    }
    
    /* Timer display - Fixed and working */
    .timer-display {
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #003b70, #0056a3);
        color: white;
        padding: 1rem 2rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1.8rem;
        box-shadow: 0 4px 15px rgba(0,59,112,0.3);
        z-index: 1000;
        min-width: 120px;
        text-align: center;
    }
    
    /* Buttons - More specific selectors to override Streamlit defaults */
    .stButton > button, 
    .stButton button,
    div[data-testid="stButton"] > button,
    .element-container .stButton > button {
        background: linear-gradient(135deg, #003b70, #0056a3) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 200px !important;          /* Fixed width */
        min-width: 200px !important;      /* Fixed width */
        max-width: 200px !important;      /* Fixed width */
        box-shadow: 0 2px 8px rgba(0,59,112,0.2) !important;
        font-size: 0.9rem !important;
        white-space: nowrap !important;   /* Prevent text wrapping */
        overflow: hidden !important;      /* Hide overflow text */
        text-overflow: ellipsis !important; /* Show ... for long text */
        display: block !important;
        margin: 0 auto !important;       /* Center the button */
    }
    
    .stButton > button:hover,
    .stButton button:hover,
    div[data-testid="stButton"] > button:hover,
    .element-container .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0,59,112,0.3) !important;
        color: #ffffff !important;
    }
    
    /* Equipment selection buttons - specific styling with higher specificity */
    .stButton > button[kind="secondary"],
    .stButton button[kind="secondary"],
    div[data-testid="stButton"] > button[kind="secondary"],
    .element-container .stButton > button[kind="secondary"] {
        background: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #dee2e6 !important;
        font-weight: 500 !important;
        width: 250px !important;
        min-width: 250px !important;
        max-width: 250px !important;
        height: auto !important;
        min-height: 50px !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        padding: 0.75rem 0.5rem !important;
        line-height: 1.2 !important;
        text-align: center !important;
    }
    
    .stButton > button[kind="secondary"]:hover,
    .stButton button[kind="secondary"]:hover,
    div[data-testid="stButton"] > button[kind="secondary"]:hover,
    .element-container .stButton > button[kind="secondary"]:hover {
        background: #f8f9fa !important;
        color: #000000 !important;
        border-color: #adb5bd !important;
        height: auto !important;
        min-height: 50px !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        padding: 0.75rem 0.5rem !important;
        line-height: 1.2 !important;
        text-align: center !important;
    }
    
    .stButton > button[kind="primary"],
    .stButton button[kind="primary"], 
    div[data-testid="stButton"] > button[kind="primary"],
    .element-container .stButton > button[kind="primary"] {
        background: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #fd7e14 !important;
        font-weight: 600 !important;
        width: 250px !important;
        min-width: 250px !important;
        max-width: 250px !important;
        height: auto !important;
        min-height: 50px !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        padding: 0.75rem 0.5rem !important;
        line-height: 1.2 !important;
        text-align: center !important;
    }
    
    .stButton > button[kind="primary"]:hover,
    .stButton button[kind="primary"]:hover,
    div[data-testid="stButton"] > button[kind="primary"]:hover,
    .element-container .stButton > button[kind="primary"]:hover {
        background: #f8f9fa !important;
        color: #000000 !important;
        border: 2px solid #fd7e14 !important;
        transform: translateY(-2px) !important;
        height: auto !important;
        min-height: 50px !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        padding: 0.75rem 0.5rem !important;
        line-height: 1.2 !important;
        text-align: center !important;
    }
    
    /* Disabled button styling with high specificity */
    .stButton > button:disabled,
    .stButton button:disabled,
    div[data-testid="stButton"] > button:disabled,
    .element-container .stButton > button:disabled {
        background: #6c757d !important;
        color: #dee2e6 !important;
        border-color: #6c757d !important;
        opacity: 0.6 !important;
        cursor: not-allowed !important;
        transform: none !important;
        width: 250px !important;
        min-width: 250px !important;
        max-width: 250px !important;
        height: auto !important;
        min-height: 50px !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        padding: 0.75rem 0.5rem !important;
        line-height: 1.2 !important;
        text-align: center !important;
    }
    
    .stButton > button:disabled:hover,
    .stButton button:disabled:hover,
    div[data-testid="stButton"] > button:disabled:hover,
    .element-container .stButton > button:disabled:hover {
        background: #6c757d !important;
        color: #dee2e6 !important;
        transform: none !important;
        height: auto !important;
        min-height: 50px !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        padding: 0.75rem 0.5rem !important;
        line-height: 1.2 !important;
        text-align: center !important;
    }
    
    /* Section headers */
    .section-header {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 0.75rem;
        margin: 1rem 0 0.5rem 0;
        font-weight: 600;
        color: #000000;
        text-align: center;
    }
    
    /* Equipment section headers */
    .equipment-section-header {
        background: linear-gradient(135deg, #003b70, #0056a3);
        color: white;
        border-radius: 8px;
        padding: 0.75rem;
        margin: 1rem 0 0.5rem 0;
        font-weight: 600;
        text-align: left;
        font-size: 1.1rem;
    }
    
    /* Step indicator */
    .step-indicator {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 1rem 0;
        gap: 1rem;
    }
    
    .step {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .step.active {
        background: linear-gradient(135deg, #003b70, #0056a3);
        color: white;
    }
    
    .step.completed {
        background: #28a745;
        color: white;
    }
    
    .step.inactive {
        background: #e9ecef;
        color: #6c757d;
    }
    
    /* Responsive adjustments */
    @media (max-width: 1200px) {
        .equipment-container {
            grid-template-columns: repeat(3, 1fr);
        }
        
        .scenario-container {
            grid-template-columns: 1fr;
        }
        
        .header-title {
            font-size: 1.8rem;
        }
        
        .header-date {
            font-size: 1.2rem;
        }
        
        .timer-display {
            font-size: 1.6rem;
            padding: 0.8rem 1.5rem;
        }
    }
    
    @media (max-width: 768px) {
        .equipment-container {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .timer-display {
            position: relative;
            top: auto;
            right: auto;
            margin: 1rem auto;
            display: block;
            width: fit-content;
            font-size: 1.4rem;
            padding: 0.7rem 1.2rem;
        }
        
        .header-title {
            font-size: 1.6rem;
        }
        
        .header-date {
            font-size: 1rem;
        }
        
        .equipment-section-header {
            font-size: 1rem;
        }
    }
    
    /* Input styling */
    .stNumberInput > div > div > input {
        border: 2px solid #dee2e6;
        border-radius: 8px;
        padding: 0.5rem;
        font-size: 1rem;
        background: #ffffff;
        color: #000000;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #003b70;
        box-shadow: 0 0 0 0.2rem rgba(0,59,112,0.25);
    }
    
    /* Streamlit text input styling */
    .stTextInput > div > div > input {
        background: #ffffff;
        border: 2px solid #dee2e6;
        color: #000000;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #003b70;
    }
    
    /* Text input label styling - make labels black */
    .stTextInput > label {
        color: #000000 !important;
        font-weight: 500;
    }
    
    /* Alternative selector for text input labels */
    .stTextInput label {
        color: #000000 !important;
    }
    
    /* Ensure all form labels are black */
    .stForm label, .stTextInput label, .stNumberInput label {
        color: #000000 !important;
    }
    
    /* Success container styling - dark text instead of white */
    .stAlert[data-baseweb="notification"] {
        background-color: #d4edda !important;
        border-color: #c3e6cb !important;
        color: #155724 !important;
    }
    
    .stAlert[data-baseweb="notification"] .st-emotion-cache-1blx69w {
        color: #155724 !important;
    }
    
    .stAlert[data-baseweb="notification"] div {
        color: #155724 !important;
    }
    
    .stSuccess {
        background-color: #d4edda !important;
        border: 1px solid #c3e6cb !important;
        color: #155724 !important;
    }
    
    .stSuccess > div {
        color: #155724 !important;
    }
    
    .stSuccess p {
        color: #155724 !important;
        font-weight: 600 !important;
    }
    
    .element-container .stAlert {
        background-color: #d4edda !important;
        color: #155724 !important;
        border-left: 4px solid #28a745 !important;
    }
    
    .element-container .stAlert div {
        color: #155724 !important;
    }
</style>
""", unsafe_allow_html=True)

# Timer update function - Pure Python
def update_timer():
    if st.session_state.timer_running and st.session_state.timer_start:
        elapsed = time.time() - st.session_state.timer_start
        minutes, seconds = divmod(int(elapsed), 60)
        st.session_state.timer_display = f"{minutes:02d}:{seconds:02d}"
        st.session_state.elapsed_time = elapsed
        
        # Alert at 3 minutes for decision making
        if int(elapsed) == 180:  # 3 minutes
            st.toast("⚠️ 3 minutes elapsed - Decision making time!", icon="⚠️")
        
        # Alert at 5 minutes but keep timer continue
        if int(elapsed) == 300:  # 5 minutes
            st.toast("🚨 5 minutes elapsed - Critical time reached!", icon="🚨")

# Authentication function
def authenticate_user(staff_id, password):
    """Simulate authentication - replace with actual backend"""
    valid_users = {
        "TGS001": {"password": "admin123", "name": "Ahmad Rahman"},
        "TGS002": {"password": "tech456", "name": "Sarah Lee"},
        "TGS003": {"password": "ops789", "name": "Kumar Raj"}
    }
    
    if staff_id in valid_users and valid_users[staff_id]["password"] == password:
        return valid_users[staff_id]["name"]
    return None

def save_resolution_data():
    """Save resolution data to CSV"""
    if not st.session_state.active_scenarios:
        return
    
    end_time = datetime.datetime.now()
    
    for scenario in st.session_state.active_scenarios:
        # Determine status based on 5-minute rule
        status = "Resolved" if st.session_state.elapsed_time <= 300 else "Failed"
        
        resolution_data = {
            "Staff ID": st.session_state.staff_id,
            "Start Time": st.session_state.scenario_start_time.strftime("%Y-%m-%d %H:%M:%S") if st.session_state.scenario_start_time else "",
            "Stop Time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Equipment": scenario.get('Equipment', 'N/A'),
            "Failure Scenario": scenario.get('Failure Scenario', 'N/A'),
            "Status": status,
            "Guideline for Chief Controller": scenario.get('Guidelines for the Chief Controller', 'N/A'),
            "Local Response": scenario.get('Local Response', 'N/A'),
            "Duration (min)": round(st.session_state.elapsed_time / 60, 1)
        }
        
        # Save to CSV
        filename = "tgs_resolution_history.csv"
        try:
            if os.path.exists(filename):
                df = pd.read_csv(filename)
                df = pd.concat([df, pd.DataFrame([resolution_data])], ignore_index=True)
            else:
                df = pd.DataFrame([resolution_data])
            
            df.to_csv(filename, index=False)
            
        except Exception as e:
            st.error(f"Error saving data: {str(e)}")

def show_step_indicator():
    """Show step progress indicator"""
    # Check if mor_data exists and is not empty
    data_uploaded = st.session_state.mor_data is not None and not st.session_state.mor_data.empty
    equipment_selected = len(st.session_state.selected_equipment) > 0
    scenario_selected = len(st.session_state.active_scenarios) > 0
    
    steps = {
        'equipment': {'name': '🔧 Equipment', 'status': 'completed' if equipment_selected else ('active' if st.session_state.current_page == 'equipment' else 'inactive')},
        'scenario': {'name': '⚠️ Scenario', 'status': 'completed' if scenario_selected else ('active' if st.session_state.current_page == 'scenario' else 'inactive')},
        'guidelines': {'name': '📖 Guidelines', 'status': 'active' if st.session_state.current_page == 'guidelines' else 'inactive'}
    }
    
    # Override status for current page
    if st.session_state.current_page in steps:
        if steps[st.session_state.current_page]['status'] == 'inactive':
            steps[st.session_state.current_page]['status'] = 'active'
    
    step_html = '<div class="step-indicator">'
    for page, info in steps.items():
        step_html += f'<div class="step {info["status"]}">{info["name"]}</div>'
    step_html += '</div>'
    
    st.markdown(step_html, unsafe_allow_html=True)

def show_download_history():
    """Download history functionality"""
    filename = "tgs_resolution_history.csv"
    
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename)
            
            # Filter by current user
            user_df = df[df['Staff ID'] == st.session_state.staff_id]
            
            if not user_df.empty:
                csv = user_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Your History",
                    data=csv,
                    file_name=f"TGS_History_{st.session_state.staff_id}_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No history found for your account")
                
        except Exception as e:
            st.error(f"Error loading history: {str(e)}")
    else:
        st.info("No history file found")

# Main application logic - Simple Python Timer
def main():
    update_timer()
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_main_interface()

def show_main_interface():
    # Sidebar - based on wireframe
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-welcome">
            👤 Welcome<br>
            <strong>{st.session_state.username}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown("### 📋 Navigation")
        if st.button("🔧 Select Equipment", key="nav_equipment"):
            st.session_state.current_page = 'equipment'
            st.rerun()
        
        if len(st.session_state.selected_equipment) > 0:
            if st.button("⚠️ Failure Scenarios", key="nav_scenario"):
                st.session_state.current_page = 'scenario'
                st.rerun()
        
        if len(st.session_state.active_scenarios) > 0:
            if st.button("📖 Guidelines", key="nav_guidelines"):
                st.session_state.current_page = 'guidelines'
                st.rerun()
        
        st.markdown("---")
        
        if st.button("Logout", key="logout_btn"):
            # Reset all session state variables for complete process reset
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.staff_id = None
            st.session_state.current_page = 'equipment'
            st.session_state.mor_data = None
            st.session_state.num_equipment_fail = 1
            st.session_state.selected_equipment = []
            st.session_state.selected_scenarios = []
            st.session_state.active_scenarios = []
            st.session_state.timer_running = False
            st.session_state.timer_start = None
            st.session_state.timer_display = None
            st.session_state.elapsed_time = 0
            st.session_state.scenario_start_time = None
            if 'alarm_status' in st.session_state:
                del st.session_state.alarm_status
            st.rerun()
        
        if st.button("Download History", key="download_btn"):
            show_download_history()
    
    # Main content area - based on current page
    current_time = datetime.datetime.now()
    st.markdown(f"""
    <div class="header-container">
        <h1 class="header-title">Troubleshooting Guide System</h1>
        <div class="header-date">{current_time.strftime('%d %B %Y')}<br>{current_time.strftime('%H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show step indicator
    show_step_indicator()
    
    # Show different pages based on current_page
    if st.session_state.current_page == 'equipment':
        show_equipment_page()
    elif st.session_state.current_page == 'scenario':
        show_scenario_page()
    elif st.session_state.current_page == 'guidelines':
        show_guidelines_page()

# Run the application
if __name__ == "__main__":
    main()