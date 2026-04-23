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
            prompt = f"""You are a car rental lead qualification expert. Analyze the FULL conversation.

FULL CONVERSATION:
{conversation_history}

Latest message: "{message}"

EXTRACT these details from the ENTIRE conversation (not just latest message):
1. car_type - What specific car or car type was mentioned? (search entire history) Examples: "Lamborghini Huracan", "SUV", "economy car"
2. duration - How long is the rental? (search entire history) Examples: "2 months", "long term", "1 week"
3. dates - Any specific dates mentioned? (search entire history) Examples: "June 1-15", "today", "not mentioned"
4. is_confirmation - Is the latest message confirming something? (check if it's "yes", "agree", "sure", "ofc", etc AND there was a confirmation question before it)
5. all_details_present - Are car_type, duration, AND dates ALL found in the conversation? (true only if ALL three are present)
6. lead_score - hot/warm/cold based on readiness to book

RETURN: Valid JSON only with fields: car_type, duration, dates, is_confirmation, all_details_present, lead_score"""

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

            # Check what info is already in conversation
            context_lower = context.lower()
            has_car_type = any(car in context_lower for car in ["bmw", "audi", "mercedes", "tesla", "suv", "sedan", "coupe", "hatchback", "truck", "van", "economy", "luxury", "sports", "g series", "series"])
            has_dates = any(month in context_lower for month in ["april", "may", "june", "july", "august", "september", "october", "november", "december", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]) or any(word in context_lower for word in ["today", "tomorrow", "week", "weeks", "month", "months", "day", "days"])
            has_duration = any(word in context_lower for word in ["week", "weeks", "month", "months", "day", "days", "for"])

            prompt = f"""You are a car rental agent texting with a customer. Be direct and natural.

CONVERSATION:
{context}

Customer: {lead_message}

WHAT WE ALREADY KNOW:
- Car type mentioned: {has_car_type}
- Dates/timeframe mentioned: {has_dates}
- Duration mentioned: {has_duration}

DO THIS:
- Only ask for info we DON'T have yet
- If they gave dates AND duration, DON'T ask "short-term or long-term" - that's already determined
- Skip any acknowledgment or recap
- Keep it 1 short sentence
- Sound casual like texting a friend

DON'T DO THIS:
- "I see you said..." (NEVER)
- "Could you let me know..." (too formal)
- Recap or acknowledge what they said

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
            return "What kind of car you need?"

openai_service = OpenAIService()
