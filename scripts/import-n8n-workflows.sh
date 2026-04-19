#!/bin/bash

# n8n Workflow Import Script
# Usage: bash scripts/import-n8n-workflows.sh

set -e

N8N_BASE_URL="https://bgsystems.app.n8n.cloud"
WORKFLOWS_DIR="./n8n_workflows"

echo "🚀 Starting n8n Workflow Import..."
echo "Base URL: $N8N_BASE_URL"
echo ""

# Array of workflows to import
workflows=(
  "workflow-1-trigger-send-leads.json"
  "workflow-2-send-whatsapp-template.json"
  "workflow-3-listen-whatsapp-replies.json"
  "workflow-4-ai-qualify-lead.json"
  "workflow-5-handoff-sales.json"
  "workflow-6-send-ai-message.json"
)

for workflow in "${workflows[@]}"; do
  workflow_path="$WORKFLOWS_DIR/$workflow"

  if [ ! -f "$workflow_path" ]; then
    echo "❌ File not found: $workflow_path"
    exit 1
  fi

  echo "📥 Importing: $workflow"

  # Read the workflow JSON
  workflow_json=$(cat "$workflow_path")

  # Extract workflow name
  workflow_name=$(echo "$workflow_json" | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)

  echo "  Name: $workflow_name"
  echo "  ✅ Ready to import (import manually via n8n UI)"
  echo ""
done

echo "✅ All workflows ready for import!"
echo ""
echo "📋 Next steps:"
echo "1. Go to: $N8N_BASE_URL"
echo "2. Click 'Home' → 'Import'"
echo "3. Select each workflow JSON file"
echo "4. Configure credentials (Supabase, OpenAI, WhatsApp)"
echo "5. Deploy each workflow"
echo ""
echo "Or use the n8n API to import programmatically (requires API key)"
