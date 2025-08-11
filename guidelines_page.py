import streamlit as st
import pandas as pd
import datetime
import time
import os

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

def show_guidelines_page():
    """Page 4: Guidelines and Clean Timer"""
    st.markdown('<div class="section-header">📖 Step 4: Follow Guidelines</div>', unsafe_allow_html=True)
    
    if len(st.session_state.active_scenarios) == 0:
        st.error("Please select a scenario first!")
        if st.button("⬅️ Back to Scenarios", key="back_to_scenario_error"):
            st.session_state.current_page = 'scenario'
            st.rerun()
        return
    
    # Initialize timer running state
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = True
    
    # SAFE TIMER INITIALIZATION - Always ensure timer_start exists
    current_time = time.time()
    
    # Initialize timer variables safely
    if 'timer_start' not in st.session_state or st.session_state.timer_start is None:
        st.session_state.timer_start = current_time
        st.session_state.scenario_start_time = datetime.datetime.now()
        st.session_state.elapsed_time = 0
        st.success("✅ Timer started automatically!")
    
    # SAFE CALCULATION - Always check for None
    try:
        if st.session_state.timer_start is not None:
            elapsed_seconds = current_time - st.session_state.timer_start
            st.session_state.elapsed_time = elapsed_seconds
        else:
            # Fallback: Reset timer if somehow None
            st.session_state.timer_start = current_time
            elapsed_seconds = 0
            st.warning("⚠️ Timer was reset due to initialization issue")
    except (TypeError, AttributeError) as e:
        # Error handling: Reset timer
        st.session_state.timer_start = current_time
        elapsed_seconds = 0
        st.error(f"🐛 Timer error fixed: {str(e)}")
    
    # Convert to minutes and seconds
    minutes = int(elapsed_seconds // 60)
    seconds = int(elapsed_seconds % 60)
    
    # Determine timer status and color
    if elapsed_seconds > 300:  # Over 5 minutes
        timer_color = "#dc3545"  # Red
        timer_icon = "🚨"
        status_text = "CRITICAL"
    elif elapsed_seconds > 180:  # Over 3 minutes
        timer_color = "#fd7e14"  # Orange
        timer_icon = "⚠️"
        status_text = "ALERT"
    else:
        timer_color = "#003b70"  # Blue
        timer_icon = "⏱️"
        status_text = "NORMAL"
    
    # Display timer
    st.markdown(f'''
     <div style="
         background: linear-gradient(135deg, {timer_color}, #0056a3);
         color: white;
         padding: 1rem;
         border-radius: 10px;
         text-align: center;
         margin-bottom: 1rem;
         font-size: 1.5rem;
         font-weight: bold;
         border: 2px solid #fff;
         box-shadow: 0 4px 8px rgba(0,0,0,0.2);
     ">
         {timer_icon} Timer: {minutes:02d}:{seconds:02d} ({status_text})
     </div>
     ''', unsafe_allow_html=True)
    
    # Timer control button
    col_timer1, col_timer2 = st.columns([1, 1])
    
    with col_timer1:
        if st.session_state.timer_running:
            if st.button("⏹️ Stop Timer", key="stop_timer", type="secondary"):
                st.session_state.timer_running = False
                st.success("✅ Timer stopped!")
                st.rerun()
        else:
            if st.button("▶️ Start Timer", key="start_timer", type="secondary"):
                st.session_state.timer_running = True
                st.success("✅ Timer resumed!")
                st.rerun()
    
    with col_timer2:
        if st.button("💾 Save & Complete", key="save_complete", type="primary"):
            st.session_state.timer_running = False
            save_resolution_data()
            
            # Reset all variables
            st.session_state.current_page = 'equipment'
            st.session_state.selected_equipment = []
            st.session_state.selected_scenarios = []
            st.session_state.active_scenarios = []
            if 'timer_start' in st.session_state:
                del st.session_state.timer_start
            st.session_state.elapsed_time = 0
            st.session_state.scenario_start_time = None
            st.session_state.timer_running = True
            
            if 'alarm_status' in st.session_state:
                del st.session_state.alarm_status
                
            st.success("✅ Data saved to history successfully!")
            st.balloons()
            time.sleep(1)
            st.rerun()
    
    # Show alerts based on time
    if 180 <= elapsed_seconds < 300:
        st.warning("⚠️ 3 minutes elapsed - Decision making time!")
    elif elapsed_seconds >= 300:
        st.error("🚨 5 minutes elapsed - Critical time reached!")
    
    # Equipment and Failure Scenario display
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
    
    # Collect alarm data
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
            if len(alarm_list) > 0:
                alarm_class = "alarm-active"
                alarm_text = "<br>".join(alarm_list)
            else:
                alarm_class = "alarm-inactive"
                alarm_text = "No alarm triggered"
            
            st.markdown(f'''
            <div class="alarm-indicator {alarm_class}">
                {system}
            </div>
            <div style="font-size: 0.8rem; margin-top: 0.5rem; text-align: center;">
                {alarm_text}
            </div>
            ''', unsafe_allow_html=True)
    
    # Guidelines Table - ONLY RENDER ONCE
    st.markdown('<div class="section-header">📋 Guidelines:</div>', unsafe_allow_html=True)
    
    scenario = st.session_state.active_scenarios[0]
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
    
    # Guidelines table - render only once
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
    
    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("⬅️ Back to Scenarios", key="back_to_scenario"):
            st.session_state.current_page = 'scenario'
            st.rerun()
    
    with col2:
        if st.button("🔄 New Scenario", key="new_scenario"):
            st.session_state.active_scenarios = []
            st.session_state.selected_scenarios = []
            if 'timer_start' in st.session_state:
                del st.session_state.timer_start
            st.session_state.timer_running = True
            st.session_state.current_page = 'scenario'
            st.rerun()
    
    # AUTO-UPDATE - Only if timer is running
    if st.session_state.timer_running:
        time.sleep(1)
        st.rerun()