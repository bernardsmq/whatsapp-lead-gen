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

        # Get conversation history (including the message we just stored)
        conv_response = supabase.table("conversations").select("content, sender").eq("lead_id", lead_id).order("created_at", desc=False).execute()

        conversation_history = ""
        if conv_response.data:
            for msg in conv_response.data:
                sender = "Lead" if msg["sender"] == "user" else "Agent"
                conversation_history += f"{sender}: {msg['content']}\n"

        # Qualify the lead using OpenAI WITH full conversation history
        print(f"Qualifying lead with OpenAI...")
        qualification = openai_service.qualify_lead(first_name, message_text, conversation_history)

        score = qualification.get("lead_score", "cold")
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

        all_details_present = qualification.get("all_details_present", False)

        # Check for explicit confirmation words to be more reliable
        confirmation_words = ["yes", "agree", "ofc", "sure", "correct", "ok", "yep", "absolutely", "definitely", "sounds good"]
        has_confirmation_word = any(word in message_text.lower() for word in confirmation_words)

        # If user confirms (says yes/agree/etc) and we have some car details collected, send to sales guy
        if has_confirmation_word and car_type != "not specified":
            sales_phone = os.getenv("SALES_GUY_PHONE", "+37124402144")
            sales_msg = f"🎉 NEW LEAD\n\nName: {first_name}\nPhone: {phone}\nCar: {car_type}\nDuration: {duration}\nDates: {dates}"

            # Send to sales guy
            print(f"Sending lead to sales guy: {sales_msg}")
            twilio_whatsapp_service.send_text_message(sales_phone, sales_msg)

            ai_response = "Perfect! Our team will be in touch with you shortly :)"
        # If all info collected and not yet confirmed, send confirmation message
        elif all_details_present and not has_confirmation_word:
            confirmation_msg = f"Just to confirm: {car_type}, for {duration}, {dates}. Correct?"
            ai_response = confirmation_msg
            print(f"Sending confirmation message")
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
