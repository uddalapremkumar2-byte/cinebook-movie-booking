import streamlit as st
import requests
import pandas as pd
import os

# Your working ngrok tunnel URL connected to local backend
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

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

def main():
    if not st.session_state["logged_in"]:
        st.title("🎬 CineBook")
        auth_option = st.radio("Choose Option:", ["Login", "Signup"])
        
        email = st.text_input("Email ID:")
        password = st.text_input("Password:", type="password")
        
        if auth_option == "Login":
            if st.button("Login"):
                if email and password:
                    try:
                        res = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
                        if res.status_code == 200:
                            st.session_state["logged_in"] = True
                            st.session_state["username"] = email
                            st.success("Login Successful!")
                            st.rerun()
                        else:
                            st.error("Invalid Email or Password.")
                    except Exception as e:
                        st.error(f"Connection Error: {str(e)}")
                else:
                    st.warning("Please enter both email and password.")
                    
        else:
            if st.button("Create Account"):
                if email and password:
                    try:
                        res = requests.post(f"{BASE_URL}/auth/signup", json={"email": email, "password": password})
                        if res.status_code == 200:
                            st.success("Account Created Successfully! Please Login.")
                        else:
                            st.error("Signup failed. Account might already exist.")
                    except Exception as e:
                        st.error(f"Connection Error: {str(e)}")
                else:
                    st.warning("Please enter both email and password.")
                    
    else:
        st.title("🎟️ Welcome to CineBook Movie Booking")
        st.sidebar.write(f"Logged in as: {st.session_state['username']}")
        if st.sidebar.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.rerun()
            
        # Movie Selection Dashboard
        selected_movie = st.selectbox("Select a Movie to Book:", list(MOVIE_META.keys()))
        
        if selected_movie:
            st.subheader(selected_movie)
            meta = MOVIE_META[selected_movie]
            
            if os.path.exists(meta["img"]):
                st.image(meta["img"], width=300)
            st.write(meta["desc"])
            
            city = st.text_input("Enter City:", "Hyderabad")
            theatre = st.text_input("Enter Theatre:", "PVR Cinemas")
            screen = st.text_input("Enter Screen:", "Screen 3")
            
            if st.button("Fetch Available Seats"):
                try:
                    fetch_url = f"{BASE_URL}/seats/fetch?city={city}&movie={selected_movie}&theatre={theatre}&screen={screen}"
                    res = requests.get(fetch_url)
                    if res.status_code == 200:
                        seats_data = res.json()
                        st.success("Seats fetched successfully!")
                        
                        # Render Seat Matrix Layout
                        st.write("### Select Your Seats:")
                        rows = sorted(list(set(s['row_name'] for s in seats_data)))
                        cols = sorted(list(set(s['col_number'] for s in seats_data)))
                        
                        selected_seats = []
                        for r in rows:
                            cols_list = st.columns(len(cols))
                            for idx, c in enumerate(cols):
                                seat = next((s for s in seats_data if s['row_name'] == r and s['col_number'] == c), None)
                                if seat:
                                    seat_label = f"{r}{c}"
                                    if seat['is_booked']:
                                        cols_list[idx].button(seat_label, key=f"btn_{seat_label}", disabled=True)
                                    else:
                                        if cols_list[idx].checkbox(seat_label, key=f"chk_{seat_label}"):
                                            selected_seats.append(seat['id'])
                        
                        if selected_seats:
                            st.write(f"Selected Seat IDs: {selected_seats}")
                            if st.button("Confirm & Book Tickets"):
                                checkout_payload = {
                                    "email": st.session_state["username"],
                                    "city": city,
                                    "movie": selected_movie,
                                    "theatre": theatre,
                                    "screen": screen,
                                    "seat_ids": selected_seats
                                }
                                commit_res = requests.post(f"{BASE_URL}/tickets/commit", json=checkout_payload)
                                if commit_res.status_code == 200:
                                    st.success("🎉 Tickets Booked Successfully!")
                                else:
                                    st.error("Booking failed. Please try again.")
                    else:
                        st.error(f"Backend error: {res.status_code}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {str(e)}")

if __name__ == "__main__":
    main()
