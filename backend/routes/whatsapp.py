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

        # Get previous rental details from conversation history if any
        previous_details = {}
        qual_response = supabase.table("qualifications").select("special_notes").eq("lead_id", lead_id).execute()
        if qual_response.data and qual_response.data[0].get("special_notes"):
            import json as json_module
            try:
                previous_details = json_module.loads(qual_response.data[0]["special_notes"])
            except:
                previous_details = {}

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
        budget = qualification.get("budget", "not mentioned")
        start_date = qualification.get("start_date", "not mentioned")
        rental_duration_type = qualification.get("rental_duration_type", "not mentioned")
        car_model = qualification.get("car_model", "not mentioned")
        is_confirmation = qualification.get("is_confirmation", False)

        # Calculate all_details_present based on extracted values (more reliable than GPT)
        # Check for "not mentioned" as missing - need budget, start_date, and rental_duration_type
        all_details_present = (
            budget not in ["not mentioned"] and
            start_date not in ["not mentioned"] and
            rental_duration_type not in ["not mentioned"]
        )

        print(f"Extracted - Score: {score}, Budget: {budget}, Start Date: {start_date}, Duration Type: {rental_duration_type}, Car: {car_model}, Confirmation: {is_confirmation}, All Present: {all_details_present}")

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
                "budget": budget,
                "start_date": start_date,
                "rental_duration_type": rental_duration_type,
                "car_model": car_model,
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

        # Check for simple greetings FIRST
        greetings = ["hey", "hi", "hello", "yo", "sup", "what's up", "hey there", "hi there"]
        is_just_greeting = any(message_text.lower().strip().startswith(g) for g in greetings) and len(message_text.strip()) < 15

        # Check if it's a general question (contains "?")
        is_asking_question = "?" in message_text

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

        # PRIORITY 0 (HIGHEST): Simple greeting - just say hi back
        if is_just_greeting:
            if is_already_handled:
                # Just greet naturally, don't ask for anything
                greeting_responses = [
                    "Hey! What's up?",
                    "Hey there!",
                    "Yo!",
                    "What's going on?",
                    "Sup! How can I help?",
                    "Hey! 👋"
                ]
                import random
                ai_response = random.choice(greeting_responses)
            else:
                # Not yet handled, ask for budget
                ai_response = "Hey! What's your budget for the rental?"
            print(f"Greeting detected - responding naturally")
        # PRIORITY 1: If asking ANY question (at any stage), answer it
        elif is_asking_question and not is_asking_about_pricing:
            ai_response = openai_service.generate_response(first_name, message_text, conversation_history, lead_already_sent=is_already_handled)
            print(f"Answering general question")
        # PRIORITY 2: If user confirms (says yes/agree/etc) AND all booking details are present, send to sales guy
        elif has_confirmation_word and all_details_present and not is_already_handled:
            sales_phone = os.getenv("SALES_GUY_PHONE", "+37124402144")
            sales_msg = f"🎉 NEW LEAD\n\nName: {first_name}\nPhone: {phone}\nBudget: {budget}\nStart Date: {start_date}\nDuration: {rental_duration_type}\nCar Model: {car_model if car_model not in ['not mentioned'] else 'Not specified'}"

            # Send to sales guy via WhatsApp
            print(f"Sending lead to sales guy: {sales_msg}")
            twilio_whatsapp_service.send_text_message(sales_phone, sales_msg)

            # Mark as handled (with error handling - message was sent successfully)
            try:
                supabase.table("leads").update({"status": "sent_to_sales"}).eq("id", lead_id).execute()
                print(f"✓ Updated lead status to sent_to_sales")
            except Exception as e:
                print(f"⚠️ Warning: Could not update status, but message was sent: {e}")

            # Closing message with full details
            ai_response = f"Perfect! Our sales team will be in touch with you within minutes ;)"
        # PRIORITY 3: If all details NOW present but NOT confirming yet, ask for confirmation
        elif all_details_present and not has_confirmation_word and score in ["hot", "warm"]:
            # If car model not mentioned, ask for it before confirmation
            if car_model in ['not mentioned']:
                ai_response = f"Cool! So {budget} budget, starting {start_date}, for {rental_duration_type}. What specific car model you want?"
                print(f"All details present - asking for specific car model")
            else:
                # Car model provided, ask final confirmation
                confirmation_msg = f"Perfect! So {budget} budget, starting {start_date}, for {rental_duration_type}, {car_model} - all good?"
                ai_response = confirmation_msg
                print(f"All details including car model - asking confirmation")
        # PRIORITY 4: If some details missing, ask for them in order: budget → start_date → rental_duration_type
        elif not all_details_present:
            # Reset their lead if they're coming from a previous booking
            if lead.get("status") == "sent_to_sales":
                qual_resp = supabase.table("qualifications").select("id").eq("lead_id", lead_id).execute()
                if qual_resp.data:
                    supabase.table("qualifications").delete().eq("id", qual_resp.data[0]["id"]).execute()

            # Update their score, keep status as "qualified" for now
            supabase.table("leads").update({
                "score": score
            }).eq("id", lead_id).execute()

            # Ask for missing details in priority order - naturally
            missing = []
            if budget in ["not mentioned"]:
                missing.append("budget")
            if start_date in ["not mentioned"]:
                missing.append("when you need it")
            if rental_duration_type in ["not mentioned"]:
                missing.append("how long")

            if missing:
                # Vary the phrasing to sound natural
                if len(missing) == 3:
                    ai_response = "Cool! Just need to know your budget, when you need it, and how long for?"
                elif len(missing) == 2:
                    if "budget" in missing:
                        ai_response = f"Just need {missing[0]} and {missing[1]}?"
                    else:
                        ai_response = f"Need to know {missing[0]} and {missing[1]}?"
                else:
                    ai_response = f"One more thing - what's your {missing[0]}?"
            else:
                # All required details present, ask for specific car model
                ai_response = "Got it! What specific car model are you looking for? (like BMW M5, Tesla, Mercedes, etc.)"
        # PRIORITY 5: If customer wants a fresh inquiry with keywords, ask for missing info
        elif wants_fresh_inquiry:
            # For fresh inquiry, ask for budget first (standard flow) - natural phrasing
            ai_response = "No problem! What's your budget looking like?"
        # PRIORITY 6: If lead already sent to sales guy, only use natural AI responses for follow-up questions
        elif is_already_handled:
            ai_response = openai_service.generate_response(first_name, message_text, conversation_history, lead_already_sent=True)
        # PRIORITY 7: If customer asks about pricing, handle it specially
        elif is_asking_about_pricing:
            if all_details_present:
                ai_response = "Good question! Our sales team will send you exact pricing right away"
            else:
                missing_info = []
                if budget in ["not mentioned"]:
                    missing_info.append("your budget")
                if start_date in ["not mentioned"]:
                    missing_info.append("when you need it")
                if rental_duration_type in ["not mentioned"]:
                    missing_info.append("how long")
                ai_response = f"For sure! Let me know {', '.join(missing_info)}, then I'll get you the pricing"
        else:
            # For any follow-up questions after confirmation has been shown, respond naturally as customer support
            ai_response = openai_service.generate_response(first_name, message_text, conversation_history, lead_already_sent=is_already_handled)

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
