import os
import re
import requests
import base64
import json
from typing import Dict

class TwilioWhatsAppService:
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        self.template_sid = os.getenv("TWILIO_TEMPLATE_SID", "HX005dfce9d30f0aa83cc1b781c3ac20bf")
        self.status_callback_url = os.getenv("TWILIO_STATUS_CALLBACK_URL")

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

            # Remove all non-digit characters (spaces, dashes, plus signs, hidden Unicode)
            # Keep only digits
            digits_only = re.sub(r'\D', '', phone_number)

            # Add + prefix
            phone_number = "+" + digits_only

            print(f"📱 Sending Twilio template to {first_name} ({phone_number})")

            # Use template with variable substitution
            data = {
                "From": f"whatsapp:{self.twilio_number}",
                "To": f"whatsapp:{phone_number}",
                "ContentSid": self.template_sid,
                "ContentVariables": json.dumps({"name": first_name})
            }

            # Add status callback URL only if it's properly configured
            if self.status_callback_url and self.status_callback_url.startswith(('http://', 'https://')):
                data["StatusCallback"] = self.status_callback_url
                print(f"  Status callback enabled: {self.status_callback_url}")
            elif self.status_callback_url:
                print(f"  ⚠️ Warning: TWILIO_STATUS_CALLBACK_URL is set but not a valid URL, skipping...")

            print(f"  Sending Twilio request with data: {data}")
            response = requests.post(
                f"{self.base_url}/Messages.json",
                data=data,
                auth=self.auth
            )

            response.raise_for_status()
            result = response.json()
            message_sid = result.get("sid", "")

            print(f"✅ Template message sent to {first_name}. SID: {message_sid}")
            return {
                "status": "sent",
                "sid": message_sid,
                "template_sid": self.template_sid,
                "template_variables": {"name": first_name}
            }

        except Exception as e:
            print(f"❌ Failed to send template message: {str(e)}")
            # Try to get more details from response
            try:
                if 'response' in locals() and hasattr(response, 'text'):
                    error_detail = response.text
                    print(f"  Twilio error response: {error_detail}")
            except:
                pass
            raise Exception(f"Twilio WhatsApp error: {str(e)}")

    def send_text_message(self, phone_number: str, message_text: str) -> Dict:
        """Send plain text WhatsApp message"""
        try:
            # Format phone number - remove all non-digit characters and hidden Unicode
            phone_number = str(phone_number).strip()

            # Remove all non-digit characters (spaces, dashes, plus signs, hidden Unicode)
            # Keep only digits
            digits_only = re.sub(r'\D', '', phone_number)

            # Add + prefix
            phone_number = "+" + digits_only

            print(f"Sending WhatsApp text to {phone_number}")

            data = {
                "From": f"whatsapp:{self.twilio_number}",
                "To": f"whatsapp:{phone_number}",
                "Body": message_text
            }

            # Add status callback URL only if it's properly configured
            if self.status_callback_url and self.status_callback_url.startswith(('http://', 'https://')):
                data["StatusCallback"] = self.status_callback_url
            elif self.status_callback_url:
                print(f"  ⚠️ Warning: TWILIO_STATUS_CALLBACK_URL is set but not a valid URL, skipping...")

            print(f"  Sending Twilio request with data: {data}")
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
            # Try to get more details from response
            try:
                if 'response' in locals() and hasattr(response, 'text'):
                    error_detail = response.text
                    print(f"  Twilio error response: {error_detail}")
            except:
                pass
            raise Exception(f"Twilio WhatsApp error: {str(e)}")

twilio_whatsapp_service = TwilioWhatsAppService()
