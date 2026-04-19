from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from services.n8n_client import n8n_client
from auth import verify_token
import os

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.post("/start")
async def start_workflow(data: Dict, user_id: str = Depends(verify_token)):
    """Start n8n workflow to send WhatsApp messages to leads"""
    try:
        leads = data.get("leads", [])

        if not leads:
            raise HTTPException(status_code=400, detail="No leads provided")

        # Get n8n webhook URL from environment
        n8n_webhook = os.getenv("N8N_WEBHOOK_SEND_TEMPLATE")

        if not n8n_webhook:
            raise HTTPException(status_code=500, detail="n8n webhook not configured")

        print(f"\n=== WORKFLOW START ===")
        print(f"User: {user_id}")
        print(f"Triggering workflow for {len(leads)} leads")

        # Trigger workflow for each lead
        triggered_count = 0
        for lead in leads:
            try:
                print(f"Triggering workflow for lead {lead.get('lead_id')}")
                response = n8n_client.trigger_workflow_webhook(n8n_webhook, {
                    "lead_id": lead.get("lead_id"),
                    "phone": lead.get("phone"),
                    "first_name": lead.get("first_name")
                })
                triggered_count += 1
                print(f"✓ Triggered for {lead.get('first_name')}")
            except Exception as e:
                print(f"✗ Failed for lead {lead.get('lead_id')}: {str(e)}")
                continue

        print(f"=== WORKFLOW COMPLETE ===")
        print(f"Triggered: {triggered_count}/{len(leads)} leads\n")

        return {
            "message": "Workflow started successfully",
            "triggered_count": triggered_count,
            "total_leads": len(leads)
        }

    except Exception as e:
        print(f"Error starting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
