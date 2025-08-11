import streamlit as st
import pandas as pd
import time
import datetime
import numpy as np
import os
import hashlib
import json

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
        background: linear-gradient(135deg, #003b70, #0056a3) !important;
        color: #ffffff !important;
        border: 2px solid #003b70 !important;
        font-weight: 600 !important;
        width: 200px !important;
        min-width: 200px !important;
        max-width: 200px !important;
    }
    
    .stButton > button[kind="primary"]:hover,
    .stButton button[kind="primary"]:hover,
    div[data-testid="stButton"] > button[kind="primary"]:hover,
    .element-container .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #004080, #0066b3) !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
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
        width: 200px !important;
        min-width: 200px !important;
        max-width: 200px !important;
    }
    
    .stButton > button:disabled:hover,
    .stButton button:disabled:hover,
    div[data-testid="stButton"] > button:disabled:hover,
    .element-container .stButton > button:disabled:hover {
        background: #6c757d !important;
        color: #dee2e6 !important;
        transform: none !important;
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

# Main application logic - Simple Python Timer
def main():
    update_timer()
    
    # Pure Python Timer Display - Simple approach
    if st.session_state.timer_running and st.session_state.timer_start:
        # Calculate current timer time
        current_time = time.time() - st.session_state.timer_start
        minutes, seconds = divmod(int(current_time), 60)
        timer_display = f"{minutes:02d}:{seconds:02d}"
        
        # Simple timer display - no JavaScript needed!
        st.markdown(f"""
        <div class="timer-display">
            ⏱️ {timer_display}
        </div>
        """, unsafe_allow_html=True)
        
        # Show timer status alerts
        if current_time > 300:  # 5 minutes
            st.error("🚨 Timer exceeded 5 minutes!")
        elif current_time > 180:  # 3 minutes
            st.warning("⚠️ Timer exceeded 3 minutes!")
        
        # Simple auto-refresh: refresh page every 1 second when timer is running
        # This will make the timer count visually: 00:01, 00:02, 00:03...
        time.sleep(1)
        st.rerun()
    
    if not st.session_state.logged_in:
        show_login_page()
    else:
        show_main_interface()

def show_login_page():
    st.markdown("""
    <div class="login-container">
        <div class="login-box">
            <h2 class="login-title">Welcome to<br>Troubleshooting Guide System</h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        staff_id = st.text_input("Staff ID :", placeholder="Enter your Staff ID")
        password = st.text_input("Password :", type="password", placeholder="Enter your password")
        
        if st.button("Login", key="login_btn"):
            if staff_id and password:
                user_name = authenticate_user(staff_id, password)
                if user_name:
                    st.session_state.logged_in = True
                    st.session_state.username = user_name
                    st.session_state.staff_id = staff_id
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            else:
                st.warning("Please enter both Staff ID and password")

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
            st.session_state.logged_in = False
            st.session_state.active_scenarios = []
            st.session_state.timer_running = False
            st.session_state.timer_start = None
            st.session_state.current_page = 'equipment'
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

def show_equipment_page():
    """Page 1: Equipment Selection with Configuration"""
    st.markdown('<div class="section-header">🔧 Step 1: Equipment Configuration & Selection</div>', unsafe_allow_html=True)
    
    # Load default data automatically on first visit
    if st.session_state.mor_data is None:
        try:
            # Load the existing MOR_KGL.xlsx file with proper Excel reading
            df = pd.read_excel('MOR_KGL.xlsx', engine='openpyxl')
            st.session_state.mor_data = df
        except FileNotFoundError:
            # Create sample data with the equipment list provided by user
            sample_data = {
                'Equipment': ['TMS', 'Power', 'Traction', 'Brake', 'Suspension System', 'Train Doors', 'Auxiliary Driving Console', 'Train Coupler', 'Axle', 'Lightning', 'Pneumatic System', 'Air Conditioning Unit', 'Fire/Smoke Sensor', 'Heat Detector', 'Radio', 'IPIS', 'CCTV', 'Train Horn', 'Event Recorder', 'Obstacle Detection', 'Abnormal Noise & Vibration Generated', 'Rollback Detection', 'Failure of Train Wake Up', 'Excessive Wheel Slip/Slide', 'Train Overshoot or Undershoot', 'Foreign object on track', 'VATC', 'Loss of Driving Modes', 'All train doors at APG side not open', 'Trackside ATO', 'Wayside - Train Communication Channel', 'ATS', 'Switch Machine', '750 VDC Switchgear'],
                'Failure Scenario': ['TMS failure', 'Power failure', 'Traction failure', 'Brake failure', 'Suspension failure', 'Door failure', 'Console failure', 'Coupler failure', 'Axle failure', 'Lightning failure', 'Pneumatic failure', 'AC failure', 'Fire sensor failure', 'Heat detector failure', 'Radio failure', 'IPIS failure', 'CCTV failure', 'Horn failure', 'Recorder failure', 'Detection failure', 'Noise/vibration', 'Rollback detected', 'Wake up failure', 'Wheel slip/slide', 'Train positioning error', 'Foreign object detected', 'VATC failure', 'Driving mode loss', 'Door opening failure', 'ATO failure', 'Communication failure', 'ATS failure', 'Switch failure', 'Switchgear failure'],
                'Failure Classification': ['Major'] * 34,
                'Guidelines for the Chief Controller': ['Follow emergency protocol'] * 34,
                'Local Response': ['Immediate action required'] * 34,
                'ATS Alarm Description': ['System alarm'] * 34,
                'FSCADA Alarm Description': ['SCADA alarm'] * 34,
                'HMI Alarm': ['HMI FAULT'] * 34
            }
            df = pd.DataFrame(sample_data)
            st.session_state.mor_data = df
        except Exception as e:
            # Create sample data with the equipment list provided by user
            sample_data = {
                'Equipment': ['TMS', 'Power', 'Traction', 'Brake', 'Suspension System', 'Train Doors', 'Auxiliary Driving Console', 'Train Coupler', 'Axle', 'Lightning', 'Pneumatic System', 'Air Conditioning Unit', 'Fire/Smoke Sensor', 'Heat Detector', 'Radio', 'IPIS', 'CCTV', 'Train Horn', 'Event Recorder', 'Obstacle Detection', 'Abnormal Noise & Vibration Generated', 'Rollback Detection', 'Failure of Train Wake Up', 'Excessive Wheel Slip/Slide', 'Train Overshoot or Undershoot', 'Foreign object on track', 'VATC', 'Loss of Driving Modes', 'All train doors at APG side not open', 'Trackside ATO', 'Wayside - Train Communication Channel', 'ATS', 'Switch Machine', '750 VDC Switchgear'],
                'Failure Scenario': ['TMS failure', 'Power failure', 'Traction failure', 'Brake failure', 'Suspension failure', 'Door failure', 'Console failure', 'Coupler failure', 'Axle failure', 'Lightning failure', 'Pneumatic failure', 'AC failure', 'Fire sensor failure', 'Heat detector failure', 'Radio failure', 'IPIS failure', 'CCTV failure', 'Horn failure', 'Recorder failure', 'Detection failure', 'Noise/vibration', 'Rollback detected', 'Wake up failure', 'Wheel slip/slide', 'Train positioning error', 'Foreign object detected', 'VATC failure', 'Driving mode loss', 'Door opening failure', 'ATO failure', 'Communication failure', 'ATS failure', 'Switch failure', 'Switchgear failure'],
                'Failure Classification': ['Major'] * 34,
                'Guidelines for the Chief Controller': ['Follow emergency protocol'] * 34,
                'Local Response': ['Immediate action required'] * 34,
                'ATS Alarm Description': ['System alarm'] * 34,
                'FSCADA Alarm Description': ['SCADA alarm'] * 34,
                'HMI Alarm': ['HMI FAULT'] * 34
            }
            df = pd.DataFrame(sample_data)
            st.session_state.mor_data = df
    
    # Equipment failure selection - centered and prominent
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='color: black;'>How many equipment can fail?</h3>", unsafe_allow_html=True)
        num_equipment = st.number_input(
            "",
            min_value=1,
            max_value=5,
            value=st.session_state.num_equipment_fail,
            key="num_equipment_input"
        )
        st.session_state.num_equipment_fail = num_equipment
    
    # Check if data is properly loaded
    if st.session_state.mor_data is None or st.session_state.mor_data.empty:
        st.error("No equipment data available!")
        return
    
    df = st.session_state.mor_data
    equipment_list = df['Equipment'].unique().tolist()
    equipment_list = [eq for eq in equipment_list if pd.notna(eq)]
    
    if len(equipment_list) == 0:
        st.error("No equipment found in the data!")
        return
    
    # Selection status display
    current_selected = len(st.session_state.selected_equipment)
    max_allowed = st.session_state.num_equipment_fail
    
    # Color-coded selection status
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if current_selected == max_allowed:
            st.markdown(f"**Selected: {current_selected}/{max_allowed}** ✅ **MAX REACHED**")
        elif current_selected > 0:
            st.markdown(f"**Selected: {current_selected}/{max_allowed}** 🔄 **{max_allowed - current_selected} more allowed**")
        else:
            st.markdown(f"**Selected: {current_selected}/{max_allowed}** 🆕 **Select equipment to continue**")
    
    # Show info message when max reached
    if len(st.session_state.selected_equipment) >= st.session_state.num_equipment_fail:
        st.info("ℹ️ Maximum equipment selected. Unselected buttons are disabled. Deselect to choose different equipment.")
    
    # Check if max selection reached
    max_reached = len(st.session_state.selected_equipment) >= st.session_state.num_equipment_fail
    
    # Equipment grid - display all equipment
    cols_per_row = 4
    total_equipment = len(equipment_list)
    rows = (total_equipment + cols_per_row - 1) // cols_per_row
    
    for row in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            equipment_idx = row * cols_per_row + col_idx
            if equipment_idx < total_equipment:
                equipment = equipment_list[equipment_idx]
                with cols[col_idx]:
                    # Determine button state
                    is_selected = equipment in st.session_state.selected_equipment
                    button_color = "primary" if is_selected else "secondary"
                    
                    # Disable button if max reached and not already selected
                    button_disabled = max_reached and not is_selected
                    
                    if st.button(
                        equipment,
                        key=f"equipment_{equipment_idx}",
                        type=button_color,
                        help=f"Select {equipment} equipment" if not button_disabled else f"Maximum {st.session_state.num_equipment_fail} equipment limit reached",
                        disabled=button_disabled
                    ):
                        if equipment not in st.session_state.selected_equipment and len(st.session_state.selected_equipment) < st.session_state.num_equipment_fail:
                            st.session_state.selected_equipment.append(equipment)
                            st.success(f"✅ {equipment} selected!")
                        elif equipment in st.session_state.selected_equipment:
                            st.session_state.selected_equipment.remove(equipment)
                            st.info(f"❌ {equipment} deselected!")
                        st.rerun()
    
    # Show selected equipment
    if len(st.session_state.selected_equipment) > 0:
        st.markdown('<div class="section-header">Selected Equipment:</div>', unsafe_allow_html=True)
        
        # Simple approach - use success boxes for selected equipment
        for equipment in st.session_state.selected_equipment:
            st.success(f"🔧 **{equipment}** - Selected")
        
        st.markdown("---")
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            # Change equipment count button
            if st.button("🔄 Change Count", key="change_count"):
                # Reset selections when changing count
                st.session_state.selected_equipment = []
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All", key="clear_all"):
                st.session_state.selected_equipment = []
                st.rerun()
        
        with col3:
            if st.button("➡️ Next: Scenarios", key="goto_scenario", type="primary"):
                st.session_state.current_page = 'scenario'
                st.rerun()

def show_scenario_page():
    """Page 3: Failure Scenario Selection"""
    
    st.markdown('<div class="section-header">⚠️ Step 3: Select Failure Scenario</div>', unsafe_allow_html=True)
    
    # Initialize selected scenarios if not exists
    if 'selected_scenarios' not in st.session_state:
        st.session_state.selected_scenarios = []
    
    if len(st.session_state.selected_equipment) == 0:
        st.error("Please select equipment first!")
        if st.button("⬅️ Back to Equipment", key="back_to_equipment_error"):
            st.session_state.current_page = 'equipment'
            st.rerun()
        return
    
    if st.session_state.mor_data is None or st.session_state.mor_data.empty:
        st.error("No data available!")
        return
    
    df = st.session_state.mor_data
    
    # Show instruction
    st.info("📋 Please select TWO failure scenarios (one from each equipment) before proceeding to guidelines.")
    
    # Show selected scenarios count with compact styling
    if len(st.session_state.selected_scenarios) > 0:
        st.markdown(f'<div class="section-header" style="margin-bottom: 0.5rem;">Selected Scenarios: {len(st.session_state.selected_scenarios)}/2</div>', unsafe_allow_html=True)
        
        # Create a more compact display for selected scenarios
        scenarios_html = ""
        for idx, scenario in enumerate(st.session_state.selected_scenarios):
            classification = scenario.get('Failure Classification', '').strip()
            class_color = '#dc3545' if 'major' in classification.lower() else '#fd7e14'
            class_text = 'MAJOR' if 'major' in classification.lower() else 'MINOR'
            
            scenarios_html += f'''
            <div style="
                background: #f8f9fa;
                border-left: 3px solid {class_color};
                padding: 0.4rem 0.6rem;
                margin: 0.2rem 0;
                border-radius: 3px;
                font-size: 0.85rem;
                line-height: 1.3;
            ">
                <strong style="color: #2c3e50;">{scenario.get('Equipment', 'N/A')}:</strong> {scenario.get('Failure Scenario', 'N/A')}
                <span style="background: {class_color}; color: white; padding: 0.15rem 0.4rem; border-radius: 8px; font-size: 0.65rem; font-weight: bold; margin-left: 0.3rem;">{class_text}</span>
            </div>
            '''
        
        st.markdown(scenarios_html, unsafe_allow_html=True)
        st.markdown('<div style="margin: 0.5rem 0; border-top: 1px solid #dee2e6;"></div>', unsafe_allow_html=True)
    
    # Create columns for equipment side by side with optimized spacing
    num_equipment = len(st.session_state.selected_equipment)
    if num_equipment == 1:
        # Use full width for single equipment with minimal side margins
        col1, col2, col3 = st.columns([0.5, 4, 0.5])
        with col2:
            cols = [st.container()]
    elif num_equipment == 2:
        cols = st.columns([1, 1], gap="small")
    elif num_equipment == 3:
        cols = st.columns([1, 1, 1], gap="small")
    else:
        cols = st.columns(min(num_equipment, 4), gap="small")  # Max 4 columns
    
    # Show scenarios grouped by equipment side by side
    for eq_idx, equipment in enumerate(st.session_state.selected_equipment):
         if num_equipment == 1:
             # Special handling for single equipment
             with cols[0]:
                 st.markdown(f'<div class="equipment-section-header">🔧 {equipment}</div>', unsafe_allow_html=True)
                 
                 equipment_scenarios = df[df['Equipment'] == equipment].to_dict('records')
                 
                 if equipment_scenarios:
                     # Sort scenarios: MAJOR first, then MINOR
                     sorted_scenarios = sorted(equipment_scenarios, key=lambda x: (0 if 'major' in x.get('Failure Classification', '').lower() else 1, x.get('Failure Scenario', '')))
                     
                     for i, scenario in enumerate(sorted_scenarios):
                         classification = scenario.get('Failure Classification', '').strip()
                         scenario_text = scenario.get('Failure Scenario', 'Unknown')
                         
                         # Create classification indicator
                         if 'major' in classification.lower():
                             class_color = '#dc3545'  # Red for major
                             class_text = 'MAJOR'
                         else:
                             class_color = '#fd7e14'  # Orange for minor
                             class_text = 'MINOR'
                         
                         # Check if this scenario is already selected
                         is_selected = any(s.get('Equipment') == equipment and s.get('Failure Scenario') == scenario_text for s in st.session_state.selected_scenarios)
                         
                         # Display classification badge with compact styling
                         st.markdown(f'''
                         <div style="
                             background: {class_color};
                             color: white;
                             padding: 0.2rem 0.6rem;
                             border-radius: 12px;
                             font-size: 0.7rem;
                             font-weight: bold;
                             text-align: center;
                             margin-bottom: 0.3rem;
                             display: inline-block;
                             width: fit-content;
                             box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                         ">
                             {class_text}
                         </div>
                         ''', unsafe_allow_html=True)
                         
                         # Create scenario button
                         scenario_id = f"scenario_{equipment}_{i}"
                         button_label = f"✅ {scenario_text}" if is_selected else scenario_text
                         button_type = "primary" if is_selected else "secondary"
                         
                         if st.button(
                             button_label,
                             key=scenario_id,
                             help=f"Classification: {classification}",
                             use_container_width=False,
                             type=button_type
                         ):
                             # Toggle scenario selection
                             if is_selected:
                                 # Remove from selected scenarios
                                 st.session_state.selected_scenarios = [s for s in st.session_state.selected_scenarios 
                                                                      if not (s.get('Equipment') == equipment and s.get('Failure Scenario') == scenario_text)]
                                 st.info(f"❌ Scenario deselected from {equipment}")
                             else:
                                 # Check if we can add more scenarios
                                 if len(st.session_state.selected_scenarios) < 2:
                                     st.session_state.selected_scenarios.append(scenario)
                                     st.success(f"✅ Scenario selected from {equipment}")
                                 else:
                                     st.warning("⚠️ You can only select 2 scenarios maximum.")
                             st.rerun()
                         
                         st.markdown('<div style="margin-bottom: 0.3rem;"></div>', unsafe_allow_html=True)
                 else:
                     st.info(f"No scenarios found for {equipment}")
         else:
             # Handle multiple equipment
             with cols[eq_idx % len(cols)]:
                 st.markdown(f'<div class="equipment-section-header">🔧 {equipment}</div>', unsafe_allow_html=True)
                 
                 equipment_scenarios = df[df['Equipment'] == equipment].to_dict('records')
                 
                 if equipment_scenarios:
                     # Sort scenarios: MAJOR first, then MINOR
                     sorted_scenarios = sorted(equipment_scenarios, key=lambda x: (0 if 'major' in x.get('Failure Classification', '').lower() else 1, x.get('Failure Scenario', '')))
                     
                     for i, scenario in enumerate(sorted_scenarios):
                         classification = scenario.get('Failure Classification', '').strip()
                         scenario_text = scenario.get('Failure Scenario', 'Unknown')
                         
                         # Create classification indicator
                         if 'major' in classification.lower():
                             class_color = '#dc3545'  # Red for major
                             class_text = 'MAJOR'
                         else:
                             class_color = '#fd7e14'  # Orange for minor
                             class_text = 'MINOR'
                         
                         # Check if this scenario is already selected
                         is_selected = any(s.get('Equipment') == equipment and s.get('Failure Scenario') == scenario_text for s in st.session_state.selected_scenarios)
                         
                         # Display classification badge with compact styling
                         st.markdown(f'''
                         <div style="
                             background: {class_color};
                             color: white;
                             padding: 0.2rem 0.6rem;
                             border-radius: 12px;
                             font-size: 0.7rem;
                             font-weight: bold;
                             text-align: center;
                             margin-bottom: 0.3rem;
                             display: inline-block;
                             width: fit-content;
                             box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                         ">
                             {class_text}
                         </div>
                         ''', unsafe_allow_html=True)
                         
                         # Create scenario button
                         scenario_id = f"scenario_{equipment}_{i}"
                         button_type = "primary" if is_selected else "secondary"
                         button_label = f"✅ {scenario_text}" if is_selected else scenario_text
                         
                         if st.button(
                             button_label,
                             key=scenario_id,
                             help=f"Classification: {classification}",
                             use_container_width=True,
                             type=button_type
                         ):
                             # Toggle scenario selection
                             if is_selected:
                                 # Remove from selected scenarios
                                 st.session_state.selected_scenarios = [s for s in st.session_state.selected_scenarios 
                                                                      if not (s.get('Equipment') == equipment and s.get('Failure Scenario') == scenario_text)]
                                 st.info(f"❌ Scenario deselected from {equipment}")
                             else:
                                 # Check if we can add more scenarios
                                 if len(st.session_state.selected_scenarios) < 2:
                                     # Check if equipment already has a selected scenario
                                     equipment_has_selection = any(s.get('Equipment') == equipment for s in st.session_state.selected_scenarios)
                                     if not equipment_has_selection:
                                         st.session_state.selected_scenarios.append(scenario)
                                         st.success(f"✅ Scenario selected from {equipment}")
                                     else:
                                         st.warning(f"⚠️ You can only select one scenario per equipment. Please deselect the current scenario from {equipment} first.")
                                 else:
                                     st.warning("⚠️ You can only select 2 scenarios maximum.")
                             st.rerun()
                         
                         st.markdown('<div style="margin-bottom: 0.3rem;"></div>', unsafe_allow_html=True)
                 else:
                     st.info(f"No scenarios found for {equipment}")
    
    # Compact navigation section
    st.markdown('<div style="margin: 0.8rem 0; border-top: 1px solid #dee2e6; padding-top: 0.8rem;"></div>', unsafe_allow_html=True)
    
    # Create a more compact navigation layout
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("⬅️ Back", key="back_to_equipment"):
            st.session_state.current_page = 'equipment'
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear", key="clear_scenarios"):
            st.session_state.selected_scenarios = []
            st.rerun()
    
    with col3:
        # Show selection status with compact styling
        status_color = "#28a745" if len(st.session_state.selected_scenarios) == 2 else "#6c757d"
        status_bg = "#d4edda" if len(st.session_state.selected_scenarios) == 2 else "#f8f9fa"
        st.markdown(f'''
        <div style="
            text-align: center; 
            padding: 0.4rem 0.6rem; 
            font-size: 0.75rem; 
            color: {status_color}; 
            background: {status_bg};
            border: 1px solid {status_color};
            border-radius: 4px;
            font-weight: bold;
            margin: 0.2rem 0;
        ">
            Status: {len(st.session_state.selected_scenarios)}/2
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        # Only allow proceeding if exactly 2 scenarios are selected
        if len(st.session_state.selected_scenarios) == 2:
            if st.button("➡️ Guidelines", key="goto_guidelines", type="primary"):
                st.session_state.active_scenarios = st.session_state.selected_scenarios
                # Start timer when entering guidelines page
                st.session_state.timer_start = time.time()
                st.session_state.timer_running = True
                st.session_state.scenario_start_time = datetime.datetime.now()
                
                # Set alarm status based on both scenarios
                st.session_state.alarm_status = {
                    'ats': any(scenario.get('ATS Alarm Description', '') not in ['N/A', '', 'No alarm triggered'] for scenario in st.session_state.selected_scenarios),
                    'fscada': any(scenario.get('FSCADA Alarm Description', '') not in ['N/A', '', 'No alarm triggered'] for scenario in st.session_state.selected_scenarios),
                    'hmi': any(scenario.get('HMI Alarm', '') not in ['N/A', '', 'No alarm triggered'] for scenario in st.session_state.selected_scenarios)
                }
                st.session_state.current_page = 'guidelines'
                st.rerun()
        else:
            st.button("➡️ Guidelines", key="goto_guidelines_disabled", disabled=True, help="Please select exactly 2 scenarios first")

def show_guidelines_page():
    """Page 4: Guidelines and Timer"""
    st.markdown('<div class="section-header">📖 Step 4: Follow Guidelines</div>', unsafe_allow_html=True)
    
    if len(st.session_state.active_scenarios) == 0:
        st.error("Please select a scenario first!")
        if st.button("⬅️ Back to Scenarios", key="back_to_scenario_error"):
            st.session_state.current_page = 'scenario'
            st.rerun()
        return
    
    # Layout based on wireframe design
    # Top section: Equipment and Failure Scenario boxes side by side
    col1, col2 = st.columns(2)
    
    with col1:
        # Equipment box
        equipment_text = ""
        for i, scenario in enumerate(st.session_state.active_scenarios, 1):
            equipment_text += f"{i}. {scenario.get('Equipment', 'N/A')}\n"
        
        st.markdown(f'''
        <div style="
            border: 2px solid #000;
            padding: 1rem;
            margin: 0.5rem 0;
            background: white;
            border-radius: 8px;
        ">
            <div style="font-weight: bold; margin-bottom: 0.5rem;">Equipment :</div>
            <div style="min-height: 60px; padding: 0.5rem; border: 1px solid #ccc; background: #f9f9f9;">
                {equipment_text.strip()}
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        # Failure Scenario box
        scenario_text = ""
        for i, scenario in enumerate(st.session_state.active_scenarios, 1):
            scenario_text += f"{i}. {scenario.get('Failure Scenario', 'N/A')}\n"
        
        st.markdown(f'''
        <div style="
            border: 2px solid #000;
            padding: 1rem;
            margin: 0.5rem 0;
            background: white;
            border-radius: 8px;
        ">
            <div style="font-weight: bold; margin-bottom: 0.5rem;">Failure Scenario :</div>
            <div style="min-height: 60px; padding: 0.5rem; border: 1px solid #ccc; background: #f9f9f9;">
                {scenario_text.strip()}
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Alarm Status section
    st.markdown('<div style="margin: 1rem 0;"><strong>Alarm Status :</strong></div>', unsafe_allow_html=True)
    
    alarm_col1, alarm_col2, alarm_col3 = st.columns(3)
    
    # Collect all alarm data from both scenarios
    all_alarms = {
        'ATS': [],
        'FSCADA': [], 
        'HMI': []
    }
    
    for scenario in st.session_state.active_scenarios:
        ats_alarm = scenario.get('ATS Alarm Description', 'N/A')
        fscada_alarm = scenario.get('FSCADA Alarm Description', 'N/A')
        hmi_alarm = scenario.get('HMI Alarm', 'N/A')
        
        if ats_alarm not in ['N/A', '', 'No alarm triggered', None] and pd.notna(ats_alarm):
            all_alarms['ATS'].append(ats_alarm)
        if fscada_alarm not in ['N/A', '', 'No alarm triggered', None] and pd.notna(fscada_alarm):
            all_alarms['FSCADA'].append(fscada_alarm)
        if hmi_alarm not in ['N/A', '', 'No alarm triggered', None] and pd.notna(hmi_alarm):
            all_alarms['HMI'].append(hmi_alarm)
    
    alarms = [
        ('ATS', all_alarms['ATS']),
        ('FSCADA', all_alarms['FSCADA']),
        ('HMI', all_alarms['HMI'])
    ]
    
    for i, (system, alarm_list) in enumerate(alarms):
        with [alarm_col1, alarm_col2, alarm_col3][i]:
            # Only blink if there are actual alarms
            if len(alarm_list) > 0:
                alarm_class = "alarm-active"  # This will have blinking animation
                alarm_text = "<br>".join(alarm_list)
            else:
                alarm_class = "alarm-inactive"  # No blinking
                alarm_text = "No alarm triggered"
            
            st.markdown(f'''
            <div class="alarm-indicator {alarm_class}">
                {system}
            </div>
            <div style="font-size: 0.8rem; margin-top: 0.5rem; text-align: center;">
                {alarm_text}
            </div>
            ''', unsafe_allow_html=True)
    
    # Guidelines Table
    st.markdown('<div class="section-header">📋 Guidelines:</div>', unsafe_allow_html=True)
    
    scenario = st.session_state.active_scenarios[0]  # Use first scenario for guidelines
    guidelines = scenario.get('Guidelines for the Chief Controller', 'N/A')
    local_response = scenario.get('Local Response', 'N/A')
    
    # Parse guidelines
    train_entering = ""
    train_in_service = ""
    note = ""
    
    if guidelines != 'N/A' and guidelines.strip():
        if 'Train Entering service:' in guidelines:
            parts = guidelines.split('Train Entering service:')
            if len(parts) > 1:
                remaining = parts[1]
                if 'Train already in service:' in remaining:
                    enter_parts = remaining.split('Train already in service:')
                    train_entering = enter_parts[0].strip()
                    if len(enter_parts) > 1:
                        if 'Note:' in enter_parts[1]:
                            service_parts = enter_parts[1].split('Note:')
                            train_in_service = service_parts[0].strip()
                            if len(service_parts) > 1:
                                note = service_parts[1].strip()
                        else:
                            train_in_service = enter_parts[1].strip()
        else:
            train_entering = guidelines.strip()
    
    # Guidelines table
    guidelines_table = f'''
    <table class="guidelines-table">
        <thead>
            <tr>
                <th>Failure Scenario</th>
                <th>Chief Controller</th>
                <th>Local Response</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="row-header">1)</td>
                <td>{train_entering if train_entering else guidelines}</td>
                <td rowspan="3">{local_response}</td>
            </tr>
            <tr>
                <td class="row-header">2)</td>
                <td>{train_in_service}</td>
            </tr>
            <tr>
                <td class="row-header">3)</td>
                <td style="background: #fff8f0;">{note if note else "N/A"}</td>
            </tr>
        </tbody>
    </table>
    '''
    
    st.markdown(guidelines_table, unsafe_allow_html=True)
    
    # Timer Control
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Back to Scenarios", key="back_to_scenario"):
            st.session_state.current_page = 'scenario'
            st.session_state.timer_running = False
            st.session_state.timer_start = None
            st.rerun()
    
    with col2:
        if st.session_state.timer_running:
            if st.button("⏹️ Stop Timer", key="stop_timer", type="primary"):
                st.session_state.timer_running = False
                save_resolution_data()
                st.success("✅ Timer stopped and data saved!")
                st.balloons()
    
    with col3:
        if st.button("🔄 New Scenario", key="new_scenario"):
            st.session_state.active_scenarios = []
            st.session_state.selected_scenarios = []
            st.session_state.timer_running = False
            st.session_state.timer_start = None
            st.session_state.current_page = 'scenario'
            st.rerun()

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

# Run the application
if __name__ == "__main__":
    main()