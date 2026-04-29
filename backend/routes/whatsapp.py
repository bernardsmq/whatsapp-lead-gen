from fastapi import APIRouter, HTTPException, Request, Form, Depends
from services.twilio_whatsapp_service import twilio_whatsapp_service
from services.openai_service import openai_service
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
    """Process incoming WhatsApp message and qualify lead"""
    try:
        print(f"\nProcessing message from {phone}")

        # Find lead by phone number
        response = supabase.table("leads").select("*").eq("phone", phone).execute()

        if not response.data:
            print(f"Lead not found for phone {phone}, creating new lead")
            # Create a new lead if one doesn't exist
            new_lead_response = supabase.table("leads").insert({
                "phone": phone,
                "first_name": "Customer",
                "score": "cold",
                "status": "qualified"
            }).execute()

            if new_lead_response.data:
                lead = new_lead_response.data[0]
                lead_id = lead["id"]
                first_name = "Customer"
                print(f"✓ Created new lead: {lead_id}")
            else:
                print(f"✗ Failed to create lead for {phone}")
                return
        else:
            lead = response.data[0]
            lead_id = lead["id"]
            first_name = lead.get("first_name", "Customer")
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
        rental_duration = qualification.get("rental_duration", "not mentioned")
        car_model = qualification.get("car_model", "not mentioned")
        is_confirmation = qualification.get("is_confirmation", False)

        # Calculate all_details_present based on extracted values (more reliable than GPT)
        # Check for "not mentioned" as missing - need budget, start_date, and rental_duration
        all_details_present = (
            budget not in ["not mentioned"] and
            start_date not in ["not mentioned"] and
            rental_duration not in ["not mentioned"]
        )

        print(f"Extracted - Score: {score}, Budget: {budget}, Start Date: {start_date}, Duration: {rental_duration}, Car: {car_model}, Confirmation: {is_confirmation}, All Present: {all_details_present}")

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
                "rental_duration": rental_duration,
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

        # Initialize ai_response to ensure it's always defined
        ai_response = None

        # Check for pricing-related questions
        pricing_keywords = ["price", "cost", "how much", "afford", "expensive", "payment", "pay", "rate", "charge", "fee"]
        is_asking_about_pricing = any(word in message_text.lower() for word in pricing_keywords)

        # Check for simple greetings FIRST
        greetings = ["hey", "hi", "hello", "yo", "sup", "what's up", "hey there", "hi there"]
        is_just_greeting = any(message_text.lower().strip().startswith(g) for g in greetings) and len(message_text.strip()) < 15

        # Check if it's a general question (contains "?" OR common question words)
        question_indicators = ["?", "how", "what", "why", "when", "where", "which", "who", "can you", "could you", "do you", "does", "is", "are", "will you", "would you"]
        is_asking_question = any(word in message_text.lower() for word in question_indicators)

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

        # PRIORITY 0 (HIGHEST): Simple greeting - ask what car type they need
        if is_just_greeting:
            if is_already_handled:
                # Just greet professionally, don't ask for anything
                greeting_responses = [
                    "Hello! How can I assist you?",
                    "Hi there! What can I help with?",
                    "Good to hear from you! How may I help?",
                    "Hello! Is there anything else I can help with?",
                    "Hi! How are you doing today?"
                ]
                import random
                ai_response = random.choice(greeting_responses)
            else:
                # Not yet handled, ask for CAR TYPE first with categories
                ai_response = "Hello! Welcome to our car rental service. What type of car would you like? We offer economy, luxury, sports, SUV, and offroad options."
            print(f"Greeting detected - responding professionally")
        # PRIORITY 1: If asking ANY question (at any stage), answer it
        elif is_asking_question and not is_asking_about_pricing:
            ai_response = openai_service.generate_response(first_name, message_text, conversation_history, lead_already_sent=is_already_handled)
            print(f"Answering general question")
        # PRIORITY 2: If user confirms (says yes/agree/etc) AND all booking details are present, send to sales guy
        elif has_confirmation_word and all_details_present and not is_already_handled:
            sales_phone = os.getenv("SALES_GUY_PHONE", "+37124402144")
            sales_msg = f"🎉 NEW LEAD\n\nName: {first_name}\nPhone: {phone}\nBudget: {budget}\nStart Date: {start_date}\nDuration: {rental_duration}\nCar Model: {car_model if car_model not in ['not mentioned'] else 'Not specified'}"

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
            ai_response = f"Thank you! Your inquiry has been received. Our sales team will contact you shortly with a detailed quote."
        # PRIORITY 3: If all details NOW present but NOT confirming yet, ask for confirmation
        elif all_details_present and not has_confirmation_word and score in ["hot", "warm"]:
            # Check if car_model is just a category, not a specific model
            car_categories = ["economy", "luxury", "sports", "suv", "offroad", "daily", "premium"]
            is_just_category = car_model.lower() in car_categories if car_model not in ['not mentioned'] else False

            # If car model not mentioned OR just a category, ask for specific model
            if car_model in ['not mentioned'] or is_just_category:
                category_text = f"{car_model.upper()}" if is_just_category else "a"
                ai_response = f"Thank you. You want {category_text}. What specific model? (Like BMW X5, Range Rover, Tesla Model Y, etc.)"
                print(f"All details present - asking for specific car model")
            else:
                # Car model is specific, ask final confirmation
                confirmation_msg = f"Excellent. Let me confirm your details: {car_model}, budget {budget}, starting {start_date}, for {rental_duration}. Is everything correct?"
                ai_response = confirmation_msg
                print(f"All details including specific car model - asking confirmation")
        # PRIORITY 4: If some details missing, ask for them in order: budget → start_date → rental_duration
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

            # Ask for missing details in priority order: car_model → budget → start_date → rental_duration
            # But check conversation history to avoid re-asking the same thing
            car_question_keywords = ["what type", "what car", "economy", "luxury", "sports", "suv", "offroad", "daily", "bmw", "tesla", "mercedes", "lamborghini", "model"]
            budget_question_keywords = ["budget", "how much", "cost", "price", "afford", "$", "per day", "per week"]
            date_question_keywords = ["when", "date", "tomorrow", "next week", "this week", "april", "may", "june"]
            duration_question_keywords = ["how long", "duration", "days", "weeks", "months", "short-term", "long-term"]

            # Check what we already asked by looking at conversation history
            conv_lower = conversation_history.lower()
            already_asked_car = any(kw in conv_lower for kw in car_question_keywords)
            already_asked_budget = any(kw in conv_lower for kw in budget_question_keywords)
            already_asked_date = any(kw in conv_lower for kw in date_question_keywords)
            already_asked_duration = any(kw in conv_lower for kw in duration_question_keywords)

            # Check if car_model is just a category
            car_categories = ["economy", "luxury", "sports", "suv", "offroad", "daily", "premium"]
            is_just_category = car_model.lower() in car_categories if car_model not in ['not mentioned'] else False

            if (car_model in ["not mentioned"] or is_just_category) and not already_asked_car:
                if is_just_category:
                    ai_response = f"Great choice on {car_model.upper()}! What specific model? (Like BMW X5, Tesla Model Y, Range Rover, etc.)"
                else:
                    ai_response = "Could you please tell me what type of car you would prefer? We offer economy, luxury, sports, SUV, and offroad vehicles."
            elif budget in ["not mentioned"] and not already_asked_budget:
                ai_response = "Thank you. What would be your budget for the rental?"
            elif start_date in ["not mentioned"] and not already_asked_date:
                ai_response = "When would you like to start your rental?"
            elif rental_duration in ["not mentioned"] and not already_asked_duration:
                ai_response = "How many days or months would you need the vehicle for? For example: 5 days, 2 weeks, 1 month, 3 months, etc."
            else:
                # Don't repeat questions - just acknowledge and move forward
                if car_model in ["not mentioned"]:
                    ai_response = "Thank you. What type of vehicle would you prefer?"
                elif budget in ["not mentioned"]:
                    ai_response = "And what would be your budget?"
                elif start_date in ["not mentioned"]:
                    ai_response = "When would you need to start the rental?"
                elif rental_duration in ["not mentioned"]:
                    ai_response = "How many days or months would you need it for?"
                else:
                    ai_response = "Thank you for that information!"
        # PRIORITY 5: If customer wants a fresh inquiry with keywords, ask for car type first
        elif wants_fresh_inquiry:
            # For fresh inquiry, ask for car type first (standard flow)
            ai_response = "No problem. I'd be happy to help with a new inquiry. What type of vehicle would you prefer?"
        # PRIORITY 6: If lead already sent to sales guy, only use natural AI responses for follow-up questions
        elif is_already_handled:
            ai_response = openai_service.generate_response(first_name, message_text, conversation_history, lead_already_sent=True)
        # PRIORITY 7: If customer asks about pricing, handle it specially
        elif is_asking_about_pricing:
            if all_details_present:
                ai_response = "Thank you for your interest. Our sales team will provide you with a detailed pricing quote right away."
            else:
                missing_info = []
                if budget in ["not mentioned"]:
                    missing_info.append("your budget")
                if start_date in ["not mentioned"]:
                    missing_info.append("your start date")
                if rental_duration in ["not mentioned"]:
                    missing_info.append("the rental duration")
                ai_response = f"I'd be happy to help with pricing. Could you please provide {' and '.join(missing_info)}?"
        else:
            # For any follow-up questions after confirmation has been shown, respond naturally as customer support
            ai_response = openai_service.generate_response(first_name, message_text, conversation_history, lead_already_sent=is_already_handled)

        # Safety check - make sure we have a response to send
        if not ai_response:
            ai_response = openai_service.generate_response(first_name, message_text, conversation_history, lead_already_sent=is_already_handled)
            print(f"⚠️ No response generated, using fallback AI response")

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
