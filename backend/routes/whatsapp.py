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

        # Calculate all_details_present based on extracted values (more reliable than GPT)
        all_details_present = (
            car_type != "not specified" and
            duration != "not specified" and
            dates != "not specified"
        )

        print(f"Extracted - Score: {score}, Car: {car_type}, Duration: {duration}, Dates: {dates}, Confirmation: {is_confirmation}, All Present: {all_details_present}")

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

        # Check for pricing-related questions
        pricing_keywords = ["price", "cost", "how much", "afford", "expensive", "payment", "pay", "rate", "charge", "fee"]
        is_asking_about_pricing = any(word in message_text.lower() for word in pricing_keywords)

        # Check for greetings
        greetings = ["hey", "hi", "hello", "yo", "sup", "what's up"]
        is_just_greeting = any(message_text.lower().strip().startswith(g) for g in greetings) and len(message_text.strip()) < 10

        # Check for words that mean they DON'T want changes
        no_change_words = ["no different", "same", "keep it", "that's fine", "sounds good", "good with that", "perfect", "good", "fine"]
        wants_no_change = any(word in message_text.lower() for word in no_change_words)

        # Check for explicit confirmation words to be more reliable
        confirmation_words = ["yes", "agree", "ofc", "sure", "correct", "ok", "yep", "absolutely", "definitely", "sounds good"]
        has_confirmation_word = any(word in message_text.lower() for word in confirmation_words) or wants_no_change

        # Check if lead has already been sent to sales guy
        is_already_handled = lead.get("status") == "sent_to_sales"

        # Check if we've already shown them the confirmation message (they've seen the booking details once)
        # If they have all details and have received a confirmation message, any new message is either confirmation or support
        has_seen_confirmation = all_details_present and len(conversation_history.split("\n")) > 4

        # If lead already sent to sales guy, only use natural AI responses for follow-up questions
        if is_already_handled:
            ai_response = openai_service.generate_response(first_name, message_text, conversation_history)
        # PRIORITY 1: If user confirms (says yes/agree/etc) AND all booking details are present, send to sales guy
        elif has_confirmation_word and all_details_present:
            sales_phone = os.getenv("SALES_GUY_PHONE", "+37124402144")
            sales_msg = f"🎉 NEW LEAD\n\nName: {first_name}\nPhone: {phone}\nCar: {car_type}\nDuration: {duration}\nDates: {dates}"

            # Send to sales guy via WhatsApp
            print(f"Sending lead to sales guy: {sales_msg}")
            twilio_whatsapp_service.send_text_message(sales_phone, sales_msg)

            # Mark as handled
            supabase.table("leads").update({"status": "sent_to_sales"}).eq("id", lead_id).execute()

            # Closing message with full details
            ai_response = f"You're all set with the {car_type} for {duration} starting {dates}. I'll finalize the details and get back to you shortly!"
        # PRIORITY 2: If customer asks about pricing, handle it specially
        elif is_asking_about_pricing:
            if all_details_present:
                ai_response = "Great question! Our sales team will provide you with exact pricing. They'll have all your details ready ;)"
            else:
                missing_info = []
                if car_type == "not specified":
                    missing_info.append("car type")
                if duration == "not specified":
                    missing_info.append("duration")
                if dates == "not specified":
                    missing_info.append("dates")
                ai_response = f"Please provide me with all the details I need ({', '.join(missing_info)}), so I can forward you to our sales team and they will tell you the prices in a moment ;)"
        # PRIORITY 3: If all info collected and not yet confirmed, send confirmation message (but not for greetings)
        elif all_details_present and not has_confirmation_word and not is_just_greeting and not has_seen_confirmation:
            confirmation_msg = f"Just to confirm: {car_type}, for {duration}, {dates}. Correct?"
            ai_response = confirmation_msg
            print(f"Sending confirmation message")
        else:
            # For any follow-up questions after confirmation has been shown, respond naturally as customer support
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
