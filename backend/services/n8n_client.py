import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

N8N_BASE_URL = os.getenv("N8N_BASE_URL", "https://n8n.bgsystems.app.n8n.cloud")
N8N_API_KEY = os.getenv("N8N_API_KEY")

class N8nClient:
    def __init__(self):
        self.base_url = N8N_BASE_URL
        self.api_key = N8N_API_KEY
        self.headers = {
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

    def trigger_workflow(self, workflow_id: str, data: Dict) -> Dict:
        """Trigger a workflow execution"""
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}/execute"
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to trigger n8n workflow: {str(e)}")

    def trigger_workflow_webhook(self, webhook_url: str, data: Dict) -> Dict:
        """Trigger workflow via webhook"""
        try:
            response = requests.post(webhook_url, json=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to trigger webhook: {str(e)}")

n8n_client = N8nClient()
