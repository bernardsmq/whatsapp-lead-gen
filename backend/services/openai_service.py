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
            prompt = f"""You are a real estate lead qualification expert.
A lead named {lead_name} has sent this message: "{message}"

Analyze this message and determine:
1. Lead score: hot, warm, or cold (hot = interested + ready to act, warm = interested but unsure, cold = not interested)
2. Key indicators found in the message
3. Recommended next action

Return as JSON with fields: score, indicators (array), next_action (string)"""

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
            prompt = f"""You are a helpful real estate agent responding to a lead.
Lead name: {lead_name}
Their message: "{lead_message}"
Context: {context}

Write a friendly, professional response that:
1. Acknowledges their message
2. Asks a qualifying question
3. Keeps it to 2-3 sentences max

Keep it natural and conversational, not robotic."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"✗ Response generation error: {str(e)}")
            return "Thanks for your message! How can I help you with your real estate needs?"

openai_service = OpenAIService()
