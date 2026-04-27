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

IMPORTANT: If the latest message mentions a DIFFERENT car than previous messages, treat it as a FRESH INQUIRY. Only use dates/duration from the latest message for this new car. Do NOT carry over old booking details.

EXTRACT these details from the LATEST message:
1. car_type - What car is mentioned? Examples: "M5 F90", "Lamborghini Aventador", "Mclaren 520S"
2. duration - How long? Look for: "2 days", "1 week", "for X days/weeks/months", "short-term", "long-term". Return "not mentioned" only if truly not stated.
3. dates - When? Look for: "tomorrow", "next week", "12:00", "starting", "from", "27 April", specific times/dates. Return "not mentioned" only if truly not stated.
4. is_confirmation - Is latest message confirming? ("yes", "agree", "sure", "correct", "sounds good", etc)
5. all_details_present - Are ALL THREE (car_type, duration, dates) explicitly mentioned in the LATEST message?
6. lead_score - hot/warm/cold based on urgency and completion of details

Examples:
- "for 2 days starting tomorrow at 12:00" → duration="2 days", dates="tomorrow at 12:00"
- "tomorrow afternoon" → dates="tomorrow afternoon" (time mentioned)
- "I'll be in town next week" → dates="next week"

RETURN: Valid JSON with exactly these fields: car_type, duration, dates, is_confirmation, all_details_present, lead_score"""

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
                    "car_type": "not specified",
                    "duration": "not specified",
                    "dates": "not specified",
                    "is_confirmation": False,
                    "all_details_present": False,
                    "lead_score": "cold"
                }

            return qualification

        except Exception as e:
            print(f"✗ OpenAI qualification error: {str(e)}")
            raise Exception(f"OpenAI error: {str(e)}")

    def generate_response(self, lead_name: str, lead_message: str, context: str = "") -> str:
        """Generate a natural, human-like AI response to send back to the lead"""
        try:
            # If they just said a greeting, respond with greeting + ask questions
            greetings = ["hey", "hi", "hello", "yo", "what's up", "sup", "hiya"]
            message_lower = lead_message.lower().strip()

            if any(message_lower.startswith(g) for g in greetings) and len(lead_message) < 10:
                return "Hey! What kind of car you looking for?"

            # If they ask about cars we have, ask what TYPE
            car_inquiry_words = ["what cars", "which cars", "car models", "car options", "vehicles", "do you have", "available cars"]
            if any(word in message_lower for word in car_inquiry_words):
                return "We have everything - offroading, sports, daily, luxury. What type interests you?"

            prompt = f"""You are a car rental agent texting with a customer. Be direct and natural.

CONVERSATION:
{context}

Customer: {lead_message}

RULES:
- Answer their question naturally - don't ask for confirmation or booking details
- Keep it 1 short sentence max
- Sound casual like texting a friend
- NEVER say "I see you said", "Could you let me know", or recap what they said
- If sales/pricing/booking questions, say "Our sales team will take care of that" or similar
- Just have a normal conversation, be human

RESPONSE:"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=1.0,
                max_tokens=60
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"✗ Response generation error: {str(e)}")
            return "What kind of car you looking for?"

openai_service = OpenAIService()
