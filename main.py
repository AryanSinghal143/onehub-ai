from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ---------------- AI LOGIC ---------------- #

def detect_category(text):
    text = text.lower()
    if "network" in text:
        return "Network"
    elif "ui" in text or "screen" in text:
        return "UI"
    elif "api" in text or "backend" in text:
        return "Service"
    return "FE"

def detect_priority(text):
    text = text.lower()
    if "urgent" in text or "down" in text:
        return "High"
    elif "error" in text:
        return "Medium"
    return "Low"

# ---------------- MODELS ---------------- #

class Ticket(BaseModel):
    title: str
    description: str
    email: str

# ---------------- ROUTES ---------------- #

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ✅ Manual ticket (your form)
@app.post("/ticket")
async def create_ticket(ticket: Ticket):
    try:
        category = detect_category(ticket.description)
        priority = detect_priority(ticket.description)
        jira_id = f"JIRA-{int(datetime.now().timestamp())}"

        response = {
            "message": "Ticket created successfully",
            "title": ticket.title,
            "category": category,
            "priority": priority,
            "ticket_id": jira_id
        }

        return response

    except Exception as e:
        print("ERROR:", e)
        return {"message": "Something went wrong"}

# ✅ Multi-source tickets (OneHub + Jira + Zendesk)
@app.get("/process-tickets")
def process_tickets():
    try:
        # Simulated data
        tickets = [
            {"source": "OneHub", "title": "App not loading", "description": "App down urgent"},
            {"source": "Jira", "title": "API error", "description": "500 error in backend"},
            {"source": "Zendesk", "title": "Login issue", "description": "User cannot login"}
        ]

        processed = []

        for t in tickets:
            processed.append({
                "source": t["source"],
                "title": t["title"],
                "category": detect_category(t["description"]),
                "priority": detect_priority(t["description"])
            })

        return {"data": processed}

    except Exception as e:
        print("ERROR:", e)
        return {"data": []}
