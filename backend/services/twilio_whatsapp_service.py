import os
from typing import Dict
from twilio.rest import Client

class TwilioWhatsAppService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

        if not all([self.account_sid, self.auth_token, self.twilio_number]):
            raise Exception("Missing Twilio credentials in environment variables")

        self.client = Client(self.account_sid, self.auth_token)

    def send_template_message(self, phone_number: str, first_name: str) -> Dict:
        """Send WhatsApp template message to lead"""
        try:
            # Format phone number - Twilio expects E.164 format (with + prefix)
            if not phone_number.startswith("+"):
                phone_number = "+" + phone_number.replace(" ", "").replace("-", "")

            print(f"Sending WhatsApp template to {first_name} ({phone_number})")

            message = self.client.messages.create(
                from_=f"whatsapp:{self.twilio_number}",
                to=f"whatsapp:{phone_number}",
                body=f"Hi {first_name}! 👋 We found properties that match your interests. Reply YES if you'd like to learn more!"
            )

            print(f"✓ Message sent to {first_name}. SID: {message.sid}")
            return {"status": "sent", "sid": message.sid}

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

            message = self.client.messages.create(
                from_=f"whatsapp:{self.twilio_number}",
                to=f"whatsapp:{phone_number}",
                body=message_text
            )

            print(f"✓ Text message sent. SID: {message.sid}")
            return {"status": "sent", "sid": message.sid}

        except Exception as e:
            print(f"✗ Failed to send text message: {str(e)}")
            raise Exception(f"Twilio WhatsApp error: {str(e)}")

twilio_whatsapp_service = TwilioWhatsAppService()
