from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
import sqlite3
from datetime import datetime
import os

app = FastAPI()

templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "templates"))

# DATABASE
conn = sqlite3.connect("tickets.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    email TEXT,
    response TEXT,
    created_at TEXT
)
""")

# MODEL
class Ticket(BaseModel):
    title: str
    description: str
    email: str

# LOGIC
def detect_priority(text):
    text = text.lower()
    if "urgent" in text or "down" in text:
        return "High"
    elif "error" in text:
        return "Medium"
    return "Low"

def generate_response(ticket):
    priority = detect_priority(ticket.description)
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""
Hi,

Your ticket has been received successfully.

Title: {ticket.title}
Priority: {priority}
Time: {time}

Our team is working on it and will update you soon.

Thanks,
AI Support System
"""

# ROUTES
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ticket")
def create_ticket(ticket: Ticket):
    response = generate_response(ticket)

    cursor.execute(
        "INSERT INTO tickets (title, description, email, response, created_at) VALUES (?, ?, ?, ?, ?)",
        (ticket.title, ticket.description, ticket.email, response, str(datetime.now()))
    )
    conn.commit()

    return {"response": response}