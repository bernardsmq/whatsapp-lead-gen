-- Migration: Update leads status constraint to include new status values
-- Date: 2026-05-04

-- Drop old constraint and add new one with additional status values
ALTER TABLE leads DROP CONSTRAINT IF EXISTS leads_status_check;
ALTER TABLE leads ADD CONSTRAINT leads_status_check CHECK (
  status IN ('pending', 'active', 'qualified', 'handed_off', 'sent_to_sales', 'do_not_contact', 'new_inquiry')
);

-- Add sent_to_sales_at column for timestamp tracking
ALTER TABLE leads ADD COLUMN IF NOT EXISTS sent_to_sales_at TIMESTAMP;

COMMENT ON COLUMN leads.status IS 'Lead status: pending (new), active (in progress), qualified (ready), handed_off (legacy), sent_to_sales (forwarded to sales), do_not_contact (opted out), new_inquiry (fresh request)';
COMMENT ON COLUMN leads.sent_to_sales_at IS 'Timestamp when lead was sent to sales team';
