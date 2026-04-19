from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from database import supabase
from auth import verify_token

router = APIRouter(prefix="/manual-leads", tags=["manual-leads"])

class ManualLeadInput(BaseModel):
    first_name: str
    phone: str

@router.post("/add")
async def add_manual_lead(data: ManualLeadInput, user_id: str = Depends(verify_token)):
    """Manually add a single lead for testing"""
    try:
        if not data.first_name or not data.phone:
            raise HTTPException(status_code=400, detail="Name and phone are required")

        print(f"\n=== MANUAL LEAD ADD ===")
        print(f"Name: {data.first_name}, Phone: {data.phone}")

        # Insert lead
        lead = {
            "phone": data.phone,
            "first_name": data.first_name,
            "status": "pending",
            "score": "cold"
        }

        response = supabase.table("leads").insert(lead).execute()

        if response.data:
            lead_id = response.data[0]["id"]

            # Create qualification record
            qual = {
                "lead_id": lead_id,
                "completed_criteria": 0
            }
            supabase.table("qualifications").insert(qual).execute()

            print(f"✓ Lead added: {lead_id}")

            return {
                "message": "Lead added successfully",
                "lead_id": lead_id,
                "lead": response.data[0]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create lead")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
