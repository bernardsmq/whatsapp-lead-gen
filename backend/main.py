from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Import routes
from routes import auth, leads, sheets, dashboard, workflows

load_dotenv()

app = FastAPI(
    title="WhatsApp Lead Gen API",
    description="API for WhatsApp lead generation system",
    version="1.0.0"
)

# CORS middleware
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    os.getenv("FRONTEND_URL", "https://your-frontend.railway.app"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(sheets.router)
app.include_router(dashboard.router)
app.include_router(workflows.router)

@app.get("/")
async def root():
    return {"message": "WhatsApp Lead Gen API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
