from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
import sqlite3
from datetime import datetime
import os
import aiosmtplib
from email.message import EmailMessage

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ✅ ENV VARIABLES
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

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
    if any(x in text for x in ["urgent", "down", "critical"]):
        return "High"
    elif any(x in text for x in ["error", "issue"]):
        return "Medium"
    return "Low"

def generate_response(ticket):
    return f"""
Hi,

✅ Your ticket has been received.

📌 Title: {ticket.title}
⚡ Priority: {detect_priority(ticket.description)}
🕒 Time: {datetime.now()}

Our team is working on it.

Thanks,
AI Support System
"""

# ✅ EMAIL FUNCTION (SAFE)
async def send_email(to_email, body):
    if not EMAIL or not PASSWORD:
        print("Email credentials not set")
        return

    try:
        message = EmailMessage()
        message["From"] = EMAIL
        message["To"] = to_email
        message["Subject"] = "Ticket Acknowledgement"
        message.set_content(body)

        await aiosmtplib.send(
            message,
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            username=EMAIL,
            password=PASSWORD
        )

    except Exception as e:
        print("EMAIL ERROR:", e)

# ✅ ROUTES
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ticket")
async def create_ticket(ticket: Ticket):
    response = generate_response(ticket)

    cursor.execute(
        "INSERT INTO tickets (title, description, email, response, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (ticket.title, ticket.description, ticket.email, response, "Open", str(datetime.now()))
    )
    conn.commit()

    # ✅ SAFE EMAIL (won’t crash)
    await send_email(ticket.email, response)

    return {"response": response}
