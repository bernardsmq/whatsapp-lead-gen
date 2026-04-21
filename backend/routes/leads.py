from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from database import supabase
from auth import verify_token

router = APIRouter(prefix="/leads", tags=["leads"])

class Lead(BaseModel):
    phone: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None

class Qualification(BaseModel):
    when_needed: Optional[str] = None
    car_type: Optional[str] = None
    timeframe: Optional[str] = None
    duration: Optional[str] = None
    special_notes: Optional[str] = None

@router.get("/")
async def get_leads(user_id: str = Depends(verify_token), status_filter: Optional[str] = None, score_filter: Optional[str] = None):
    try:
        print(f"\n=== GET /leads ===")
        print(f"User ID: {user_id}")
        print(f"Status filter: {status_filter}")
        print(f"Score filter: {score_filter}")

        query = supabase.table("leads").select("*, qualifications(*)")

        if status_filter:
            print(f"Applying status filter: {status_filter}")
            query = query.eq("status", status_filter)
        if score_filter:
            print(f"Applying score filter: {score_filter}")
            query = query.eq("score", score_filter)

        print(f"Executing query...")
        response = query.execute()

        print(f"✓ Got {len(response.data) if response.data else 0} leads")
        return response.data
    except Exception as e:
        print(f"✗ Error in GET /leads: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{lead_id}")
async def get_lead(lead_id: str, user_id: str = Depends(verify_token)):
    try:
        response = supabase.table("leads").select("*, qualifications(*)").eq("id", lead_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Lead not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{lead_id}/conversations")
async def get_lead_conversations(lead_id: str, user_id: str = Depends(verify_token)):
    try:
        response = supabase.table("conversations").select("*").eq("lead_id", lead_id).order("created_at", desc=False).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{lead_id}/qualification")
async def update_qualification(lead_id: str, qual: Qualification, user_id: str = Depends(verify_token)):
    try:
        # Count completed criteria
        completed = sum([
            qual.when_needed is not None,
            qual.car_type is not None,
            qual.timeframe is not None,
            qual.duration is not None
        ])

        # Determine score
        if completed == 4:
            score = "hot"
        elif completed > 0:
            score = "warm"
        else:
            score = "cold"

        # Update qualification
        response = supabase.table("qualifications").upsert({
            "lead_id": lead_id,
            "when_needed": qual.when_needed,
            "car_type": qual.car_type,
            "timeframe": qual.timeframe,
            "duration": qual.duration,
            "special_notes": qual.special_notes,
            "completed_criteria": completed
        }).execute()

        # Update lead score
        supabase.table("leads").update({"score": score}).eq("id", lead_id).execute()

        return response.data[0] if response.data else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
