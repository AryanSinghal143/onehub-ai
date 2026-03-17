from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
import sqlite3
from datetime import datetime
import os

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "templates"))

conn = sqlite3.connect("tickets.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    email TEXT,
    response TEXT,
    status TEXT,
    created_at TEXT
)
""")

class Ticket(BaseModel):
    title: str
    description: str
    email: str

def detect_priority(text):
    text = text.lower()
    if any(word in text for word in ["urgent", "down", "critical", "failure"]):
        return "High"
    elif any(word in text for word in ["error", "issue", "fail"]):
        return "Medium"
    return "Low"

def detect_category(text):
    text = text.lower()
    if "api" in text:
        return "API Issue"
    elif "network" in text:
        return "Network Issue"
    elif "login" in text:
        return "Authentication Issue"
    elif "payment" in text:
        return "Billing Issue"
    return "General Query"

def generate_response(ticket):
    priority = detect_priority(ticket.description)
    category = detect_category(ticket.description)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""
Hi,

✅ Your ticket has been received.

📌 Title: {ticket.title}
📂 Category: {category}
⚡ Priority: {priority}
🕒 Time: {time}

Our team is actively working on this issue and will update you shortly.

Thanks,
AI Support System
"""

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ticket")
def create_ticket(ticket: Ticket):
    response = generate_response(ticket)
    status = "Open"

    cursor.execute(
        "INSERT INTO tickets (title, description, email, response, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (ticket.title, ticket.description, ticket.email, response, status, str(datetime.now()))
    )
    conn.commit()

    return {"response": response}

@app.get("/tickets")
def get_tickets():
    cursor.execute("SELECT * FROM tickets ORDER BY id DESC")
    return {"tickets": cursor.fetchall()}

@app.put("/ticket/{ticket_id}")
def update_status(ticket_id: int):
    cursor.execute("UPDATE tickets SET status='Resolved' WHERE id=?", (ticket_id,))
    conn.commit()
    return {"message": "Ticket resolved"}
