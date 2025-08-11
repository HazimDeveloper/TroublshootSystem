import streamlit as st
import datetime
import time

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