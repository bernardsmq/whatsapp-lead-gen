#!/usr/bin/env python3
"""Update admin password in Supabase"""

import requests
import sys

SUPABASE_URL = "https://rtaeoiwivvojovuimdue.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0YWVvaXdpdm92am92dWltZHVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY1ODY2NjYsImV4cCI6MjA5MjE2MjY2Nn0.ca0Y_kAd7MZabcRCO2bbEuOXbzyWd8DNrUwvSzKx08E"
NEW_HASH = "a5f1dbaf9fe025ac74de60996c775cc93816ff7472b21a1ba1fb09ecb6776e9d"

url = f"{SUPABASE_URL}/rest/v1/users?email=eq.admin@example.com"
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}
data = {"password_hash": NEW_HASH}

response = requests.patch(url, json=data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("✅ Password updated successfully!")
    sys.exit(0)
else:
    print("❌ Failed to update password")
    sys.exit(1)
