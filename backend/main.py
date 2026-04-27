from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import atexit

# Import routes
from routes import auth, leads, sheets, dashboard, workflows, whatsapp, manual_leads, analytics, auto_send

load_dotenv()

app = FastAPI(
    title="WhatsApp Lead Gen API",
    description="API for WhatsApp lead generation system",
    version="2.0.0",
    redirect_slashes=False  # Disable automatic trailing slash redirects - using Meta Cloud API
)

# Middleware to handle X-Forwarded-Proto for HTTPS
@app.middleware("http")
async def https_redirect_middleware(request, call_next):
    """Ensure HTTPS protocol is properly recognized behind proxy"""
    # Detect HTTPS from proxy headers (Railway sends x-forwarded-proto)
    x_forwarded_proto = request.headers.get("x-forwarded-proto")
    if x_forwarded_proto:
        request.scope["scheme"] = x_forwarded_proto

    response = await call_next(request)
    return response

# CORS middleware
frontend_url = os.getenv("FRONTEND_URL", "https://whatsapp-lead-gen-production.up.railway.app")
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    frontend_url,
    # Add both versions (with and without www, http and https)
    frontend_url.replace("https://", "http://") if frontend_url.startswith("https://") else frontend_url,
]

# Remove duplicates
origins = list(set(origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(sheets.router)
app.include_router(dashboard.router)
app.include_router(workflows.router)
app.include_router(whatsapp.router)
app.include_router(manual_leads.router)
app.include_router(analytics.router)
app.include_router(auto_send.router)

@app.get("/")
async def root():
    return {"message": "WhatsApp Lead Gen API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Background scheduler for auto-sending leads after timeout
scheduler = BackgroundScheduler()

def check_lead_timeouts():
    """Periodically check for leads that need auto-send"""
    try:
        requests.post("http://localhost:8000/auto-send/check-timeout")
    except Exception as e:
        print(f"Auto-send check error: {e}")

# Schedule the check every 30 seconds
scheduler.add_job(check_lead_timeouts, "interval", seconds=30, id="lead_timeout_check")

@app.on_event("startup")
def start_scheduler():
    scheduler.start()
    print("✓ Auto-send scheduler started")

@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()
    print("✓ Auto-send scheduler stopped")

# Ensure scheduler stops on exit
atexit.register(lambda: scheduler.shutdown())

@app.get("/debug/status")
async def debug_status():
    """Debug endpoint to check database and system status"""
    try:
        from database import supabase

        # Check users
        users_response = supabase.table("users").select("id, email").execute()

        # Check leads
        leads_response = supabase.table("leads").select("id, first_name, phone").execute()

        # Check conversations
        convs_response = supabase.table("conversations").select("id, lead_id").execute()

        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "cors_config": {
                "allowed_origins": list(set([
                    "http://localhost:3000",
                    "http://localhost:5173",
                    os.getenv("FRONTEND_URL", "https://whatsapp-lead-gen-production.up.railway.app"),
                ]))
            },
            "database": {
                "users_count": len(users_response.data) if users_response.data else 0,
                "leads_count": len(leads_response.data) if leads_response.data else 0,
                "conversations_count": len(convs_response.data) if convs_response.data else 0,
            },
            "users": [{"email": u["email"]} for u in (users_response.data or [])],
            "leads": [{"id": l["id"], "name": l["first_name"], "phone": l["phone"]} for l in (leads_response.data or [])],
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
