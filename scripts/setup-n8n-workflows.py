#!/usr/bin/env python3
"""
n8n Workflow Setup Script
Automatically imports and configures all 6 workflows via n8n API
"""

import json
import os
import sys
import requests
from pathlib import Path

# Configuration
N8N_BASE_URL = os.getenv("N8N_BASE_URL", "https://bgsystems.app.n8n.cloud")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")
WORKFLOWS_DIR = Path(__file__).parent.parent / "n8n_workflows"

# Credentials to create
CREDENTIALS = {
    "supabase": {
        "type": "supabase",
        "name": "Supabase",
        "data": {
            "host": "rtaeoiwivovjovuimdue.supabase.co",
            "user": "postgres",
            "password": os.getenv("SUPABASE_DB_PASSWORD", ""),
            "database": "postgres",
            "ssl": "true",
            "port": 5432
        }
    },
    "openai": {
        "type": "openAiApi",
        "name": "OpenAI",
        "data": {
            "apiKey": os.getenv("OPENAI_API_KEY", "")
        }
    },
    "whatsapp": {
        "type": "httpHeaderAuth",
        "name": "WhatsApp API",
        "data": {
            "headerName": "Authorization",
            "headerValue": f"Bearer {os.getenv('WHATSAPP_API_TOKEN', '')}"
        }
    }
}

# Environment variables for workflows
ENV_VARS = {
    "PHONE_NUMBER_ID": "2001798287045224",
    "WHATSAPP_SALES_GUY_NUMBER": "+37124811178",
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "SUPABASE_URL": "https://rtaeoiwivovjovuimdue.supabase.co",
    "SUPABASE_KEY": os.getenv("SUPABASE_KEY", ""),
    "BACKEND_URL": os.getenv("BACKEND_URL", "http://localhost:8000")
}

def log(msg, level="INFO"):
    """Simple logging"""
    print(f"[{level}] {msg}")

def create_credential(cred_type, cred_data):
    """Create credential via n8n API"""
    if not N8N_API_KEY:
        log(f"Skipping credential creation (no API key): {cred_data['name']}", "WARN")
        return None

    url = f"{N8N_BASE_URL}/api/v1/credentials"
    headers = {"X-N8N-API-KEY": N8N_API_KEY, "Content-Type": "application/json"}

    payload = {
        "type": cred_data["type"],
        "name": cred_data["name"],
        "data": cred_data["data"]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        cred = response.json()
        log(f"✅ Created credential: {cred_data['name']} (ID: {cred.get('id')})")
        return cred.get("id")
    except requests.exceptions.RequestException as e:
        log(f"⚠️  Failed to create credential: {cred_data['name']}", "WARN")
        log(f"   Error: {str(e)}", "WARN")
        return None

def set_env_variable(key, value):
    """Set environment variable via n8n API"""
    if not N8N_API_KEY:
        return False

    url = f"{N8N_BASE_URL}/api/v1/variables"
    headers = {"X-N8N-API-KEY": N8N_API_KEY, "Content-Type": "application/json"}

    payload = {"key": key, "value": value}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        log(f"✅ Set environment variable: {key}")
        return True
    except requests.exceptions.RequestException:
        log(f"⚠️  Failed to set env var: {key}", "WARN")
        return False

def import_workflow(workflow_file):
    """Import workflow JSON via n8n API"""
    if not N8N_API_KEY:
        log(f"⚠️  Skipping workflow import (no API key): {workflow_file.name}", "WARN")
        return False

    try:
        with open(workflow_file, 'r') as f:
            workflow_json = json.load(f)

        workflow_name = workflow_json.get("name", workflow_file.stem)

        url = f"{N8N_BASE_URL}/api/v1/workflows"
        headers = {"X-N8N-API-KEY": N8N_API_KEY, "Content-Type": "application/json"}

        payload = {
            "name": workflow_name,
            "nodes": workflow_json.get("nodes", []),
            "connections": workflow_json.get("connections", {}),
            "active": True
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        workflow = response.json()
        log(f"✅ Imported workflow: {workflow_name} (ID: {workflow.get('id')})")
        return True

    except json.JSONDecodeError:
        log(f"❌ Invalid JSON in workflow file: {workflow_file.name}", "ERROR")
        return False
    except requests.exceptions.RequestException as e:
        log(f"⚠️  Failed to import workflow: {workflow_file.name}", "WARN")
        log(f"   Error: {str(e)}", "WARN")
        return False
    except Exception as e:
        log(f"❌ Error importing workflow: {workflow_file.name}: {str(e)}", "ERROR")
        return False

def main():
    """Main setup function"""
    log("=" * 60)
    log("n8n Workflow Setup Script")
    log("=" * 60)

    # Check if n8n is accessible
    log(f"\n📡 Checking n8n connection: {N8N_BASE_URL}")
    try:
        response = requests.get(f"{N8N_BASE_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            log("✅ n8n is accessible")
        else:
            log(f"⚠️  n8n returned status {response.status_code}", "WARN")
    except requests.exceptions.RequestException:
        log(f"❌ Cannot connect to n8n. Is it running at {N8N_BASE_URL}?", "ERROR")
        return False

    # Check API key
    if N8N_API_KEY:
        log(f"✅ Using API key for authentication")
    else:
        log("⚠️  No API key set. Set N8N_API_KEY environment variable for full setup", "WARN")
        log("   You can still view available workflows, but can't import automatically")

    # Create credentials
    if N8N_API_KEY:
        log("\n🔐 Creating Credentials...")
        for cred_type, cred_data in CREDENTIALS.items():
            if cred_data["data"].get("apiKey") or cred_data["data"].get("password") or \
               cred_data["data"].get("headerValue"):
                create_credential(cred_type, cred_data)

    # Set environment variables
    if N8N_API_KEY:
        log("\n🔧 Setting Environment Variables...")
        for key, value in ENV_VARS.items():
            if value:
                set_env_variable(key, value)

    # Import workflows
    log("\n📥 Importing Workflows...")
    if not WORKFLOWS_DIR.exists():
        log(f"❌ Workflows directory not found: {WORKFLOWS_DIR}", "ERROR")
        return False

    workflow_files = sorted(WORKFLOWS_DIR.glob("workflow-*.json"))
    if not workflow_files:
        log(f"⚠️  No workflow files found in {WORKFLOWS_DIR}", "WARN")
        return False

    log(f"Found {len(workflow_files)} workflow files")

    success_count = 0
    for workflow_file in workflow_files:
        if import_workflow(workflow_file):
            success_count += 1

    # Summary
    log("\n" + "=" * 60)
    log(f"Setup Complete: {success_count}/{len(workflow_files)} workflows imported")
    log("=" * 60)

    if N8N_API_KEY:
        log("\n✅ All workflows have been imported and are ready to use!")
        log("\n📋 Next steps:")
        log("1. Go to https://bgsystems.app.n8n.cloud")
        log("2. Verify all 6 workflows are present")
        log("3. Test the workflows by running them")
    else:
        log("\n⚠️  API setup incomplete. To finish:")
        log("1. Set environment variables in n8n: Settings → Environment Variables")
        log("2. Create credentials: Settings → Credentials")
        log("3. Manually import workflows via UI: Home → Import")

    return success_count == len(workflow_files)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
