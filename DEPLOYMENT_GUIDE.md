# Deployment Guide - WhatsApp Lead Gen System

## Status: Ready to Deploy ✅

All code is built and tested. Ready to deploy to Railway.

## What's Been Built

✅ **Supabase Database** - All 5 tables created + schema
  - users, leads, conversations, qualifications, batch_uploads
  - Demo admin user: admin@example.com / password

✅ **FastAPI Backend** - Full API implementation
  - Auth endpoints (login, register)
  - Leads management (CRUD)
  - Sheet upload & processing
  - Dashboard stats

✅ **React Dashboard** - Complete frontend
  - Login page
  - Dashboard with stats (Hot/Warm/Cold)
  - Lead management table
  - Real-time chat viewer
  - Sheet upload zone

✅ **n8n Workflows** - 6 workflows ready to import
  - Workflow 1: Trigger send leads from sheet
  - Workflow 2: Send WhatsApp template
  - Workflow 3: Listen for WhatsApp replies
  - Workflow 4: AI qualify lead (GPT-4o mini)
  - Workflow 5: Handoff to sales guy
  - Workflow 6: Send AI message

---

## Deployment Steps

### Step 1: Import n8n Workflows (5 mins)
Location: `/whatsapp-lead-gen/n8n_workflows/`

Follow: `IMPORT_INSTRUCTIONS.md`

### Step 2: Deploy FastAPI Backend to Railway (10 mins)

1. **Create Railway account** (if not done)
   - Go to railway.app
   - Sign up with GitHub

2. **Create new project**
   - Click "New Project" → "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select the `whatsapp-lead-gen` repo

3. **Configure Backend Service**
   - Create new service
   - Specify: Python
   - Build command: `pip install -r backend/requirements.txt`
   - Start command: `cd backend && python main.py`
   - Port: `8000`

4. **Set Environment Variables**
   - Click service → Variables
   - Add these:
     ```
     SUPABASE_URL=https://rtaeoiwivovjovuimdue.supabase.co
     SUPABASE_KEY={your-anon-key}
     SECRET_KEY=your-secret-key-change-this
     N8N_BASE_URL=https://bgsystems.app.n8n.cloud
     N8N_API_KEY={your-n8n-api-key}
     N8N_WEBHOOK_SEND_TEMPLATE={n8n-webhook-url-from-step-1}
     WHATSAPP_SALES_GUY_NUMBER=+37124811178
     OPENAI_API_KEY=sk-proj-...
     FRONTEND_URL={your-frontend-railway-url}
     ```

5. **Deploy**
   - Click "Deploy"
   - Wait for green status
   - Copy the backend URL (e.g., `https://your-backend.railway.app`)

### Step 3: Deploy React Frontend to Railway (10 mins)

1. **Create new Railway service**
   - In same project, click "New Service"
   - Select Node.js

2. **Configure Frontend Service**
   - Build command: `cd frontend && npm install && npm run build`
   - Start command: `cd frontend && npm run preview` or use static hosting
   - Port: `3000`

3. **Set Environment Variables**
   ```
   VITE_API_URL=https://your-backend.railway.app
   VITE_SUPABASE_URL=https://rtaeoiwivovjovuimdue.supabase.co
   VITE_SUPABASE_KEY={your-anon-key}
   ```

4. **Deploy**
   - Click "Deploy"
   - Copy the frontend URL

### Step 4: Update Backend with Frontend URL (5 mins)

1. In Railway backend service, update:
   - `FRONTEND_URL={your-frontend-url}`

2. Redeploy backend

### Step 5: Configure n8n Webhooks (10 mins)

Update in n8n workflows:
- `BACKEND_URL` → `https://your-backend.railway.app`
- Redeploy each workflow

---

## Testing Checklist

- [ ] Dashboard login works (admin@example.com / password)
- [ ] Can upload CSV/Excel file
- [ ] Leads appear in dashboard
- [ ] Can click lead and see details
- [ ] Chat viewer displays messages (real-time Supabase)
- [ ] Stats update correctly (Hot/Warm/Cold counts)
- [ ] n8n workflows trigger on webhook calls
- [ ] WhatsApp messages send successfully
- [ ] AI qualification extracts data correctly
- [ ] Sales guy receives handoff message on WhatsApp

---

## Credentials Needed

**Supabase:**
- Project URL: `https://rtaeoiwivvojovuimdue.supabase.co`
- Anon Key: Get from Settings → API

**WhatsApp:**
- Phone Number ID: `2001798287045224`
- API Token: `EAASy1pOiAgsBRDUXPEDZAaReB7sLCQKjVQDTYmAlh35divSDMLdMw1qL25fo1187i8fWZAROZCBPDggrLjoZAhbmA3ZCX3TlRNIJp8UHQS1JZADMWWYdDuwWpcYTfODsQ4mwYcqWo5dL6NsXdmc7XtaBdDMzLyJTQChn4BZAvHw50JUZAlm8RsffhrokrcTvOQ2baAZA6YgsuZAQ8XuRabUnjjVCBZB4sL7pYMx8UCfBBfv9uJJWUDJeoT3GKeFB3XF6rmpspERsxGRQ1vbFS31RZC5Y88b9s4WKlJeDI1wurQZDZD`

**OpenAI:**
- API Key: `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`

---

## File Structure

```
whatsapp-lead-gen/
├── backend/                           # FastAPI backend
│   ├── main.py                       # App entry point
│   ├── auth.py                       # JWT & password auth
│   ├── database.py                   # Supabase client
│   ├── routes/                       # API endpoints
│   │   ├── auth.py, leads.py, sheets.py, dashboard.py
│   ├── services/                     # Business logic
│   │   ├── n8n_client.py, sheet_parser.py
│   ├── requirements.txt               # Python dependencies
│   └── .env.example
│
├── frontend/                          # React dashboard
│   ├── src/
│   │   ├── pages/                    # Pages (Login, Dashboard, etc)
│   │   ├── components/               # Reusable components
│   │   ├── hooks/                    # Custom hooks (auth, leads, etc)
│   │   ├── context/                  # Auth context
│   │   ├── lib/                      # Utilities (API, Supabase)
│   │   ├── App.jsx, main.jsx
│   │   └── index.css
│   ├── package.json, vite.config.js
│   └── .env.example
│
├── n8n_workflows/                     # n8n workflow JSONs
│   ├── workflow-1-trigger-send-leads.json
│   ├── workflow-2-send-whatsapp-template.json
│   ├── workflow-3-listen-whatsapp-replies.json
│   ├── workflow-4-ai-qualify-lead.json
│   ├── workflow-5-handoff-sales.json
│   ├── workflow-6-send-ai-message.json
│   └── IMPORT_INSTRUCTIONS.md
│
├── scripts/
│   └── setup_supabase.sql             # Database schema
│
└── README.md
```

---

## Support

- Backend API docs: `http://localhost:8000/docs` (Swagger UI)
- Supabase console: `https://app.supabase.com`
- n8n workflows: `https://bgsystems.app.n8n.cloud`
- React dev server: `npm run dev` in frontend folder

---

## Next: Start with Step 1 (n8n Import)

Go to `/n8n_workflows/IMPORT_INSTRUCTIONS.md` and follow the setup guide.

Once done, proceed to Railway deployment.
