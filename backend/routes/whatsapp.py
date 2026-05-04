from fastapi import APIRouter, HTTPException, Request, Form, Depends
from services.twilio_whatsapp_service import twilio_whatsapp_service
from services.openai_service import openai_service
from services.conversation_manager import ConversationManager
from services.response_generator import ResponseGenerator
from database import supabase
import os
import json

from pydantic import BaseModel
from typing import List
from auth import verify_token

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

class BulkSendRequest(BaseModel):
    """Request model for bulk sending WhatsApp messages"""
    leads: List[dict]  # List of {name, phone} objects

@router.post("/test")
async def test_endpoint(request: Request):
    """Test endpoint to verify webhook is working"""
    try:
        form_data = await request.form()
        from_phone = form_data.get("From")
        message_text = form_data.get("Body")

        print(f"TEST: Received message from {from_phone}: {message_text}")

        if from_phone and message_text:
            clean_phone = from_phone.replace("whatsapp:", "")
            # Send simple test response
            test_response = f"TEST RECEIVED: {message_text}"
            twilio_whatsapp_service.send_text_message(clean_phone, test_response)
            print(f"TEST: Sent response to {clean_phone}")

        return {"status": "ok", "test": "working"}
    except Exception as e:
        print(f"TEST ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}

@router.post("/webhook")
async def webhook_receive(request: Request):
    """Receive incoming WhatsApp messages from Twilio"""
    try:
        # Twilio sends form data, not JSON
        form_data = await request.form()

        from_phone = form_data.get("From")  # Format: whatsapp:+1234567890
        message_text = form_data.get("Body")
        message_sid = form_data.get("MessageSid")

        print(f"\n=== INCOMING TWILIO MESSAGE ===")
        print(f"From: {from_phone}")
        print(f"Message: {message_text}")
        print(f"SID: {message_sid}")

        if message_text and from_phone:
            # Extract phone number from "whatsapp:+1234567890" format
            clean_phone = from_phone.replace("whatsapp:", "")
            print(f"Processing message from {clean_phone}: {message_text}")

            # Process the message
            await process_incoming_message(clean_phone, message_text, message_sid)

        return {"status": "ok"}

    except Exception as e:
        print(f"✗ Webhook error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}

async def process_incoming_message(phone: str, message_text: str, message_id: str):
    """
    Process incoming WhatsApp message using intelligent conversation manager.

    Flow:
    1. Load/create lead
    2. Check for opt-out immediately
    3. Store message in conversations
    4. Load conversation manager
    5. Extract fields from message
    6. Generate intelligent response
    7. Send response + log
    """
    try:
        print(f"\n=== INCOMING MESSAGE ===")
        print(f"From: {phone}")
        print(f"Message: {message_text[:100]}...")

        # STEP 1: Find or create lead
        response = supabase.table("leads").select("*").eq("phone", phone).execute()

        if not response.data:
            print(f"Lead not found, creating new lead")
            new_lead_response = supabase.table("leads").insert({
                "phone": phone,
                "first_name": "Customer",
                "score": "cold",
                "status": "qualified"
            }).execute()

            if not new_lead_response.data:
                print(f"✗ Failed to create lead")
                return

            lead = new_lead_response.data[0]
            lead_id = lead["id"]
            first_name = "Customer"
        else:
            lead = response.data[0]
            lead_id = lead["id"]
            first_name = lead.get("first_name", "Customer")

        print(f"✓ Lead: {first_name} ({lead_id})")

        # STEP 2: Check for opt-out immediately
        message_lower = message_text.lower()
        optout_keywords = ["don't message", "do not message", "don't text", "do not text", "stop messaging",
                          "stop texting", "unsubscribe", "do not contact", "dont message", "dont text",
                          "don't contact", "no messages", "remove me", "stop"]

        if any(keyword in message_lower for keyword in optout_keywords):
            print(f"✓ Opt-out detected")
            supabase.table("leads").update({"status": "do_not_contact"}).eq("id", lead_id).execute()
            twilio_whatsapp_service.send_text_message(phone, "Ok no problem 👍")
            supabase.table("conversations").insert({
                "lead_id": lead_id,
                "content": "Ok no problem 👍",
                "sender": "ai"
            }).execute()
            print(f"✓ Opt-out handled")
            return

        # STEP 3: Store incoming message
        supabase.table("conversations").insert({
            "lead_id": lead_id,
            "content": message_text,
            "sender": "user"
        }).execute()

        # STEP 4: Load conversation manager
        conv_mgr = ConversationManager(lead_id, supabase)
        conversation_history = conv_mgr.get_conversation_history_text()

        # STEP 5: Extract fields from message using GPT
        print(f"Extracting fields from message...")
        extracted_fields = openai_service.extract_all_fields(message_text, conversation_history)
        print(f"Extracted fields: {extracted_fields}")

        # STEP 6: Generate intelligent response using ResponseGenerator
        responder = ResponseGenerator(first_name, conv_mgr)
        ai_response = responder.generate(message_text, extracted_fields)

        print(f"Generated response: {ai_response}")

        # STEP 7: Send response and log
        twilio_whatsapp_service.send_text_message(phone, ai_response)
        supabase.table("conversations").insert({
            "lead_id": lead_id,
            "content": ai_response,
            "sender": "ai"
        }).execute()

        print(f"✓ Response sent to {first_name}")

        # Check if ready for sales and send to sales team if confirmed
        if conv_mgr.is_ready_for_sales() and conv_mgr.is_confirmed():
            print(f"✓ Lead ready for sales handoff")
            supabase.table("leads").update({
                "status": "sent_to_sales",
                "score": "warm"
            }).eq("id", lead_id).execute()

    except Exception as e:
        print(f"✗ Error processing message: {str(e)}")
        import traceback
        traceback.print_exc()


@router.post("/send-bulk")
async def send_bulk_messages(request: BulkSendRequest, user_id: str = Depends(verify_token)):
    """Send WhatsApp template messages to multiple leads"""
    try:
        print(f"\n=== BULK SEND START ===")
        print(f"User ID: {user_id}")
        print(f"Sending to {len(request.leads)} leads")

        results = []

        for idx, lead in enumerate(request.leads):
            try:
                name = lead.get("name", "Customer")
                phone = lead.get("phone", "")

                if not phone:
                    results.append({
                        "name": name,
                        "phone": phone,
                        "status": "failed",
                        "error": "Missing phone number"
                    })
                    continue

                print(f"[{idx + 1}/{len(request.leads)}] Sending to {name} ({phone})")

                # Send template message
                send_result = twilio_whatsapp_service.send_template_message(phone, name)

                # Find or create the lead by phone number
                lead_response = supabase.table("leads").select("id").eq("phone", phone).execute()
                if lead_response.data:
                    lead_id = lead_response.data[0]["id"]
                else:
                    # Create new lead if doesn't exist
                    new_lead_response = supabase.table("leads").insert({
                        "phone": phone,
                        "first_name": name,
                        "score": "cold",
                        "status": "qualified"
                    }).execute()
                    lead_id = new_lead_response.data[0]["id"] if new_lead_response.data else None

                # Store template message as a conversation record with status tracking
                if lead_id and send_result.get("sid"):
                    try:
                        supabase.table("conversations").insert({
                            "lead_id": lead_id,
                            "message_type": "template",
                            "sender": "template",
                            "content": "Template message sent (details stored in template_sid and template_variables)",
                            "message_sid": send_result.get("sid"),
                            "template_sid": send_result.get("template_sid"),
                            "template_variables": json.dumps(send_result.get("template_variables", {})),
                            "delivery_status": "sent"
                        }).execute()
                        print(f"  ✓ Stored template message for {name}")
                    except Exception as e:
                        print(f"  ⚠️ Warning: Could not store template message: {str(e)}")

                results.append({
                    "name": name,
                    "phone": phone,
                    "status": "sent",
                    "sid": send_result.get("sid")
                })

            except Exception as e:
                print(f"Failed to send to {lead.get('name')}: {str(e)}")
                results.append({
                    "name": lead.get("name", "Unknown"),
                    "phone": lead.get("phone", ""),
                    "status": "failed",
                    "error": str(e)
                })

        # Count successes and failures
        sent_count = sum(1 for r in results if r["status"] == "sent")
        failed_count = sum(1 for r in results if r["status"] == "failed")

        print(f"=== BULK SEND COMPLETE ===")
        print(f"Sent: {sent_count}, Failed: {failed_count}\n")

        return {
            "message": "Bulk send completed",
            "total": len(request.leads),
            "sent": sent_count,
            "failed": failed_count,
            "results": results
        }

    except Exception as e:
        print(f"✗ Bulk send error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook/status")
async def webhook_status_callback(request: Request):
    """Receive Twilio message status callbacks"""
    try:
        form_data = await request.form()

        message_sid = form_data.get("MessageSid")
        message_status = form_data.get("MessageStatus")  # Values: sent, delivered, read, failed, undelivered

        print(f"\n=== TWILIO STATUS CALLBACK ===")
        print(f"MessageSid: {message_sid}")
        print(f"Status: {message_status}")

        # Map Twilio status to our status values
        status_map = {
            "sent": "sent",
            "delivered": "delivered",
            "read": "read",
            "failed": "failed",
            "undelivered": "failed"
        }

        db_status = status_map.get(message_status, message_status)

        # Update conversation record with status
        if message_sid:
            from datetime import datetime
            try:
                result = supabase.table("conversations").update({
                    "delivery_status": db_status,
                    "delivery_timestamp": datetime.utcnow().isoformat()
                }).eq("message_sid", message_sid).execute()

                if result.data:
                    print(f"✓ Updated message status to: {db_status}")
                else:
                    print(f"⚠️ No message found with SID: {message_sid}")
            except Exception as e:
                print(f"Error updating message status: {str(e)}")

        return {"status": "ok"}

    except Exception as e:
        print(f"✗ Status callback error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}
