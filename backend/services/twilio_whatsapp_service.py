import os
import requests
import base64
import json
from typing import Dict

class TwilioWhatsAppService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        self.template_sid = os.getenv("TWILIO_TEMPLATE_SID", "HXc4ed6b2ba4cb723081afc57303e718f4")

        if not all([self.account_sid, self.auth_token, self.twilio_number]):
            raise Exception("Missing Twilio credentials in environment variables")

        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}"
        self.auth = (self.account_sid, self.auth_token)

    def send_template_message(self, phone_number: str, first_name: str) -> Dict:
        """Send WhatsApp template message using Twilio template"""
        try:
            # Format phone number - Twilio expects E.164 format (with + prefix)
            # Convert to string first in case it's an integer
            phone_number = str(phone_number).strip()

            if not phone_number.startswith("+"):
                phone_number = "+" + phone_number.replace(" ", "").replace("-", "")

            print(f"📱 Sending Twilio template to {first_name} ({phone_number})")

            # Use template with variable substitution
            data = {
                "From": f"whatsapp:{self.twilio_number}",
                "To": f"whatsapp:{phone_number}",
                "ContentSid": self.template_sid,
                "ContentVariables": json.dumps({"name": first_name})
            }

            response = requests.post(
                f"{self.base_url}/Messages.json",
                data=data,
                auth=self.auth
            )

            response.raise_for_status()
            result = response.json()
            message_sid = result.get("sid", "")

            print(f"✅ Template message sent to {first_name}. SID: {message_sid}")
            return {"status": "sent", "sid": message_sid}

        except Exception as e:
            print(f"❌ Failed to send template message: {str(e)}")
            raise Exception(f"Twilio WhatsApp error: {str(e)}")

    def send_text_message(self, phone_number: str, message_text: str) -> Dict:
        """Send plain text WhatsApp message"""
        try:
            # Format phone number
            # Convert to string first in case it's an integer
            phone_number = str(phone_number).strip()

            if not phone_number.startswith("+"):
                phone_number = "+" + phone_number.replace(" ", "").replace("-", "")

            print(f"Sending WhatsApp text to {phone_number}")

            data = {
                "From": f"whatsapp:{self.twilio_number}",
                "To": f"whatsapp:{phone_number}",
                "Body": message_text
            }

            response = requests.post(
                f"{self.base_url}/Messages.json",
                data=data,
                auth=self.auth
            )

            response.raise_for_status()
            result = response.json()
            message_sid = result.get("sid", "")

            print(f"✓ Text message sent. SID: {message_sid}")
            return {"status": "sent", "sid": message_sid}

        except Exception as e:
            print(f"✗ Failed to send text message: {str(e)}")
            raise Exception(f"Twilio WhatsApp error: {str(e)}")

twilio_whatsapp_service = TwilioWhatsAppService()
