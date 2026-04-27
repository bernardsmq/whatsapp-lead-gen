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

        # Get previous car from conversation history if any
        previous_car = None
        qual_response = supabase.table("qualifications").select("special_notes").eq("lead_id", lead_id).execute()
        if qual_response.data and qual_response.data[0].get("special_notes"):
            import json as json_module
            try:
                notes = json_module.loads(qual_response.data[0]["special_notes"])
                previous_car = notes.get("car_type", "").lower()
            except:
                previous_car = None

        # Car brands including abbreviations
        car_brands = {
            "bmw": "bmw",
            "audi": "audi",
            "mercedes": "mercedes",
            "tesla": "tesla",
            "porsche": "porsche",
            "lamborghini": "lamborghini",
            "lambo": "lamborghini",
            "ferrari": "ferrari",
            "jeep": "jeep",
            "ford": "ford",
            "chevy": "chevy",
            "honda": "honda",
            "toyota": "toyota",
            "nissan": "nissan",
            "range rover": "range rover",
            "bentley": "bentley",
            "rolls royce": "rolls royce",
            "bugatti": "bugatti",
            "maserati": "maserati"
        }

        message_lower = message_text.lower()
        mentioned_car = None
        for car_key, car_name in car_brands.items():
            if car_key in message_lower:
                mentioned_car = car_name
                break

        # Check if customer wants a fresh inquiry (different car, new inquiry, etc)
        fresh_inquiry_keywords = ["another car", "different car", "new car", "different", "change car", "i need another", "want another", "looking for another"]
        wants_fresh_inquiry = any(keyword in message_lower for keyword in fresh_inquiry_keywords)

        # Also trigger fresh inquiry if they mention a car and already have a previous booking
        if mentioned_car and lead.get("status") == "sent_to_sales":
            wants_fresh_inquiry = True
            print(f"Fresh inquiry: mentioned {mentioned_car}")

        # If they want a fresh inquiry, reset their status and clear booking details
        if wants_fresh_inquiry and lead.get("status") == "sent_to_sales":
            print(f"Fresh inquiry detected for {first_name} - resetting status")
            supabase.table("leads").update({
                "score": "cold",
                "status": "new_inquiry"
            }).eq("id", lead_id).execute()

            # Clear previous qualification
            qual_response = supabase.table("qualifications").select("id").eq("lead_id", lead_id).execute()
            if qual_response.data:
                qual_id = qual_response.data[0]["id"]
                supabase.table("qualifications").delete().eq("id", qual_id).execute()

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
        # Check for both "not specified" and "not mentioned" as missing
        all_details_present = (
            car_type not in ["not specified", "not mentioned"] and
            duration not in ["not specified", "not mentioned"] and
            dates not in ["not specified", "not mentioned"]
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

        # Check if lead has already been sent to sales guy (but not if they're requesting a fresh inquiry)
        is_already_handled = lead.get("status") == "sent_to_sales" and not wants_fresh_inquiry

        # Check if we've already shown them the confirmation message (they've seen the booking details once)
        # If they have all details and have received a confirmation message, any new message is either confirmation or support
        has_seen_confirmation = all_details_present and len(conversation_history.split("\n")) > 4

        # PRIORITY 0: If car mentioned but missing dates/duration - ask for missing info
        # The AI already extracted car_type from the message, so if car_type != "not specified" they mentioned a car
        is_missing_details = dates in ["not specified", "not mentioned"] or duration in ["not specified", "not mentioned"]

        if car_type not in ["not specified", "not mentioned"] and is_missing_details:
            # Reset their lead if they're coming from a previous booking
            if lead.get("status") == "sent_to_sales":
                qual_resp = supabase.table("qualifications").select("id").eq("lead_id", lead_id).execute()
                if qual_resp.data:
                    supabase.table("qualifications").delete().eq("id", qual_resp.data[0]["id"]).execute()

            # Update their score, keep status as "qualified" for now
            supabase.table("leads").update({
                "score": score
            }).eq("id", lead_id).execute()

            # Ask for missing info
            missing = []
            if dates in ["not specified", "not mentioned"]:
                missing.append("when you need it")
            if duration in ["not specified", "not mentioned"]:
                missing.append("for how long")
            ai_response = f"Got it! Now I just need to know {' and '.join(missing)}."
        # If customer wants a fresh inquiry with keywords, ask for missing info
        elif wants_fresh_inquiry:
            new_car_type = mentioned_car if mentioned_car else "not specified"
            missing_info = []
            if new_car_type == "not specified":
                missing_info.append("car type")
            missing_info.append("when you need it")
            missing_info.append("for how long")
            missing_text = " and ".join(missing_info)
            ai_response = f"Got it! Now I just need to know {missing_text}."
        # If lead already sent to sales guy, only use natural AI responses for follow-up questions
        elif is_already_handled:
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
