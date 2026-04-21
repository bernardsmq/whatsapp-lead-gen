from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Import routes
from routes import auth, leads, sheets, dashboard, workflows, whatsapp, manual_leads, analytics

load_dotenv()

app = FastAPI(
    title="WhatsApp Lead Gen API",
    description="API for WhatsApp lead generation system",
    version="1.0.0"
)

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

@app.get("/")
async def root():
    return {"message": "WhatsApp Lead Gen API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

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
            "users_count": len(users_response.data) if users_response.data else 0,
            "users": [{"email": u["email"]} for u in (users_response.data or [])],
            "leads_count": len(leads_response.data) if leads_response.data else 0,
            "leads": [{"id": l["id"], "name": l["first_name"], "phone": l["phone"]} for l in (leads_response.data or [])],
            "conversations_count": len(convs_response.data) if convs_response.data else 0,
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
