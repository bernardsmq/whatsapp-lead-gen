#!/usr/bin/env python3
import os
from supabase import create_client

# Get credentials from environment or use defaults
SUPABASE_URL = "https://rtaeoiwivvojovuimdue.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0YWVvaXdpdm92am92dWltZHVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY1ODY2NjYsImV4cCI6MjA5MjE2MjY2Nn0.ca0Y_kAd7MZabcRCO2bbEuOXbzyWd8DNrUwvSzKx08E"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQL to create all tables
sql_queries = [
    """
    CREATE TABLE IF NOT EXISTS users (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      name TEXT,
      role TEXT DEFAULT 'user',
      created_at TIMESTAMP DEFAULT NOW()
    );
    """,
    """
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
    """,
    """
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
    """,
    """
    CREATE TABLE IF NOT EXISTS conversations (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
      message TEXT NOT NULL,
      sender TEXT,
      created_at TIMESTAMP DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS batch_uploads (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      admin_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      filename TEXT NOT NULL,
      total_leads INTEGER DEFAULT 0,
      processed_count INTEGER DEFAULT 0,
      status TEXT DEFAULT 'pending',
      created_at TIMESTAMP DEFAULT NOW()
    );
    """
]

# Execute each query using Supabase RPC or direct query
try:
    # Use the admin API to run raw SQL
    from supabase import PostgrestAPIResponse

    print("Creating database tables...")

    # Create users table
    print("Creating users table...")
    supabase.postgrest.request(
        "POST",
        "/rpc/exec_sql",
        body={"sql": sql_queries[0]}
    )
    print("✓ Users table created")

    # Create leads table
    print("Creating leads table...")
    supabase.postgrest.request(
        "POST",
        "/rpc/exec_sql",
        body={"sql": sql_queries[1]}
    )
    print("✓ Leads table created")

    # Create qualifications table
    print("Creating qualifications table...")
    supabase.postgrest.request(
        "POST",
        "/rpc/exec_sql",
        body={"sql": sql_queries[2]}
    )
    print("✓ Qualifications table created")

    # Create conversations table
    print("Creating conversations table...")
    supabase.postgrest.request(
        "POST",
        "/rpc/exec_sql",
        body={"sql": sql_queries[3]}
    )
    print("✓ Conversations table created")

    # Create batch_uploads table
    print("Creating batch_uploads table...")
    supabase.postgrest.request(
        "POST",
        "/rpc/exec_sql",
        body={"sql": sql_queries[4]}
    )
    print("✓ Batch uploads table created")

    print("\n✓ All tables created successfully!")

except Exception as e:
    print(f"Error: {str(e)}")
    print("\nFalling back to manual approach...")
    print("Please manually run these SQL queries in Supabase SQL Editor:")
    for i, query in enumerate(sql_queries, 1):
        print(f"\n--- Query {i} ---")
        print(query)
