import os
import requests
import base64
from typing import Dict

class TwilioWhatsAppService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

        if not all([self.account_sid, self.auth_token, self.twilio_number]):
            raise Exception("Missing Twilio credentials in environment variables")

        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}"
        self.auth = (self.account_sid, self.auth_token)

    def send_template_message(self, phone_number: str, first_name: str) -> Dict:
        """Send WhatsApp template message to lead"""
        try:
            # Format phone number - Twilio expects E.164 format (with + prefix)
            if not phone_number.startswith("+"):
                phone_number = "+" + phone_number.replace(" ", "").replace("-", "")

            print(f"Sending WhatsApp template to {first_name} ({phone_number})")

            data = {
                "From": f"whatsapp:{self.twilio_number}",
                "To": f"whatsapp:{phone_number}",
                "Body": f"Hi {first_name}! Looking to rent a car? Short term or long term?"
            }

            response = requests.post(
                f"{self.base_url}/Messages.json",
                data=data,
                auth=self.auth
            )

            response.raise_for_status()
            result = response.json()
            message_sid = result.get("sid", "")

            print(f"✓ Message sent to {first_name}. SID: {message_sid}")
            return {"status": "sent", "sid": message_sid}

        except Exception as e:
            print(f"✗ Failed to send WhatsApp message: {str(e)}")
            raise Exception(f"Twilio WhatsApp error: {str(e)}")

    def send_text_message(self, phone_number: str, message_text: str) -> Dict:
        """Send plain text WhatsApp message"""
        try:
            # Format phone number
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
