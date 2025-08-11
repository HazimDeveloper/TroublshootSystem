import streamlit as st

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