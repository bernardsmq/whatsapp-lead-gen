-- Migration: Add message status tracking and template information to conversations table
-- Date: 2026-05-04

-- Add new columns to conversations table for message status tracking
ALTER TABLE conversations
ADD COLUMN IF NOT EXISTS message_sid TEXT UNIQUE,
ADD COLUMN IF NOT EXISTS delivery_status TEXT DEFAULT 'sent' CHECK (delivery_status IN ('pending', 'sent', 'delivered', 'read', 'failed')),
ADD COLUMN IF NOT EXISTS delivery_timestamp TIMESTAMP,
ADD COLUMN IF NOT EXISTS template_sid TEXT,
ADD COLUMN IF NOT EXISTS template_variables JSONB;

-- Update message_type constraint to include 'template' type
-- Note: This requires dropping and recreating the constraint
ALTER TABLE conversations DROP CONSTRAINT IF EXISTS conversations_message_type_check;
ALTER TABLE conversations ADD CONSTRAINT conversations_message_type_check CHECK (message_type IN ('incoming', 'outgoing', 'template'));

-- Update sender constraint to include 'template' type
ALTER TABLE conversations DROP CONSTRAINT IF EXISTS conversations_sender_check;
ALTER TABLE conversations ADD CONSTRAINT conversations_sender_check CHECK (sender IN ('user', 'ai', 'system', 'template'));

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS conversations_message_sid_idx ON conversations(message_sid);
CREATE INDEX IF NOT EXISTS conversations_delivery_status_idx ON conversations(delivery_status);
CREATE INDEX IF NOT EXISTS conversations_lead_id_created_at_idx ON conversations(lead_id, created_at);
CREATE INDEX IF NOT EXISTS conversations_template_sid_idx ON conversations(template_sid);

-- Add comment to document the schema changes
COMMENT ON COLUMN conversations.message_sid IS 'Twilio MessageSid for tracking delivery status via webhooks';
COMMENT ON COLUMN conversations.delivery_status IS 'Message delivery status: pending, sent, delivered, read, or failed';
COMMENT ON COLUMN conversations.delivery_timestamp IS 'Timestamp when delivery status was last updated';
COMMENT ON COLUMN conversations.template_sid IS 'Twilio ContentSid of the template used (for bulk sends)';
COMMENT ON COLUMN conversations.template_variables IS 'JSON data containing template variable values (e.g., {name: "John"})';
