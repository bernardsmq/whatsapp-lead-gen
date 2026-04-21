#!/usr/bin/env python3
"""
Initialize database with admin user and sample data
Run: python init_db.py
"""

import os
from dotenv import load_dotenv
from database import supabase
from auth import hash_password

load_dotenv()

def init_admin():
    """Create or reset admin user"""
    try:
        print("Initializing admin user...")

        admin_email = "admin@example.com"
        admin_password = "password"

        # Check if admin exists
        response = supabase.table("users").select("*").eq("email", admin_email).execute()

        hashed = hash_password(admin_password)

        if response.data:
            # Update existing
            supabase.table("users").update({
                "password_hash": hashed,
                "name": "Admin",
                "role": "admin"
            }).eq("email", admin_email).execute()
            print(f"✓ Admin user updated: {admin_email} / {admin_password}")
        else:
            # Create new
            supabase.table("users").insert({
                "email": admin_email,
                "password_hash": hashed,
                "name": "Admin",
                "role": "admin"
            }).execute()
            print(f"✓ Admin user created: {admin_email} / {admin_password}")
    except Exception as e:
        print(f"✗ Failed to init admin: {e}")

def add_sample_leads():
    """Add sample leads for testing"""
    try:
        print("\nAdding sample leads...")

        sample_leads = [
            {
                "phone": "+37124811178",
                "first_name": "Bernard",
                "last_name": "Smith",
                "email": "bernard@example.com",
                "status": "new",
                "score": "cold"
            },
            {
                "phone": "+37124811179",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "status": "qualified",
                "score": "warm"
            },
            {
                "phone": "+37124811180",
                "first_name": "Jane",
                "last_name": "Wilson",
                "email": "jane@example.com",
                "status": "qualified",
                "score": "hot"
            }
        ]

        for lead in sample_leads:
            # Check if lead exists
            response = supabase.table("leads").select("*").eq("phone", lead["phone"]).execute()

            if not response.data:
                supabase.table("leads").insert(lead).execute()
                print(f"  ✓ Added lead: {lead['first_name']} ({lead['phone']})")
            else:
                print(f"  - Lead already exists: {lead['phone']}")

    except Exception as e:
        print(f"✗ Failed to add sample leads: {e}")

def check_database():
    """Verify database tables exist"""
    try:
        print("\nChecking database tables...")

        tables = ["users", "leads", "conversations", "qualifications", "batch_uploads"]

        for table in tables:
            try:
                response = supabase.table(table).select("id").limit(1).execute()
                print(f"  ✓ Table '{table}' exists")
            except Exception as e:
                print(f"  ✗ Table '{table}' missing or error: {e}")

    except Exception as e:
        print(f"✗ Failed to check database: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("WhatsApp Lead Gen - Database Initialization")
    print("=" * 50)

    check_database()
    init_admin()
    add_sample_leads()

    print("\n" + "=" * 50)
    print("✓ Initialization complete!")
    print("=" * 50)
