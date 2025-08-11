import streamlit as st
import pandas as pd

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