-- Migration: Add conversation_state table for intelligent chat tracking
-- Date: 2026-05-04
-- Purpose: Track conversation state per lead, avoid repeated questions, normalize field values

CREATE TABLE conversation_state (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID UNIQUE NOT NULL REFERENCES leads(id) ON DELETE CASCADE,

  -- Extracted rental fields
  vehicle_type TEXT,              -- "economy", "luxury", "sports", "suv", "offroad"
  vehicle_model TEXT,             -- Specific: "BMW X5", "Tesla Model Y", "Geely Emgrand"
  rental_start_date TEXT,         -- "April 28", "next week", "tomorrow"
  rental_duration TEXT,           -- "5 days", "2 weeks", "1 month"
  budget TEXT,                    -- "$100/day", "AED 500", "600"

  -- Tracking what's been asked
  asked_fields JSONB DEFAULT '{}'::jsonb,  -- {"vehicle_type": 2, "budget": 1, "rental_start_date": 0}
  last_asked_field TEXT,                    -- Which field was asked most recently
  last_asked_at TIMESTAMP,                  -- When it was asked

  -- Normalized/parsed values for reliable comparison
  budget_numeric DECIMAL,                   -- 100.00 (extracted number only)
  budget_period TEXT,                       -- "day", "week", "month"

  -- Confirmation tracking
  user_confirmed BOOLEAN DEFAULT FALSE,     -- Has user said "yes", "agree", etc?
  confirmed_at TIMESTAMP,                   -- When user confirmed

  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient queries
CREATE INDEX idx_conversation_state_lead_id ON conversation_state(lead_id);
CREATE INDEX idx_conversation_state_updated_at ON conversation_state(updated_at DESC);

-- Add comments to document the schema
COMMENT ON TABLE conversation_state IS 'Tracks conversation state per lead to avoid repeated questions and manage context';
COMMENT ON COLUMN conversation_state.asked_fields IS 'JSON object tracking how many times each field has been asked: {"vehicle_type": 2, "budget": 1}';
COMMENT ON COLUMN conversation_state.budget_numeric IS 'Extracted numeric budget value for reliable comparisons (e.g., 100 from "100/day" or "$100")';
COMMENT ON COLUMN conversation_state.budget_period IS 'Budget period unit: day, week, month';
COMMENT ON COLUMN conversation_state.user_confirmed IS 'True only after user explicitly confirms details with words like yes, agree, sure, etc.';
