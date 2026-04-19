from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from services.twilio_whatsapp_service import twilio_whatsapp_service
from database import supabase
from auth import verify_token
import asyncio

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.post("/start")
async def start_workflow(data: Dict, user_id: str = Depends(verify_token)):
    """Send WhatsApp messages to all leads via Twilio"""
    try:
        leads = data.get("leads", [])

        if not leads:
            raise HTTPException(status_code=400, detail="No leads provided")

        print(f"\n=== WORKFLOW START (TWILIO) ===")
        print(f"User: {user_id}")
        print(f"Sending WhatsApp to {len(leads)} leads")

        # Send WhatsApp message to each lead
        sent_count = 0
        failed_count = 0

        for lead in leads:
            try:
                phone = lead.get("phone")
                first_name = lead.get("first_name")

                print(f"Sending WhatsApp to {first_name} ({phone})")

                # Send WhatsApp message via Twilio
                twilio_whatsapp_service.send_template_message(phone, first_name)

                # Update lead status to "contacted"
                lead_id = lead.get("lead_id")
                if lead_id:
                    supabase.table("leads").update({
                        "status": "contacted"
                    }).eq("id", lead_id).execute()

                sent_count += 1
                print(f"✓ Message sent to {first_name}")

            except Exception as e:
                print(f"✗ Failed for {lead.get('first_name')}: {str(e)}")
                failed_count += 1
                continue

        print(f"=== WORKFLOW COMPLETE ===")
        print(f"Sent: {sent_count}/{len(leads)} leads\n")

        return {
            "message": "Workflow started successfully",
            "sent_count": sent_count,
            "failed_count": failed_count,
            "total_leads": len(leads)
        }

    except Exception as e:
        print(f"Error starting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
