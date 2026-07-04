import streamlit as st
import requests
import pandas as pd
import os

# Updated base url with your working ngrok tunnel
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

# Ensure session state variables exist
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- AUTHENTICATION INTERFACE (BYPASSED FOR TESTING) ---
if not st.session_state["logged_in"]:
    st.title("🎬 CineBook")
    
    choice = st.radio("Choose Option:", ["Login", "Signup"])
    email_in = st.text_input("Email ID:")
    password_in = st.text_input("Password:", type="password")
    
    if choice == "Login":
        if st.button("Login"):
            # Bypassing backend database lock, forcing successful login entry
            st.session_state["logged_in"] = True
            st.success("Login Successful! (Bypassed)")
            st.rerun()
            
    elif choice == "Signup":
        if st.button("Create Account"):
            # Bypassing backend validation to let you access movie selection directly
            st.session_state["logged_in"] = True
            st.success("Account Created Successfully! (Bypassed)")
            st.rerun()

# --- MAIN APP INTERFACE (SHOWS AFTER LOGIN) ---
else:
    st.title("🎟️ Welcome to CineBook Movie Booking")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"logged_in": False}))
    
    # Movie Selection Dashboard
    selected_movie = st.selectbox("Select a Movie to Book:", list(MOVIE_META.keys()))
    
    if selected_movie:
        st.subheader(selected_movie)
        meta = MOVIE_META[selected_movie]
        
        # Display Image and Cast Details cleanly
        if os.path.exists(meta["img"]):
            st.image(meta["img"], width=300)
        st.write(meta["desc"])
        
        # Booking Workflow Triggers
        st.info(f"Proceeding to fetch seats for {selected_movie} from local backend via Ngrok...")
        
        # Sample payload connection test back to your machine
        city = "Hyderabad"
        theatre = "PVR Cinemas"
        screen = "Screen 3"
        
        if st.button("Fetch Real-time Available Seats"):
            try:
                # Testing connection route through tunnel directly to your terminal endpoints
                fetch_url = f"{BASE_URL}/seats/fetch?city={city}&movie={selected_movie}&theatre={theatre}&screen={screen}"
                res = requests.get(fetch_url)
                if res.status_code == 200:
                    st.success("Connected to local backend successfully! Seats fetched.")
                    st.json(res.json())
                else:
                    st.error(f"Backend returned status code: {res.status_code}")
            except Exception as e:
                st.error(f"Failed to fetch from backend link: {str(e)}")
