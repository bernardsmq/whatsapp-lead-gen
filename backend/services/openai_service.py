import os
from openai import OpenAI
from typing import Dict

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OPENAI_API_KEY not configured")
        self.client = OpenAI(api_key=api_key)

    def qualify_lead(self, lead_name: str, message: str, conversation_history: str = "") -> Dict:
        """Use GPT to qualify a lead based on their message response"""
        try:
            prompt = f"""You are a car rental lead qualification expert. Analyze the conversation carefully.

FULL CONVERSATION:
{conversation_history}

Latest message: "{message}"

EXTRACT these details from the LATEST message:
1. budget - How much will they spend? Look for: "$100 per day", "5000", "budget-friendly", "premium", "under 100", "$600", "600$", "AED 500", etc. Return "not mentioned" if not stated.
2. start_date - When do they need the car? Look for: "tomorrow", "next week", "April 29", "this Friday", specific dates/times. Return "not mentioned" if not stated.
3. rental_duration - How long? Extract from ANY context: "5 days", "2 weeks", "3 months", "1 week", "24H", "24 hours", "48 hours", etc. Return "not mentioned" if duration not stated. Include the unit (days/weeks/months/hours).
4. car_model - What car do they want? Extract car TYPES: economy, luxury, sports, SUV, offroad, daily, etc. OR specific brands/models: BMW, Tesla, Mercedes, Lamborghini, BMW M5, Tesla Model 3, Ferrari, etc. Return "not mentioned" ONLY if they said nothing about cars.
5. is_confirmation - Is latest message confirming previous details? ("yes", "agree", "sure", "correct", "sounds good", etc)
6. all_details_present - Are the THREE REQUIRED details present: budget, start_date, AND rental_duration? (car_model is optional)
7. lead_score - hot/warm/cold based on urgency and completion of required details

Examples:
- "I need a car tomorrow for 2 weeks, budget is 100 per day" → start_date="tomorrow", rental_duration="2 weeks", budget="100 per day", car_model="not mentioned"
- "BMW, next week, 5 days, $80/day" → car_model="BMW", start_date="next week", rental_duration="5 days", budget="$80/day"
- "3 months rental" → rental_duration="3 months"
- "how much is it for 24H?" → rental_duration="24H" (extract from pricing question)
- "600$" → budget="600$"
- "Just say yes to confirm" → is_confirmation=true, other fields from context

RETURN: Valid JSON with exactly these fields: budget, start_date, rental_duration, car_model, is_confirmation, all_details_present, lead_score"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )

            result = response.choices[0].message.content
            print(f"GPT Response: {result}")

            # Parse the response (expect JSON, may have markdown code blocks)
            import json
            try:
                # Strip markdown code blocks if present
                if "```" in result:
                    result = result.split("```")[1]
                    if result.startswith("json"):
                        result = result[4:]
                    result = result.strip()

                qualification = json.loads(result)
            except Exception as e:
                print(f"JSON parse error: {e}, result: {result}")
                # If not valid JSON, create a simple response
                qualification = {
                    "budget": "not mentioned",
                    "start_date": "not mentioned",
                    "rental_duration": "not mentioned",
                    "car_model": "not mentioned",
                    "is_confirmation": False,
                    "all_details_present": False,
                    "lead_score": "cold"
                }

            return qualification

        except Exception as e:
            print(f"✗ OpenAI qualification error: {str(e)}")
            raise Exception(f"OpenAI error: {str(e)}")

    def generate_response(self, lead_name: str, lead_message: str, context: str = "", lead_already_sent: bool = False) -> str:
        """Generate a natural, human-like AI response to send back to the lead"""
        try:
            message_lower = lead_message.lower().strip()

            # If they just said a greeting
            greetings = ["hey", "hi", "hello", "yo", "what's up", "sup", "hiya"]
            is_greeting = any(message_lower.startswith(g) for g in greetings) and len(lead_message) < 10

            # If greeting AND already sent to sales, respond naturally, don't ask for budget again
            if is_greeting and lead_already_sent:
                # Just greet them back naturally
                greeting_responses = [
                    "Hey! What's up?",
                    "Hey there!",
                    "Yo! 👋",
                    "What's going on?",
                    "Sup! How can I help?"
                ]
                import random
                return random.choice(greeting_responses)
            elif is_greeting and not lead_already_sent:
                return "Hey! What's your budget for the rental?"

            # If they ask about cars we have, confirm we have it and ask standard questions
            car_inquiry_words = ["what cars", "which cars", "car models", "car options", "vehicles", "do you have", "available cars", "you have"]

            if any(word in message_lower for word in car_inquiry_words):
                # Define car types (not specific brands)
                car_types = ["luxury", "premium", "high-end", "expensive", "sport", "sports", "performance", "fast", "race", "suv", "4x4", "jeep", "offroad", "adventure", "budget", "cheap", "economical", "affordable", "economy", "family", "spacious", "comfort", "7 seater", "seats"]

                # Check if what they're asking for is a CAR TYPE
                is_car_type = any(kw in message_lower for kw in car_types)

                if is_car_type:
                    # It's a car type - respond with type confirmation
                    if any(kw in message_lower for kw in ["luxury", "premium", "high-end", "expensive"]):
                        return "Yes, we have luxury vehicles. What's your budget and when do you need it?"
                    elif any(kw in message_lower for kw in ["sport", "sports", "performance", "fast", "race"]):
                        return "Yes, we have sporty vehicles. What are your dates and budget?"
                    elif any(kw in message_lower for kw in ["suv", "4x4", "jeep", "offroad", "adventure"]):
                        return "Yes, we have SUVs. When do you need it and what's your budget?"
                    elif any(kw in message_lower for kw in ["budget", "cheap", "economical", "affordable", "economy"]):
                        return "Yes, we have budget-friendly options. When do you need the car?"
                    elif any(kw in message_lower for kw in ["family", "spacious", "comfort", "7 seater", "seats"]):
                        return "Yes, we have spacious family vehicles. What dates work for you?"
                else:
                    # Not a known car type - assume it's a SPECIFIC CAR BRAND/MODEL
                    # This catches ALL car brands automatically (BMW, Tesla, Rolls Royce, etc.)
                    return "Yes, we have it! When do you need it?"

            context_note = "They're already connected with our sales team." if lead_already_sent else "We're still collecting their details."

            prompt = f"""You are a professional car rental customer service representative. {context_note} Be courteous, helpful, and professional.

CONVERSATION HISTORY:
{context}

Customer just said: {lead_message}

YOUR TASK:
Answer their question professionally and courteously. Be helpful and concise.

SPECIAL INSTRUCTIONS:
- If they ask "Do you have [car name]?" → Always say "Yes, we have it!"
- If they ask about a car type → Confirm we have that type and ask for dates/budget
- Never refuse a car request - we have options

CRITICAL RULES - NEVER DO THESE:
❌ NEVER say "I see you said...", "I understand...", "Let me help you..."
❌ NEVER recap or parrot back what they said
❌ NEVER ask for booking details if they're already connected with sales team
❌ NEVER be casual or overly informal
❌ NEVER use excessive exclamation marks or slang
❌ NEVER be robotic or repetitive
❌ NEVER say we DON'T have a car
❌ NEVER ask questions you already asked

DO THIS INSTEAD:
✅ Be professional but warm and friendly
✅ Use polite language: "Could you please", "Thank you", "I'd be happy to"
✅ Keep it concise - 1-2 sentences max
✅ If they ask about something you don't know, say "Our sales team will be able to assist with that"
✅ Sound knowledgeable and trustworthy
✅ If already sent to sales, respond professionally to their questions
✅ Always confirm we have what they're asking for

ANSWER NOW:"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=1.2,
                max_tokens=80
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"✗ Response generation error: {str(e)}")
            return "What kind of car you looking for?"

    def extract_all_fields(self, message: str, conversation_history: str = "") -> Dict:
        """
        Extract EVERY field mentioned in the message.
        Returns ONLY fields that were explicitly stated (no inferred/missing fields).
        Used by ResponseGenerator for fine-grained state updates.
        """
        try:
            prompt = f"""You are a car rental conversation analyzer. Extract ONLY fields that the customer explicitly mentioned in their latest message.
DO NOT invent or infer missing fields - only return fields that were directly stated.

CONVERSATION HISTORY:
{conversation_history}

Latest message: "{message}"

Extract only if explicitly mentioned:
1. vehicle_model: Specific brand/model if mentioned (BMW, Tesla, luxury, SUV, etc.) or null
2. vehicle_type: Category if mentioned (economy, luxury, sports, SUV, offroad, etc.) or null
3. rental_start_date: Specific date/timeframe if mentioned (tomorrow, April 28, next week, etc.) or null
4. rental_duration: Duration if mentioned (5 days, 2 weeks, 3 months, 24 hours, etc.) or null
5. budget: Budget if mentioned ($100/day, AED 500, 600, etc.) or null
6. confirmed: true only if they used confirmation words (yes, agree, sure, correct, sounds good, ok, yep) or null/false

EXAMPLES:
- "I want a Tesla" → {"vehicle_model": "Tesla"}
- "Next week for 2 weeks" → {"rental_start_date": "next week", "rental_duration": "2 weeks"}
- "Yeah sounds good" → {"confirmed": true}
- "What's the price?" → {} (no details, just question)

Return ONLY valid JSON with non-null fields."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # More deterministic
                max_tokens=150
            )

            result = response.choices[0].message.content.strip()

            import json
            try:
                # Strip markdown if present
                if "```" in result:
                    result = result.split("```")[1]
                    if result.startswith("json"):
                        result = result[4:]
                    result = result.strip()

                extracted = json.loads(result)
                # Filter out None/null values
                return {k: v for k, v in extracted.items() if v}
            except Exception as e:
                print(f"⚠️ JSON parse error in extract_all_fields: {e}, result: {result}")
                return {}

        except Exception as e:
            print(f"✗ Field extraction error: {str(e)}")
            return {}

openai_service = OpenAIService()
