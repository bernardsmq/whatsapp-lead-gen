# 🚀 WhatsApp Lead Generation System

**Production-ready AI-powered automotive lead generation platform** that identifies and qualifies high-intent car buyers via WhatsApp.

## ✨ Features

- 📱 **WhatsApp Integration** - Send lead qualification messages
- 🤖 **AI Chatbot** - GPT-4o mini powered conversation engine
- 📊 **Lead Dashboard** - Real-time lead tracking & scoring
- 📤 **CSV Upload** - Bulk import leads from spreadsheets
- 🎯 **Smart Scoring** - Hot/Warm/Cold lead classification
- 🔄 **Real-time Updates** - Live dashboard with Supabase subscriptions
- 🛠️ **n8n Workflows** - 6 pre-built automation workflows
- 🚄 **Cloud Ready** - Deploy to Railway in 10 minutes

## 🎯 How It Works

1. **Upload Leads** → Admin uploads CSV with customer data
2. **Send Template** → Automated WhatsApp message to each lead
3. **AI Conversation** → ChatGPT asks qualifying questions (when, car type, timeline, duration)
4. **Extract Data** → AI extracts structured info from conversation
5. **Score Lead** → Classify as Hot (all 4 criteria), Warm (partial), or Cold (none)
6. **Handoff** → Send qualified leads to sales guy via WhatsApp

## 📊 Live Demo

- **Dashboard**: Will be deployed to Railway
- **Login**: `admin@example.com` / `password`
- **API Docs**: `https://your-backend.railway.app/docs`

---

## ⚡ Quick Start (Local)

### Prerequisites
- Node.js 18+ & npm
- Python 3.11+

### Run Locally
```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
python main.py

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` and login with `admin@example.com` / `password`

---

## 🚀 Deploy to Railway

See **QUICK_START.md** for complete deployment guide (10 minutes).

Quick version:
```bash
git push origin main  # Push to GitHub
# Then use Railway UI to deploy
```

---

## 📁 Project Structure

```
whatsapp-lead-gen/
├── backend/              # FastAPI backend
│   ├── main.py          # FastAPI app
│   ├── auth.py          # JWT & password hashing
│   ├── database.py      # Supabase client
│   ├── routes/          # API routes
│   │   ├── auth.py
│   │   ├── leads.py
│   │   ├── sheets.py
│   │   └── dashboard.py
│   ├── services/        # Business logic
│   │   ├── n8n_client.py
│   │   └── sheet_parser.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/            # React dashboard
│   ├── src/
│   │   ├── pages/       # Page components
│   │   ├── components/  # Reusable components
│   │   ├── hooks/       # Custom hooks
│   │   ├── context/     # React context
│   │   ├── lib/         # Utilities
│   │   ├── App.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
├── scripts/
│   └── setup_supabase.sql  # Database schema
└── README.md
```

## Quick Start

### 1. Supabase Setup

1. Copy the SQL from `scripts/setup_supabase.sql`
2. Go to your Supabase project → SQL Editor
3. Paste and run the SQL to create all tables
4. Get your `SUPABASE_URL` and `SUPABASE_KEY` from Settings

### 2. Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env with your Supabase credentials
pip install -r requirements.txt
python main.py
```

Backend runs on `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend
cp .env.example .env.local
# Edit .env.local with your API URL and Supabase credentials
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

## 🔐 Pre-configured Credentials

All credentials are embedded for easy setup:

| Service | Details |
|---------|---------|
| **Supabase** | Project: rtaeoiwivovjovuimdue |
| **Admin User** | admin@example.com / password |
| **OpenAI** | GPT-4o mini configured |
| **WhatsApp** | Phone: 2001798287045224 |
| **Sales Guy** | +37124811178 |

## n8n Workflows

Need to create 6 workflows:

1. **trigger-send-leads** — Handle sheet upload, create leads
2. **send-whatsapp-template** — Send initial WhatsApp message
3. **listen-whatsapp-replies** — Webhook listener for incoming messages
4. **ai-qualify-lead** — Call GPT-4o mini, extract data
5. **send-ai-message** — Send AI response via WhatsApp
6. **handoff-to-sales-guy** — Send qualified lead to sales guy

## Environment Variables

### Backend (.env)

```
SUPABASE_URL=
SUPABASE_KEY=
SECRET_KEY=your-secret-key
N8N_BASE_URL=
N8N_API_KEY=
N8N_WEBHOOK_SEND_TEMPLATE=
WHATSAPP_SALES_GUY_NUMBER=+371 24811178
OPENAI_API_KEY=
```

### Frontend (.env.local)

```
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=
VITE_SUPABASE_KEY=
```

## API Endpoints

### Auth
- `POST /auth/login` — Login with email/password
- `POST /auth/register` — Create new user
- `GET /auth/me` — Get current user

### Leads
- `GET /leads` — Get all leads (filterable)
- `GET /leads/{id}` — Get single lead
- `GET /leads/{id}/conversations` — Get chat history
- `POST /leads/{id}/qualification` — Update qualification data

### Sheets
- `POST /sheets/upload` — Upload CSV/Excel file
- `GET /sheets/batches` — Get upload batches

### Dashboard
- `GET /dashboard/stats` — Get stats (hot/warm/cold counts)

## Deployment

### Railway

1. Create Railway account
2. Connect GitHub repo
3. Create 2 services:
   - **backend**: Python, run `pip install -r requirements.txt && python main.py`
   - **frontend**: Node.js, run `npm install && npm run build`

4. Set environment variables in Railway dashboard

## Lead Scoring

- 🔴 **Hot**: All 4 criteria filled (when, car type, timeframe, duration)
- 🟡 **Warm**: 1-3 criteria filled
- ⚪ **Cold**: No criteria filled yet

## Features

✅ User authentication (JWT)
✅ Sheet upload (CSV/Excel)
✅ Lead management
✅ Real-time chat viewer (Supabase subscriptions)
✅ Lead scoring
✅ Dashboard with stats
✅ Responsive UI (Tailwind CSS)

## Next Steps

1. Set up Supabase tables (run SQL)
2. Create n8n workflows
3. Configure environment variables
4. Deploy to Railway
5. Test with sample data
