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
        'resolution_data': []
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
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        color: white;
    }
    
    .header-date {
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
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
    
    /* Timer display */
    .timer-display {
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #003b70, #0056a3);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: 0 4px 15px rgba(0,59,112,0.3);
        z-index: 1000;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #003b70, #0056a3);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 2px 8px rgba(0,59,112,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,59,112,0.3);
    }
    
    /* Stop timer button */
    .stop-timer-btn {
        background: linear-gradient(135deg, #dc3545, #c82333);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 1rem auto;
        display: block;
    }
    
    .stop-timer-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(220,53,69,0.3);
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
    
    /* Content boxes */
    .content-box {
        background: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        min-height: 120px;
        color: #000000;
    }
    
    /* Equipment selection input */
    .equipment-input-container {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .equipment-input {
        flex: 1;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        padding: 0.5rem;
        font-size: 1rem;
        background: #ffffff;
        color: #000000;
    }
    
    .equipment-input:focus {
        border-color: #003b70;
        outline: none;
    }
    
    .increment-btn {
        background: #003b70;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem;
        font-size: 1.2rem;
        cursor: pointer;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Responsive adjustments */
    @media (max-width: 1200px) {
        .equipment-container {
            grid-template-columns: repeat(3, 1fr);
        }
        
        .scenario-container {
            grid-template-columns: 1fr;
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
    
    /* File uploader styling */
    .uploadedFile {
        border: 2px solid #003b70;
        border-radius: 8px;
        background: #ffffff;
        color: #000000;
    }
    
    /* Hide scrollbars */
    .main .block-container {
        max-height: 100vh;
    }
    
    /* Ensure everything fits */
    .element-container {
        margin: 0.25rem 0;
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
    
    /* Streamlit checkbox styling */
    .stCheckbox > label {
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# Timer update function
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

# Main application logic
def main():
    update_timer()
    
    # Timer display (only show when running)
    if st.session_state.timer_running:
        st.markdown(f"""
        <div class="timer-display">
            ⏱️ {st.session_state.timer_display}
        </div>
        """, unsafe_allow_html=True)
    
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

def show_main_interface():
    # Sidebar - based on wireframe
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-welcome">
            👤 Welcome<br>
            <strong>{st.session_state.username}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Logout", key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.active_scenarios = []
            st.session_state.timer_running = False
            st.rerun()
        
        if st.button("Download History", key="download_btn"):
            show_download_history()
    
    # Main content area - based on wireframe layout
    # Header with title and digital timer
    current_time = datetime.datetime.now()
    st.markdown(f"""
    <div class="header-container">
        <h1 class="header-title">Troubleshooting Guide System</h1>
        <div class="header-date">{current_time.strftime('%d %B %Y')}<br>{current_time.strftime('%H:%M')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Equipment failure selection - based on wireframe
    st.markdown('<div class="section-header">Select how many equipment fail</div>', unsafe_allow_html=True)
    
    # Equipment input with increment button - based on wireframe
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        num_equipment = st.number_input(
            "",
            min_value=1,
            max_value=5,
            value=st.session_state.num_equipment_fail,
            key="num_equipment_input"
        )
        st.session_state.num_equipment_fail = num_equipment
    
    # Data upload
    uploaded_file = st.file_uploader("Upload MOR Data", type=['csv', 'xlsx'], key="file_upload")
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            else:
                df = pd.read_excel(uploaded_file)
            
            st.session_state.mor_data = df
            st.success("✅ Data uploaded successfully!")
            
            # Equipment selection - based on wireframe grid layout
            st.markdown('<div class="section-header">Equipment:</div>', unsafe_allow_html=True)
            
            equipment_list = df['Equipment'].unique().tolist()
            equipment_list = [eq for eq in equipment_list if pd.notna(eq)]
            
            # Equipment grid layout - based on wireframe (4 columns, 3 rows)
            st.markdown("**Select Equipment (Click to toggle, max 3):**")
            
            # Create grid layout similar to wireframe
            cols = st.columns(4)
            for i, equipment in enumerate(equipment_list[:12]):  # Limit to 12 equipment (4x3 grid)
                with cols[i % 4]:
                    button_color = "primary" if equipment in st.session_state.selected_equipment else "secondary"
                    if st.button(
                        equipment,
                        key=f"equipment_{i}",
                        type=button_color,
                        help=f"Select {equipment} equipment"
                    ):
                        if equipment not in st.session_state.selected_equipment and len(st.session_state.selected_equipment) < st.session_state.num_equipment_fail:
                            st.session_state.selected_equipment.append(equipment)
                            st.success(f"✅ {equipment} selected!")
                        elif equipment in st.session_state.selected_equipment:
                            st.session_state.selected_equipment.remove(equipment)
                            st.info(f"❌ {equipment} deselected!")
                        else:
                            st.warning(f"⚠️ Maximum {st.session_state.num_equipment_fail} equipment allowed!")
                        st.rerun()
            
            # Show selected equipment
            if st.session_state.selected_equipment:
                st.markdown("**Selected Equipment:**")
                selected_cols = st.columns(3)
                for i, equipment in enumerate(st.session_state.selected_equipment):
                    with selected_cols[i % 3]:
                        st.markdown(f"🔧 **{equipment}**")
            
            # Show failure scenarios if equipment selected - based on wireframe
            if st.session_state.selected_equipment:
                st.markdown('<div class="section-header">Failure Scenario:</div>', unsafe_allow_html=True)
                
                # Get scenarios for selected equipment
                scenarios = []
                for equipment in st.session_state.selected_equipment:
                    equipment_scenarios = df[df['Equipment'] == equipment]
                    scenarios.extend(equipment_scenarios.to_dict('records'))
                
                # Scenario selection with classification - based on wireframe
                if scenarios:
                    # Create two columns for scenarios like in wireframe
                    col1, col2 = st.columns(2)
                    
                    for i, scenario in enumerate(scenarios):
                        classification = scenario.get('Failure Classification', '').lower()
                        scenario_class = 'major' if 'major' in classification else 'minor'
                        
                        # Alternate between columns
                        with col1 if i % 2 == 0 else col2:
                            scenario_text = f"{scenario.get('Equipment', 'Unknown')}\n{scenario.get('Failure Scenario', 'Unknown')}"
                            
                            if st.button(
                                scenario_text,
                                key=f"scenario_{i}",
                                help=f"Classification: {scenario_class.upper()}"
                            ):
                                st.session_state.active_scenarios = [scenario]
                                st.session_state.timer_start = time.time()
                                st.session_state.timer_running = True
                                st.session_state.scenario_start_time = datetime.datetime.now()
                                
                                # Set alarm status based on scenario data
                                st.session_state.alarm_status = {
                                    'ats': scenario.get('ATS Alarm Description', '') not in ['N/A', '', 'No alarm triggered'],
                                    'fscada': scenario.get('FSCADA Alarm Description', '') not in ['N/A', '', 'No alarm triggered'],
                                    'hmi': scenario.get('HMI Alarm', '') not in ['N/A', '', 'No alarm triggered']
                                }
                                st.rerun()
                
                # Show active scenario details - based on wireframe layout
                if st.session_state.active_scenarios:
                    scenario = st.session_state.active_scenarios[0]
                    
                    # Equipment and Failure Scenario display - right side like wireframe
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        # Alarm Status Section - based on wireframe
                        st.markdown('<div class="section-header">Alarm Status</div>', unsafe_allow_html=True)
                        
                        # Alarm indicators
                        alarm_col1, alarm_col2, alarm_col3 = st.columns(3)
                        
                        alarms = [
                            ('ATS', scenario.get('ATS Alarm Description', 'N/A'), st.session_state.alarm_status['ats']),
                            ('FSCADA', scenario.get('FSCADA Alarm Description', 'N/A'), st.session_state.alarm_status['fscada']),
                            ('HMI', scenario.get('HMI Alarm', 'N/A'), st.session_state.alarm_status['hmi'])
                        ]
                        
                        for i, (system, description, is_active) in enumerate(alarms):
                            with [alarm_col1, alarm_col2, alarm_col3][i]:
                                if is_active and description not in ['N/A', '', 'No alarm triggered']:
                                    st.markdown(f'''
                                    <div class="alarm-indicator alarm-active">
                                        {system}
                                    </div>
                                    <div style="font-size: 0.8rem; margin-top: 0.5rem; text-align: center;">
                                        {description}
                                    </div>
                                    ''', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'''
                                    <div class="alarm-indicator alarm-inactive">
                                        {system}
                                    </div>
                                    <div style="font-size: 0.8rem; margin-top: 0.5rem; text-align: center;">
                                        No alarm triggered
                                    </div>
                                    ''', unsafe_allow_html=True)
                    
                    with col2:
                        # Equipment and Failure Scenario display - right side
                        st.markdown('<div class="section-header">Equipment:</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="content-box">{scenario.get("Equipment", "N/A")}</div>', unsafe_allow_html=True)
                        
                        st.markdown('<div class="section-header">Failure Scenario:</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="content-box">{scenario.get("Failure Scenario", "N/A")}</div>', unsafe_allow_html=True)
                    
                    # Guidelines Section - based on wireframe table structure
                    st.markdown('<div class="section-header">Guideline:</div>', unsafe_allow_html=True)
                    
                    # Parse guidelines
                    guidelines = scenario.get('Guidelines for the Chief Controller', 'N/A')
                    local_response = scenario.get('Local Response', 'N/A')
                    
                    # Parse guidelines for table structure
                    train_entering = ""
                    train_in_service = ""
                    note = ""
                    
                    if guidelines != 'N/A' and guidelines.strip():
                        # Simple parsing based on common patterns
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
                            # If no structured format, show as general guideline
                            train_entering = guidelines.strip()
                    
                    # Create guidelines table - based on wireframe structure
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
                    
                    # Stop Timer Button - based on wireframe
                    if st.session_state.timer_running:
                        if st.button("Stop Timer", key="stop_timer", type="primary"):
                            st.session_state.timer_running = False
                            save_resolution_data()
                            st.success("✅ Timer stopped and data saved!")
                            st.balloons()
                            
        except Exception as e:
            st.error(f"Error reading uploaded file: {str(e)}")

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

# Auto-refresh for timer updates
if st.session_state.timer_running:
    time.sleep(1)
    st.rerun()