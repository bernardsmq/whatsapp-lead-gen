from fastapi import APIRouter, HTTPException, Request, Form
from services.twilio_whatsapp_service import twilio_whatsapp_service
from services.openai_service import openai_service
from database import supabase
import os
import json

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

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
            "content": message_text,
            "sender": "user"
        }).execute()

        # Qualify the lead using OpenAI
        print(f"Qualifying lead with OpenAI...")
        qualification = openai_service.qualify_lead(first_name, message_text)

        score = qualification.get("score", "cold")
        car_type = qualification.get("car_type", "not specified")
        duration = qualification.get("duration", "not specified")
        dates = qualification.get("dates", "not specified")
        is_confirmation = qualification.get("is_confirmation", False)

        print(f"Score: {score}, Car: {car_type}, Duration: {duration}, Dates: {dates}, Is Confirmation: {is_confirmation}")

        # Update lead score
        supabase.table("leads").update({
            "score": score,
            "status": "qualified"
        }).eq("id", lead_id).execute()

        # Update or create qualification record with extracted details
        qual_response = supabase.table("qualifications").select("id, special_notes").eq("lead_id", lead_id).execute()

        # Store rental details as JSON in special_notes
        qual_data = {
            "lead_id": lead_id,
            "completed_criteria": 1 if score in ["hot", "warm"] else 0,
            "special_notes": json.dumps({
                "car_type": car_type,
                "duration": duration,
                "dates": dates,
                "confirmation_sent": False
            })
        }

        if qual_response.data:
            qual_id = qual_response.data[0]["id"]
            supabase.table("qualifications").update(qual_data).eq("id", qual_id).execute()
        else:
            supabase.table("qualifications").insert(qual_data).execute()

        print(f"✓ Lead qualified as {score}")

        # Get conversation history for context
        conv_response = supabase.table("conversations").select("content, sender").eq("lead_id", lead_id).order("created_at", desc=False).execute()

        conversation_history = ""
        if conv_response.data:
            for msg in conv_response.data:
                sender = "Lead" if msg["sender"] == "user" else "Agent"
                conversation_history += f"{sender}: {msg['content']}\n"

        # Check if all required info is collected
        has_car = car_type != "not specified" and car_type.lower() != "unknown"
        has_duration = duration != "not specified" and duration.lower() != "unknown"
        has_dates = dates != "not specified" and dates.lower() != "unknown"
        all_info_collected = has_car and has_duration and has_dates

        # If all info collected and not yet confirmed, send confirmation message
        if all_info_collected and not is_confirmation:
            confirmation_msg = f"Just to confirm: {car_type}, for {duration}, {dates}. Correct?"
            ai_response = confirmation_msg
            print(f"Sending confirmation message")
        # If positive confirmation, send to sales guy
        elif is_confirmation and all_info_collected:
            sales_msg = f"🎉 NEW LEAD\n\nName: {first_name}\nPhone: {phone}\nCar: {car_type}\nDuration: {duration}\nDates: {dates}"

            # Send to sales guy
            print(f"Sending lead to sales guy: {sales_msg}")
            twilio_whatsapp_service.send_text_message("+37124402144", sales_msg)

            ai_response = "Perfect! Our sales team will be in touch shortly. Thanks!"
        else:
            # Continue collecting info
            ai_response = openai_service.generate_response(first_name, message_text, conversation_history)

        print(f"AI Response: {ai_response}")

        # Send response back via WhatsApp
        twilio_whatsapp_service.send_text_message(phone, ai_response)

        # Store our response in conversations
        supabase.table("conversations").insert({
            "lead_id": lead_id,
            "content": ai_response,
            "sender": "ai"
        }).execute()

        print(f"✓ Message processed and response sent")

    except Exception as e:
        print(f"✗ Error processing message: {str(e)}")
        import traceback
        traceback.print_exc()
