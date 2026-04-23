import os
import requests
from typing import Dict

class MetaWhatsAppService:
    def __init__(self):
        self.phone_id = os.getenv("META_PHONE_ID", "").strip()
        # Remove all whitespace (spaces, newlines, tabs) from access token
        self.access_token = "".join(os.getenv("META_ACCESS_TOKEN", "").split())
        self.template_name = "lead_inquiry"
        self.language = "en"

        if not all([self.phone_id, self.access_token]):
            raise Exception("Missing Meta Cloud API credentials (META_PHONE_ID or META_ACCESS_TOKEN)")

        self.base_url = f"https://graph.instagram.com/v18.0/{self.phone_id}/messages"

    def send_template_message(self, phone_number: str, first_name: str) -> Dict:
        """Send WhatsApp template message using Meta Cloud API"""
        try:
            # Format phone number - Meta expects just digits, optionally with +
            if phone_number.startswith("+"):
                phone_number = phone_number[1:]  # Remove + prefix
            phone_number = phone_number.replace(" ", "").replace("-", "")

            print(f"📱 Sending Meta template 'lead_inquiry' to {first_name} ({phone_number})")

            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone_number,
                "type": "template",
                "template": {
                    "name": self.template_name,
                    "language": {
                        "code": self.language
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": first_name
                                }
                            ]
                        }
                    ]
                }
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()

            message_id = result.get("messages", [{}])[0].get("id", "")
            print(f"✅ Template message sent to {first_name}. Message ID: {message_id}")
            return {"status": "sent", "message_id": message_id}

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e.response, 'text'):
                error_msg = e.response.text
            print(f"❌ Failed to send template message: {error_msg}")
            raise Exception(f"Meta WhatsApp error: {error_msg}")
        except Exception as e:
            print(f"❌ Failed to send template message: {str(e)}")
            raise Exception(f"Meta WhatsApp error: {str(e)}")

try:
    meta_whatsapp_service = MetaWhatsAppService()
    print("✅ Meta WhatsApp service initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Meta service: {str(e)}")
    meta_whatsapp_service = None
