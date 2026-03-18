# OneHub AI Ticket System

## Setup

1. Install dependencies:
pip install -r requirements.txt

2. Run locally:
uvicorn main:app --reload

3. Create .env file with:
OPENAI_API_KEY=your_key
EMAIL=your_email
PASSWORD=your_password

## Deploy on Render
Build: pip install -r requirements.txt
Start: uvicorn main:app --host 0.0.0.0 --port 10000
