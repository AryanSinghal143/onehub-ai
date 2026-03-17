from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
import sqlite3
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ✅ DATABASE
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

# ✅ MODEL
class Ticket(BaseModel):
    title: str
    description: str
    email: str

# ✅ AI LOGIC
def detect_priority(text):
    text = text.lower()
    if "urgent" in text or "down" in text:
        return "High"
    elif "error" in text:
        return "Medium"
    return "Low"

def generate_response(ticket):
    return f"""
Ticket Received ✅

Title: {ticket.title}
Priority: {detect_priority(ticket.description)}
Time: {datetime.now()}

We are working on it.
"""

# ✅ ROUTES
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ticket")
async def create_ticket(ticket: Ticket):
    try:
        response = generate_response(ticket)

        cursor.execute(
            "INSERT INTO tickets (title, description, email, response, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (ticket.title, ticket.description, ticket.email, response, "Open", str(datetime.now()))
        )
        conn.commit()

        return {"response": response}

    except Exception as e:
        print("ERROR:", e)
        return {"response": "Something went wrong. Check logs."}
