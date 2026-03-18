from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

tickets_db = []

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

class Ticket(BaseModel):
    title: str
    description: str
    email: str

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ticket")
async def create_ticket(ticket: Ticket):
    try:
        for t in tickets_db:
            if t["description"] == ticket.description:
                return {"message": "Duplicate ticket detected ⚠️"}

        ticket_id = f"JIRA-{int(datetime.now().timestamp())}"

        data = {
            "title": ticket.title,
            "description": ticket.description,
            "email": ticket.email,
            "ticket_id": ticket_id
        }

        tickets_db.append(data)

        return {
            "message": "✅ Ticket created",
            "ticket_id": ticket_id
        }

    except Exception as e:
        return {"message": "Internal error"}

@app.get("/dashboard")
def dashboard():
    return {"total_tickets": len(tickets_db)}
