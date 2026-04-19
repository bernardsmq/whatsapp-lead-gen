from fastapi import APIRouter, Depends, HTTPException
from database import supabase
from auth import verify_token

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
async def get_dashboard_stats(user_id: str = Depends(verify_token)):
    try:
        # Get lead counts by score
        hot_response = supabase.table("leads").select("id").eq("score", "hot").execute()
        warm_response = supabase.table("leads").select("id").eq("score", "warm").execute()
        cold_response = supabase.table("leads").select("id").eq("score", "cold").execute()

        # Get lead counts by status
        pending_response = supabase.table("leads").select("id").eq("status", "pending").execute()
        active_response = supabase.table("leads").select("id").eq("status", "active").execute()
        qualified_response = supabase.table("leads").select("id").eq("status", "qualified").execute()
        handed_off_response = supabase.table("leads").select("id").eq("status", "handed_off").execute()

        return {
            "by_score": {
                "hot": len(hot_response.data),
                "warm": len(warm_response.data),
                "cold": len(cold_response.data)
            },
            "by_status": {
                "pending": len(pending_response.data),
                "active": len(active_response.data),
                "qualified": len(qualified_response.data),
                "handed_off": len(handed_off_response.data)
            },
            "total": len(hot_response.data) + len(warm_response.data) + len(cold_response.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
