from fastapi import APIRouter, HTTPException, Query, Request
from services.whatsapp_service import whatsapp_service
from services.openai_service import openai_service
from database import supabase
import os
import json

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "your-verify-token")

@router.get("/webhook")
async def webhook_verify(
    mode: str = Query(None),
    challenge: str = Query(None),
    token: str = Query(None)
):
    """Webhook verification endpoint for WhatsApp"""
    print(f"Webhook verification request - mode: {mode}, token: {token}")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        print(f"✓ Webhook verified")
        return challenge
    else:
        print(f"✗ Invalid webhook token")
        raise HTTPException(status_code=403, detail="Invalid verification token")

@router.post("/webhook")
async def webhook_receive(request: Request):
    """Receive incoming WhatsApp messages"""
    try:
        body = await request.json()
        print(f"\n=== INCOMING MESSAGE ===")
        print(json.dumps(body, indent=2))

        # Check if this is a message event
        if body.get("object") != "whatsapp_business_account":
            print("Not a WhatsApp business account event")
            return {"status": "ok"}

        entries = body.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})

                # Check for incoming messages
                messages = value.get("messages", [])
                for message in messages:
                    from_phone = message.get("from")
                    message_id = message.get("id")
                    message_text = None
                    message_type = message.get("type")

                    if message_type == "text":
                        message_text = message.get("text", {}).get("body", "")

                    if message_text and from_phone:
                        print(f"Message from {from_phone}: {message_text}")

                        # Process the message
                        await process_incoming_message(from_phone, message_text, message_id)

        return {"status": "ok"}

    except Exception as e:
        print(f"✗ Webhook error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}

async def process_incoming_message(phone: str, message_text: str, message_id: str):
    """Process incoming WhatsApp message and qualify lead"""
    try:
        print(f"\nProcessing message from {phone}")

        # Find lead by phone number
        response = supabase.table("leads").select("*").eq("phone", phone).execute()

        if not response.data:
            print(f"Lead not found for phone {phone}")
            return

        lead = response.data[0]
        lead_id = lead["id"]
        first_name = lead.get("first_name", "Lead")

        print(f"Found lead: {first_name}")

        # Store conversation message
        supabase.table("conversations").insert({
            "lead_id": lead_id,
            "message": message_text,
            "sender": "lead"
        }).execute()

        # Qualify the lead using OpenAI
        print(f"Qualifying lead with OpenAI...")
        qualification = openai_service.qualify_lead(first_name, message_text)

        score = qualification.get("score", "cold")
        indicators = qualification.get("indicators", [])
        next_action = qualification.get("next_action", "Follow up")

        print(f"Score: {score}")
        print(f"Indicators: {indicators}")

        # Update lead score
        supabase.table("leads").update({
            "score": score,
            "status": "qualified"
        }).eq("id", lead_id).execute()

        # Update or create qualification record
        qual_data = {
            "lead_id": lead_id,
            "completed_criteria": 1 if score in ["hot", "warm"] else 0,
            "special_notes": f"Indicators: {', '.join(indicators[:2])}"
        }

        # Try to update existing, if not create new
        supabase.table("qualifications").upsert(qual_data).execute()

        print(f"✓ Lead qualified as {score}")

        # Generate and send AI response
        ai_response = openai_service.generate_response(first_name, message_text)
        print(f"AI Response: {ai_response}")

        # Send response back via WhatsApp
        whatsapp_service.send_text_message(phone, ai_response)

        # Store our response in conversations
        supabase.table("conversations").insert({
            "lead_id": lead_id,
            "message": ai_response,
            "sender": "agent"
        }).execute()

        print(f"✓ Message processed and response sent")

    except Exception as e:
        print(f"✗ Error processing message: {str(e)}")
        import traceback
        traceback.print_exc()
