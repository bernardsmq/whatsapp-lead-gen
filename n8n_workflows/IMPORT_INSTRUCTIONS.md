# n8n Workflows Import Instructions

## Quick Setup

### Step 1: Create Credentials in n8n Cloud
1. Go to your n8n account → Credentials
2. Click "New Credential"

**Create Supabase Credential:**
- Type: Supabase
- Name: "Supabase"
- Project URL: `https://rtaeoiwivovjovuimdue.supabase.co`
- API Key: Get from Supabase → Settings → API (use anon/public key)

**Create OpenAI Credential:**
- Type: OpenAI
- Name: "OpenAI"
- API Key: `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`

**Create HTTP Auth Credential:**
- Type: Generic Credential (HTTP Header Auth)
- Name: "WhatsApp API"
- Authentication: Leave as Generic
- (The bearer token is embedded in workflow JSONs)

### Step 2: Set Environment Variables in n8n Cloud
1. Go to Settings → Environment Variables
2. Add these variables:
   - `PHONE_NUMBER_ID`: `2001798287045224`
   - `SUPABASE_URL`: `https://rtaeoiwivovjovuimdue.supabase.co`
   - `OPENAI_API_KEY`: `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`
   - `WHATSAPP_SALES_GUY_NUMBER`: `+37124811178`
   - `BACKEND_URL`: `http://localhost:8000` (update after deploying to Railway)

### Step 3: Import Workflows
1. In n8n, go to Projects → Your Project → Import from file
2. Select the workflow JSON file and import
3. Repeat for all 6 workflow files

**Workflows to import (in order):**
1. `workflow-1-trigger-send-leads.json`
2. `workflow-2-send-whatsapp-template.json`
3. `workflow-3-listen-whatsapp-replies.json`
4. `workflow-4-ai-qualify-lead.json`
5. `workflow-5-handoff-sales.json`
6. `workflow-6-send-ai-message.json`

### Step 4: Configure Webhooks
After importing, for each workflow:
1. Click on the Webhook node
2. Copy the **Production URL** (not test URL)
3. Configure WhatsApp webhook in Meta Business Manager:
   - For Workflow 3 (replies): Set as incoming messages webhook
   - Verify token: `your-verify-token` (create one yourself)

## Workflow Overview

| # | Name | Trigger | Purpose |
|---|------|---------|---------|
| 1 | Send Template | Webhook POST | Send initial WhatsApp template to leads |
| 2 | Listen Replies | WhatsApp Webhook | Receive incoming messages |
| 3 | AI Qualify | Called from #2 | Use GPT-4o mini to qualify lead |
| 4 | Send AI Message | Called from #3 | Send AI response back to lead |
| 5 | Handoff Sales | Called from #3 | Send qualified lead to sales guy |
| 6 | Process Sheet | FastAPI trigger | Insert bulk leads from CSV/Excel |

## Critical Configuration

- **Phone Number ID**: `2001798287045224`
- **WhatsApp API Endpoint**: `https://graph.instagram.com/v18.0/{{PHONE_NUMBER_ID}}/messages`
- **Sales Guy Number**: `+37124811178` (hardcoded in workflows, update in Workflow 5)
