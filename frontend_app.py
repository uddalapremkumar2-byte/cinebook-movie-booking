import streamlit as st
import requests
import pandas as pd
import os

BASE_URL = "https://dario-brusque-lilly.ngrok-free.dev"

# MATCHED TO YOUR EXACT DOUBLE EXTENSION FILENAMES IN VS CODE EXPLORER
MOVIE_META = {
    "Project K": {
        "img": "images/prabhas.jpeg.jpeg",
        "desc": "Cast: Prabhas, Amitabh Bachchan, Kamal Haasan"
    },
    "Pushpa 2": {
        "img": "images/pushpa.jpeg.jpeg",
        "desc": "Cast: Allu Arjun, Rashmika Mandanna, Fahadh Faasil"
    },
    "Devara": {
        "img": "images/devara.jpeg.jpeg",
        "desc": "Cast: NTR Jr, Saif Ali Khan, Janhvi Kapoor"
    }
}

# Reliable Byte Stream Loader to read raw image data without PIL crashes
def load_movie_poster(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "rb") as f:
                return f.read()
        except Exception:
            pass
    return None

if "stage" not in st.session_state:
    st.session_state.stage = "LOGIN"
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None
if "booking_data" not in st.session_state:
    st.session_state.booking_data = {}

def change_stage(target):
    st.session_state.stage = target
    st.rerun()

st.title("🎬 CineBook")
st.markdown("---")

# ==================== FORCED GLOBAL NAVIGATION ENGINE ====================
if st.session_state.stage != "LOGIN":
    nav_box = st.container()
    with nav_box:
        nav_col1, nav_col2, nav_col3 = st.columns([3, 3, 3])
        
        with nav_col1:
            if st.session_state.stage != "CITY_SELECT":
                if st.button("⬅️ Back", use_container_width=True, key="force_nav_back_action"):
                    back_routes = {
                        "MOVIE_SELECT": "CITY_SELECT",
                        "THEATRE_SELECT": "MOVIE_SELECT",
                        "SCREEN_SELECT": "THEATRE_SELECT",
                        "SEAT_GRID": "SCREEN_SELECT",
                        "REVIEW_TICKET": "SEAT_GRID",
                        "PAYMENT_GATEWAY": "REVIEW_TICKET",
                        "SUCCESS_RECEIPT": "CITY_SELECT",
                        "VIEW_BOOKINGS": "CITY_SELECT"
                    }
                    target_step = back_routes.get(st.session_state.stage, "CITY_SELECT")
                    if target_step == "CITY_SELECT":
                        st.session_state.booking_data = {}
                    change_stage(target_step)
            else:
                st.caption(f"👤 Account: **{st.session_state.auth_user if st.session_state.auth_user else 'Active'}**")

        with nav_col2:
            if st.button("📁 My Bookings", use_container_width=True, key="force_nav_bookings_action"):
                change_stage("VIEW_BOOKINGS")

        with nav_col3:
            if st.button("🔒 Logout", use_container_width=True, key="force_nav_logout_action", type="secondary"):
                st.session_state.auth_user = None
                st.session_state.booking_data = {}
                change_stage("LOGIN")
                
    st.markdown("---")

# ==================== LOGIN / SIGNUP ====================
if st.session_state.stage == "LOGIN":
    portal_mode = st.radio("Choose Option:", ["Login", "Signup"], horizontal=True)
    email_in = st.text_input("Email ID:")
    pass_in = st.text_input("Password:", type="password")
    
    if portal_mode == "Login":
        if st.button("Login", type="primary", use_container_width=True):
            res = requests.post(f"{BASE_URL}/auth/login", json={"email": email_in, "password": pass_in})
            if res.status_code == 200:
                st.session_state.auth_user = email_in
                change_stage("CITY_SELECT")
            else:
                st.error("Invalid Email or Password.")
    else:
        if st.button("Create Account", use_container_width=True):
            res = requests.post(f"{BASE_URL}/auth/signup", json={"email": email_in, "password": pass_in})
            if res.status_code == 200:
                st.success("Account created successfully! Please select Login mode to continue.")
            else:
                st.error("Signup failed. Account might already exist.")

# ==================== SELECT CITY ====================
elif st.session_state.stage == "CITY_SELECT":
    st.subheader("Select Your City")
    city_choice = st.selectbox("Choose City:", ["Hyderabad", "Vizag", "Vijayawada"])
    if st.button("Next", type="primary", use_container_width=True):
        st.session_state.booking_data["city"] = city_choice
        change_stage("MOVIE_SELECT")

# ==================== SELECT MOVIE ====================
elif st.session_state.stage == "MOVIE_SELECT":
    st.subheader("Select Movie")
    m_cols = st.columns(3)
    selected_movie = None
    for idx, (m_name, m_info) in enumerate(MOVIE_META.items()):
        with m_cols[idx]:
            poster_bytes = load_movie_poster(m_info["img"])
            if poster_bytes:
                st.image(poster_bytes, use_container_width=True)
            else:
                st.error(f"Missing Image: '{m_info['img']}'")
            st.markdown(f"**{m_name}**")
            st.caption(m_info["desc"])
            if st.button("Book Tickets", use_container_width=True, type="primary", key=f"bs_{m_name}"):
                selected_movie = m_name
    if selected_movie:
        st.session_state.booking_data["movie"] = selected_movie
        change_stage("THEATRE_SELECT")

# ==================== SELECT THEATRE ====================
elif st.session_state.stage == "THEATRE_SELECT":
    st.subheader("Select Your Theatre")
    th_choice = st.radio("Available Theatres:", ["Prasads IMAX", "PVR Cinemas", "AMB Cinemas"], horizontal=True)
    if st.button("Next", type="primary", use_container_width=True):
        st.session_state.booking_data["theatre"] = th_choice
        change_stage("SCREEN_SELECT")

# ==================== UPDATED: SELECT SCREEN & TIME ====================
elif st.session_state.stage == "SCREEN_SELECT":
    st.subheader("Select Screen & Show Time")
    
    # 1. Screen Option
    scr_choice = st.radio("Available Screens:", ["Screen 1", "Screen 2", "Screen 3", "Screen 4", "Screen 5"], horizontal=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Show Time Option (NEW ADDITION)
    time_choice = st.radio("Select Show Time:", ["11:00 AM (Morning)", "02:30 PM (Matinee)", "06:00 PM (First Show)", "09:30 PM (Second Show)"], horizontal=True)
    
    st.markdown("---")
    if st.button("Proceed to Seats", type="primary", use_container_width=True):
        st.session_state.booking_data["screen"] = scr_choice
        st.session_state.booking_data["show_time"] = time_choice
        change_stage("SEAT_GRID")

# ==================== SEAT GRID ====================
elif st.session_state.stage == "SEAT_GRID":
    bd = st.session_state.booking_data
    st.subheader(f"Select Your Seats ({bd['screen']} - {bd['show_time']})")
    
    s1, s2, s3, s4 = st.columns(4)
    s1.markdown("<div style='background-color:#2ecc71;padding:5px;text-align:center;color:white;font-weight:bold;border-radius:4px;'>Available</div>", unsafe_allow_html=True)
    s2.markdown("<div style='background-color:#3498db;padding:5px;text-align:center;color:white;font-weight:bold;border-radius:4px;'>Selected</div>", unsafe_allow_html=True)
    s3.markdown("<div style='background-color:#e74c3c;padding:5px;text-align:center;color:white;font-weight:bold;border-radius:4px;'>Booked</div>", unsafe_allow_html=True)
    s4.markdown("<div style='background-color:#f1c40f;padding:5px;text-align:center;color:black;font-weight:bold;border-radius:4px;'>Pending</div>", unsafe_allow_html=True)
    
    st.markdown("<br><center><div style='background-color:#333;color:#fff;padding:8px;font-weight:bold;border-radius:4px;'>📺 SCREEN THIS WAY</div></center><br>", unsafe_allow_html=True)
    
    rows_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    selected_seats = []
    
    res = requests.get(f"{BASE_URL}/seats/fetch", params={"city": bd['city'], "movie": bd['movie'], "theatre": bd['theatre'], "screen": bd['screen']})
    db_seats = {item['Seat_ID']: item['Status'] for item in res.json()} if res.status_code == 200 else {}
    
    for row in rows_labels:
        ui_cols = st.columns(10)
        for num in range(1, 11):
            seat_code = f"{row}{num}"
            current_status = db_seats.get(seat_code, "Available")
            
            with ui_cols[num-1]:
                if current_status == "Booked":
                    st.button(f"🔴\n{seat_code}", key=f"b_{seat_code}", disabled=True)
                elif current_status == "Pending":
                    st.button(f"🟡\n{seat_code}", key=f"b_{seat_code}", disabled=True)
                else:
                    is_sel = st.checkbox(f"{seat_code}", key=f"c_{seat_code}")
                    if is_sel:
                        selected_seats.append(seat_code)
                        
    st.markdown("---")
    if st.button("Proceed Booking", type="primary", use_container_width=True):
        if selected_seats:
            st.session_state.booking_data["chosen_codes"] = selected_seats
            st.session_state.booking_data["cost"] = len(selected_seats) * 250.0
            change_stage("REVIEW_TICKET")
        else:
            st.warning("Please select at least one seat.")

# ==================== REVIEW TICKET DETAILS ====================
elif st.session_state.stage == "REVIEW_TICKET":
    bd = st.session_state.booking_data
    st.subheader("Review Ticket Details")
    st.markdown("---")
    st.write(f"• Movie: **{bd['movie']}**")
    st.write(f"• Theatre & Screen: **{bd['theatre']} - {bd['screen']}**")
    st.write(f"• Show Time: **{bd['show_time']}**")
    st.write(f"• Seats: **{bd['chosen_codes']}**")
    st.write(f"• Total Amount: **₹ {bd['cost']}**")
    
    st.markdown("---")
    if st.button("Confirm Booking", type="primary", use_container_width=True):
        change_stage("PAYMENT_GATEWAY")

# ==================== PAYMENT GATEWAY ====================
elif st.session_state.stage == "PAYMENT_GATEWAY":
    bd = st.session_state.booking_data
    st.subheader("Payment Details")
    st.markdown("---")
    st.write(f"Total Amount to Pay: **₹ {bd['cost']}**")
    st.text_input("Enter UPI ID or Card Number:", value="user@upi")
    
    if st.button("Proceed Payment", type="primary", use_container_width=True):
        payload = {
            "email": str(st.session_state.auth_user),
            "city": str(bd['city']),
            "movie": str(bd['movie']),
            "theatre": str(bd['theatre']),
            "screen": str(bd['screen']),
            "seats": list(bd['chosen_codes']),
            "cost": float(bd['cost'])
        }
        res = requests.post(f"{BASE_URL}/tickets/commit", json=payload)
        if res.status_code == 200:
            change_stage("SUCCESS_RECEIPT")
        else:
            st.error("Transaction layer failed. Please verify server connectivity.")

# ==================== DIGITAL TICKET RECEIPT ====================
elif st.session_state.stage == "SUCCESS_RECEIPT":
    bd = st.session_state.booking_data
    st.balloons()
    st.success("Booking Confirmed!")
    
    c_img, c_txt = st.columns([1, 2])
    with c_img:
        final_bytes = load_movie_poster(MOVIE_META.get(bd['movie'], {}).get("img", ""))
        if final_bytes:
            st.image(final_bytes, use_container_width=True)
    with c_txt:
        st.markdown(f"""
        <div style='background-color:#2c3e50; color:#fff; padding:20px; border-radius:10px; border-left:8px solid #2ecc71;'>
            <h2 style='color:#2ecc71; margin-top:0;'>🎟️ CINEBOOK DIGITAL TICKET</h2>
            <p><b>User:</b> {st.session_state.auth_user}</p>
            <p><b>Movie:</b> {bd['movie']}</p>
            <p><b>Theatre & Screen:</b> {bd['theatre']} [ {bd['screen']} ]</p>
            <p><b>Show Time:</b> {bd['show_time']}</p>
            <p><b>Seats:</b> {", ".join(bd['chosen_codes'])}</p>
            <p><b>Amount Paid:</b> ₹ {bd['cost']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Book Another Ticket", use_container_width=True, type="primary"):
            st.session_state.booking_data = {}
            change_stage("CITY_SELECT")
    with c2:
        if st.button("View All Bookings", use_container_width=True):
            change_stage("VIEW_BOOKINGS")

# ==================== VIEW HISTORY ====================
elif st.session_state.stage == "VIEW_BOOKINGS":
    st.subheader("My Bookings")
    res = requests.get(f"{BASE_URL}/bookings/history", params={"email": st.session_state.auth_user})
    
    if res.status_code == 200 and res.json():
        for b in res.json():
            with st.container():
                st.markdown("---")
                col_poster, col_details = st.columns([1, 4])
                with col_poster:
                    history_bytes = load_movie_poster(MOVIE_META.get(b['Movie'], {}).get("img", ""))
                    if history_bytes:
                        st.image(history_bytes, use_container_width=True)
                with col_details:
                    st.markdown(f"### 🎟️ Booking ID: #{b['id']} - {b['Movie']}")
                    st.write(f"• **City:** {b['City']} | **Theatre:** {b['Theatre']} ({b['Screen']})")
                    st.write(f"• **Seats:** {b['Seats_Booked']} | **Paid:** ₹ {b['Total_Paid']}")
    else:
        st.caption("No booking logs found.")
        
    st.markdown("---")
    if st.button("Return to Main Dashboard", use_container_width=True, type="primary", key="history_dashboard_back"):
        change_stage("CITY_SELECT")
