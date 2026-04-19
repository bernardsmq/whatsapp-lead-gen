-- Create users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name TEXT NOT NULL,
  role TEXT DEFAULT 'admin' CHECK (role IN ('admin', 'sales_guy')),
  whatsapp_number TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create leads table
CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone TEXT UNIQUE NOT NULL,
  first_name TEXT NOT NULL,
  middle_name TEXT,
  last_name TEXT,
  email TEXT,
  gender TEXT,
  nationality TEXT,
  creation_date TIMESTAMP,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'qualified', 'handed_off')),
  score TEXT DEFAULT 'cold' CHECK (score IN ('hot', 'warm', 'cold')),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create conversations table
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  message_type TEXT CHECK (message_type IN ('incoming', 'outgoing')),
  sender TEXT CHECK (sender IN ('user', 'ai', 'system')),
  content TEXT NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create qualifications table
CREATE TABLE qualifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID UNIQUE NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  when_needed TEXT,
  car_type TEXT,
  timeframe TEXT CHECK (timeframe IN ('short_term', 'long_term')),
  duration TEXT,
  special_notes TEXT,
  completed_criteria INTEGER DEFAULT 0,
  qualified_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create batch_uploads table
CREATE TABLE batch_uploads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  admin_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  total_leads INTEGER DEFAULT 0,
  processed_count INTEGER DEFAULT 0,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  n8n_execution_id TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_leads_score ON leads(score);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_phone ON leads(phone);
CREATE INDEX idx_conversations_lead_id ON conversations(lead_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_qualifications_lead_id ON qualifications(lead_id);
CREATE INDEX idx_batch_uploads_admin_id ON batch_uploads(admin_id);

-- Enable RLS (Row Level Security)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE qualifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_uploads ENABLE ROW LEVEL SECURITY;

-- Create policies (permissive for MVP)
CREATE POLICY "Allow all reads for users" ON users FOR SELECT USING (true);
CREATE POLICY "Allow all reads for leads" ON leads FOR SELECT USING (true);
CREATE POLICY "Allow all reads for conversations" ON conversations FOR SELECT USING (true);
CREATE POLICY "Allow all reads for qualifications" ON qualifications FOR SELECT USING (true);
CREATE POLICY "Allow all reads for batch_uploads" ON batch_uploads FOR SELECT USING (true);

CREATE POLICY "Allow all writes for users" ON users FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all writes for leads" ON leads FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all writes for conversations" ON conversations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all writes for qualifications" ON qualifications FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all writes for batch_uploads" ON batch_uploads FOR ALL USING (true) WITH CHECK (true);

-- Create demo admin user (password: password)
INSERT INTO users (email, password_hash, name, role) VALUES (
  'admin@example.com',
  '$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss7KIUgO2t0jKMm2',
  'Admin User',
  'admin'
);
