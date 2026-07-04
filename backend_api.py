from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="CineBook Core Engine API Service Panel", version="5.0.0")

class AuthSchema(BaseModel):
    email: str
    password: str

class CheckoutSchema(BaseModel):
    email: str
    city: str
    movie: str
    theatre: str
    screen: str
    seats: list
    cost: float

@app.post("/auth/signup")
def user_signup(data: AuthSchema):
    conn = sqlite3.connect("cinema.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO user_registry (email, password) VALUES (?, ?)", (data.email, data.password))
        conn.commit()
        return {"status": "SUCCESS"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Account validation signature trace duplicate.")
    finally:
        conn.close()

@app.post("/auth/login")
def user_login(data: AuthSchema):
    conn = sqlite3.connect("cinema.db")
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM user_registry WHERE email = ?", (data.email,))
    res = cursor.fetchone()
    conn.close()
    if res and res[0] == data.password:
        return {"status": "SUCCESS"}
    raise HTTPException(status_code=401, detail="Authentication failed.")

@app.get("/seats/fetch")
def fetch_targeted_seats(city: str, movie: str, theatre: str, screen: str):
    conn = sqlite3.connect("cinema.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Seat_ID, Status FROM seat_inventory 
        WHERE City=? AND Movie=? AND Theatre=? AND Screen=?
    """, (city, movie, theatre, screen))
    rows = cursor.fetchall()
    conn.close()
    return [{"Seat_ID": r[0], "Status": r[1]} for r in rows]

@app.post("/tickets/commit")
def process_atomic_checkout(payload: CheckoutSchema):
    conn = sqlite3.connect("cinema.db")
    cursor = conn.cursor()
    
    # Validation constraint checks parameters pipelines map verification alignment
    for seat in payload.seats:
        s_key = f"{payload.city}_{payload.movie}_{payload.theatre}_{payload.screen}_{seat}"
        cursor.execute("SELECT Status FROM seat_inventory WHERE Seat_Key=?", (s_key,))
        curr = cursor.fetchone()
        
        if not curr:
            cursor.execute("""
                INSERT OR IGNORE INTO seat_inventory (Seat_Key, City, Movie, Theatre, Screen, Seat_ID, Status)
                VALUES (?, ?, ?, ?, ?, ?, 'Available')
            """, (s_key, payload.city, payload.movie, payload.theatre, payload.screen, seat, "Available"))
        elif curr[0] == "Booked":
            conn.close()
            raise HTTPException(status_code=400, detail=f"Concurrency Block: Seat {seat} matches locked state.")
            
    # Process batch transactions updates maps properties strings commands
    for seat in payload.seats:
        s_key = f"{payload.city}_{payload.movie}_{payload.theatre}_{payload.screen}_{seat}"
        cursor.execute("UPDATE seat_inventory SET Status='Booked' WHERE Seat_Key=?", (s_key,))
        
    seats_str = ", ".join(payload.seats)
    cursor.execute("""
        INSERT INTO booking_ledger (Customer_Email, City, Movie, Theatre, Screen, Seats_Booked, Total_Paid)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (payload.email, payload.city, payload.movie, payload.theatre, payload.screen, seats_str, payload.cost))
    
    conn.commit()
    conn.close()
    return {"status": "SUCCESS"}

@app.get("/bookings/history")
def fetch_history(email: str):
    conn = sqlite3.connect("cinema.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, City, Movie, Theatre, Screen, Seats_Booked, Total_Paid FROM booking_ledger WHERE Customer_Email=? ORDER BY id DESC", (email,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "City": r[1], "Movie": r[2], "Theatre": r[3], "Screen": r[4], "Seats_Booked": r[5], "Total_Paid": r[6]} for r in rows]