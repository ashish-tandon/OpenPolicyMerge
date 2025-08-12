from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Notification Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Notification(BaseModel):
    user_id: str
    message: str
    type: str = "info"

@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

@app.get("/readyz")
async def readiness_check():
    return {"status": "ready"}

@app.get("/")
async def root():
    return {"message": "Notification Service is running"}

@app.post("/notifications/send")
async def send_notification(notification: Notification):
    # TODO: Implement notification sending
    return {"message": "Notification sent", "notification": notification}
