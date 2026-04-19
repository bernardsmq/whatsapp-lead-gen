import os
import requests
import json
from typing import Dict

class WhatsAppService:
    def __init__(self):
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "2001798287045224")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.base_url = "https://graph.instagram.com/v18.0"
        self.api_url = f"{self.base_url}/{self.phone_number_id}/messages"

    def send_template_message(self, phone_number: str, first_name: str) -> Dict:
        """Send WhatsApp template message to lead"""
        try:
            if not self.access_token:
                raise Exception("WHATSAPP_ACCESS_TOKEN not configured")

            # Remove + and spaces from phone number
            clean_phone = phone_number.replace("+", "").replace(" ", "")

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_phone,
                "type": "template",
                "template": {
                    "name": "hello_world",  # Default WhatsApp template
                    "language": {
                        "code": "en_US"
                    }
                }
            }

            print(f"Sending WhatsApp template to {clean_phone}")
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            print(f"✓ Message sent to {first_name}")
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to send WhatsApp message: {str(e)}")
            raise Exception(f"WhatsApp API error: {str(e)}")

    def send_text_message(self, phone_number: str, message: str) -> Dict:
        """Send plain text WhatsApp message"""
        try:
            if not self.access_token:
                raise Exception("WHATSAPP_ACCESS_TOKEN not configured")

            clean_phone = phone_number.replace("+", "").replace(" ", "")

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": clean_phone,
                "type": "text",
                "text": {
                    "body": message
                }
            }

            print(f"Sending text message to {clean_phone}")
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to send text message: {str(e)}")
            raise Exception(f"WhatsApp API error: {str(e)}")

whatsapp_service = WhatsAppService()
