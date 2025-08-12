from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Authentication Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

class User(BaseModel):
    username: str
    email: str

@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

@app.get("/readyz")
async def readiness_check():
    return {"status": "ready"}

@app.get("/")
async def root():
    return {"message": "Authentication Service is running"}

@app.post("/auth/login")
async def login(username: str, password: str):
    # TODO: Implement actual authentication
    return {"message": "Login endpoint", "username": username}

@app.get("/auth/me", response_model=User)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # TODO: Implement token validation
    return {"username": "test_user", "email": "test@example.com"}
