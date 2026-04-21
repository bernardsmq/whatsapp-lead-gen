# RCR AI Dashboard Redesign - Implementation Guide

## Overview
Complete dashboard redesign with RCR AI branding, dark theme, and 3 new analytics endpoints.

## Backend API Endpoints

### 1. Analytics Stats
```
GET /analytics/stats
Headers: Authorization: Bearer {token}

Response:
{
  "qualification_rate": 45.5,          # % leads with all 3 details (car, duration, dates)
  "sales_handoffs_today": 3,           # Count sent to sales today
  "avg_score": 2.3,                    # Average: hot=3, warm=2, cold=1
  "reply_rate": 78.5,                  # % leads with messages
  "full_info_gathered": 45.5,          # % with complete data
  "total_sales_handoffs": 12           # Lifetime count
}
```

### 2. Messages by Date
```
GET /analytics/messages/by-date?date_str=2026-04-21
Headers: Authorization: Bearer {token}

Response: [
  {
    "id": "uuid",
    "lead_id": "uuid",
    "lead_name": "John Smith",
    "lead_phone": "+1234567890",
    "message": "I need a car for the weekend",
    "sender": "user" | "ai",
    "created_at": "2026-04-21T10:30:00Z",
    "delivery_status": "delivered"
  },
  ...
]
```

### 3. Recent Activity
```
GET /analytics/activity/recent?limit=20
Headers: Authorization: Bearer {token}

Response: [
  {
    "type": "lead_added" | "lead_scored" | "sent_to_sales" | "message_sent",
    "icon": "📝" | "⭐" | "🎯" | "💬",
    "title": "New lead added",
    "description": "John Smith",
    "timestamp": "2026-04-21T10:30:00Z",
    "lead_id": "uuid"
  },
  ...
]
```

## Frontend Structure

### Pages
- **Dashboard** (`/`) - Main dashboard with stats, pipeline, live activity
- **Import Leads** - CSV upload + manual lead form
- **All Leads** - Table view of all leads
- **Hot Leads** - Filtered table (score="hot")
- **Warm Leads** - Filtered table (score="warm")
- **Chats** - Conversation view (placeholder)
- **Messages Sent** - Date-filtered message history
- **Analytics** - Advanced metrics and AI performance
- **Settings** - Configuration (placeholder)

### Navigation
- Fixed left sidebar with RCR AI branding
- Collapsible menu for space management
- Yellow highlight for active page
- Logout button

### Components
- **Sidebar.jsx** - Navigation sidebar with RCR AI logo
- **StatsCard.jsx** - Metric cards with gradient backgrounds
- **UploadZone.jsx** - Drag-and-drop file upload
- **ManualLeadForm.jsx** - Add single lead form
- (Other existing components auto-styled with dark theme)

### Hooks
- **useAnalytics()** - Fetch analytics stats (30s refresh)
- **useMessagesByDate(dateStr)** - Fetch messages for date
- **useRecentActivity(limit)** - Fetch activity feed (10s refresh)

## Styling

### Colors
- **Background**: Slate-900 (`#0f172a`)
- **Cards**: Slate-800 with slate-700 borders
- **Text**: White on dark
- **Accents**: Yellow (buttons, highlights, active states)
- **Hot Leads**: Red (`bg-red-600`)
- **Warm Leads**: Yellow (`bg-yellow-600`)
- **Cold Leads**: Gray (`bg-slate-600`)

### Dark Theme
- All pages use dark theme
- High contrast text for readability
- Slate color palette for consistency
- Yellow (#FFFF00 area) for primary actions

## Branding Changes
- All "DriveAI" references → "RCR AI"
- Logo: Blue → Yellow gradient with "RCR" text
- Accent color: Blue → Yellow
- Product name: "WhatsApp Lead Gen" → "RCR AI Lead Gen"

## Key Features

### Dashboard
- 4 stat cards (Total, Hot, Messages, Conversion)
- Live activity feed (real-time events)
- Pipeline visualization (lead distribution)
- Dark theme with yellow accents

### Import Leads
- CSV/Excel drag-and-drop upload
- Manual form fields: Name, Phone, Car Interest (optional), Duration (optional)
- Immediate feedback on success/error

### All Leads & Filters
- Responsive table with 7 columns
- LEAD, PHONE, INTEREST, SCORE, LAST CONTACT, STATUS, ACTION
- Color-coded scores
- "View Chat" button for interactions

### Analytics
- 6 metric cards with key statistics
- AI Performance section with progress bars
- Qualification, Reply, and Sales Handoff metrics

### Messages
- Date picker for filtering
- Timestamp, sender, status for each message
- Lead info (name, phone) with each message
- Delivery status tracking

## Testing

### Test Backend Endpoints
```bash
# Login first to get token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password"}'

# Get analytics stats
curl http://localhost:8000/analytics/stats \
  -H "Authorization: Bearer {token}"

# Get messages for a date
curl "http://localhost:8000/analytics/messages/by-date?date_str=2026-04-21" \
  -H "Authorization: Bearer {token}"

# Get recent activity
curl "http://localhost:8000/analytics/activity/recent?limit=15" \
  -H "Authorization: Bearer {token}"
```

### Test Frontend
```bash
cd frontend
npm run dev
# Navigate to http://localhost:5173
# Login with: admin@example.com / password
```

## Files Modified/Created

### Backend
- `backend/routes/analytics.py` (NEW) - Analytics endpoints
- `backend/routes/dashboard.py` (UPDATED) - Enhanced stats
- `backend/main.py` (UPDATED) - Added analytics router

### Frontend
- `frontend/src/pages/Dashboard.jsx` (REBUILT)
- `frontend/src/pages/Login.jsx` (REDESIGNED)
- `frontend/src/components/Sidebar.jsx` (NEW)
- `frontend/src/components/StatsCard.jsx` (UPDATED)
- `frontend/src/components/UploadZone.jsx` (UPDATED)
- `frontend/src/components/ManualLeadForm.jsx` (UPDATED)
- `frontend/src/hooks/useAnalytics.js` (NEW)
- `frontend/src/lib/api.js` (UPDATED)
- `frontend/src/index.css` (UPDATED)

## Deployment

### Backend
```bash
# No new dependencies, uses existing:
# - FastAPI
# - Supabase
# - Python 3.8+

# Start server
python3 backend/main.py
# Or with uvicorn
uvicorn backend.main:app --reload
```

### Frontend
```bash
# Existing dependencies, no changes
cd frontend
npm install  # Already done
npm run build  # For production
npm run dev    # For development
```

## Future Enhancements

Placeholder pages ready for:
- Chats (conversation view)
- Settings (advanced configuration)

Additional potential features:
- Export lead reports
- Custom analytics filters
- Lead scoring history
- Message templates
- Team management
