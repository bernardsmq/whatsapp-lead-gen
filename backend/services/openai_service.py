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
        """Generate an AI response to send back to the lead"""
        try:
            prompt = f"""You are a sharp car rental agent responding to a customer. Remember the ENTIRE conversation history.

CONVERSATION HISTORY:
{context}

Customer's latest message: "{lead_message}"

Rules:
1. Acknowledge SPECIFICALLY what they just said (car model, dates, duration if mentioned)
2. DO NOT ask about things they already told you - check the history first
3. Only ask for MISSING information
4. Be short and direct - 2 sentences MAX
5. No signatures, no formal greetings/closings, no "I'm here to help" fluff
6. Keep it conversational like texting, not like an email

Just write the response text, nothing else."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"✗ Response generation error: {str(e)}")
            return "Thanks for your interest! What type of car do you need, and when would you like it for?"

openai_service = OpenAIService()
