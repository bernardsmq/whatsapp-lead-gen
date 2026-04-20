import os
from openai import OpenAI
from typing import Dict

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OPENAI_API_KEY not configured")
        self.client = OpenAI(api_key=api_key)

    def qualify_lead(self, lead_name: str, message: str) -> Dict:
        """Use GPT to qualify a lead based on their message response"""
        try:
            prompt = f"""You are a car rental lead qualification expert.
A potential customer named {lead_name} has sent this message: "{message}"

Analyze this message and determine:
1. Lead score: hot, warm, or cold (hot = ready to book now, warm = interested but needs info, cold = not interested)
2. Key indicators: rental duration (short/long term), car type preference, urgency level
3. Recommended next action

Return ONLY valid JSON with fields: score, indicators (array), next_action (string)"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )

            result = response.choices[0].message.content
            print(f"GPT Response: {result}")

            # Parse the response (expect JSON)
            import json
            try:
                qualification = json.loads(result)
            except:
                # If not valid JSON, create a simple response
                qualification = {
                    "score": "warm",
                    "indicators": [message[:50]],
                    "next_action": "Follow up with more information"
                }

            return qualification

        except Exception as e:
            print(f"✗ OpenAI qualification error: {str(e)}")
            raise Exception(f"OpenAI error: {str(e)}")

    def generate_response(self, lead_name: str, lead_message: str, context: str = "") -> str:
        """Generate an AI response to send back to the lead"""
        try:
            prompt = f"""You are a sharp car rental agent. Respond naturally to this customer message.

Customer: "{lead_message}"

Rules:
1. Acknowledge SPECIFICALLY what they said (if they mentioned a car model, dates, duration - confirm it sounds good)
2. Only ask for MISSING information
3. Be short and direct - 2 sentences MAX
4. No signatures, no formal greetings/closings, no "I'm here to help" fluff
5. Keep it conversational like texting, not like an email

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
