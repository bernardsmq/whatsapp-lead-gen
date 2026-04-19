#!/bin/bash

# Supabase credentials
SUPABASE_URL="https://rtaeoiwivvojovuimdue.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0YWVvaXdpdm92am92dWltZHVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY1ODY2NjYsImV4cCI6MjA5MjE2MjY2Nn0.ca0Y_kAd7MZabcRCO2bbEuOXbzyWd8DNrUwvSzKx08E"

echo "🔧 Setting up Supabase database tables..."
echo ""

# Go to Supabase SQL Editor and run this manually:
echo "❌ IMPORTANT: You need to run this manually in Supabase SQL Editor"
echo ""
echo "1. Go to: https://supabase.com/dashboard/project/rtaeoiwivvojovuimdue/sql"
echo "2. Create a NEW QUERY"
echo "3. Paste ONE of these scripts and run each separately:"
echo ""

echo "========== SCRIPT 1: Create Users Table =========="
cat << 'EOF'
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT,
  role TEXT DEFAULT 'user',
  created_at TIMESTAMP DEFAULT NOW()
);
EOF

echo ""
echo "========== SCRIPT 2: Create Leads Table =========="
cat << 'EOF'
CREATE TABLE IF NOT EXISTS leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone TEXT NOT NULL,
  first_name TEXT NOT NULL,
  middle_name TEXT,
  last_name TEXT,
  email TEXT,
  gender TEXT,
  nationality TEXT,
  creation_date TEXT,
  status TEXT DEFAULT 'pending',
  score TEXT DEFAULT 'cold',
  created_at TIMESTAMP DEFAULT NOW()
);
EOF

echo ""
echo "========== SCRIPT 3: Create Qualifications Table =========="
cat << 'EOF'
CREATE TABLE IF NOT EXISTS qualifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  when_needed TEXT,
  car_type TEXT,
  timeframe TEXT,
  duration TEXT,
  special_notes TEXT,
  completed_criteria INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);
EOF

echo ""
echo "========== SCRIPT 4: Create Conversations Table =========="
cat << 'EOF'
CREATE TABLE IF NOT EXISTS conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  message TEXT NOT NULL,
  sender TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
EOF

echo ""
echo "========== SCRIPT 5: Create Batch Uploads Table =========="
cat << 'EOF'
CREATE TABLE IF NOT EXISTS batch_uploads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  admin_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  total_leads INTEGER DEFAULT 0,
  processed_count INTEGER DEFAULT 0,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW()
);
EOF

echo ""
echo "After creating all tables, test with:"
echo "  - Go to Table Editor"
echo "  - You should see: users, leads, qualifications, conversations, batch_uploads"
