from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

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

@app.get("/notifications/user/{user_id}")
async def get_user_notifications(user_id: str, limit: int = 10, offset: int = 0):
    """Get notifications for a specific user."""
    # Simulate user notifications
    notifications = [
        {
            "id": "notif-1",
            "user_id": user_id,
            "message": "Policy update available",
            "type": "info",
            "created_at": "2025-08-12T00:00:00Z",
            "read": False
        },
        {
            "id": "notif-2",
            "user_id": user_id,
            "message": "New data available for analysis",
            "type": "info",
            "created_at": "2025-08-11T00:00:00Z",
            "read": True
        }
    ]
    
    return {
        "user_id": user_id,
        "total_notifications": len(notifications),
        "unread_count": len([n for n in notifications if not n["read"]]),
        "notifications": notifications[offset:offset+limit]
    }

@app.post("/notifications/bulk")
async def send_bulk_notifications(notifications: List[Notification]):
    """Send multiple notifications at once."""
    results = []
    for notification in notifications:
        results.append({
            "user_id": notification.user_id,
            "status": "sent",
            "message_id": f"msg-{len(results)+1}"
        })
    
    return {
        "total_sent": len(results),
        "results": results
    }

@app.get("/notifications/stats")
async def get_notification_stats():
    """Get notification service statistics."""
    return {
        "total_notifications_sent": 1247,
        "notifications_today": 23,
        "active_users": 156,
        "delivery_success_rate": 0.98,
        "average_delivery_time": "2.3s",
        "last_updated": "2025-08-12T00:00:00Z"
    }
