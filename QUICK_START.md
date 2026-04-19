# Quick Start - WhatsApp Lead Gen System

## 🚀 Local Development (2 minutes)

### Prerequisites
- Node.js 18+
- Python 3.11+
- npm/yarn

### Run Locally

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
# Backend runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:3000
```

**Login:**
- Email: `admin@example.com`
- Password: `password`

---

## 🚄 Deploy to Railway (10 minutes)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Dockerfiles and deployment config"
git push origin main
```

### Step 2: Create Railway Project
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your repo

### Step 3: Configure Backend Service
1. Click "New" → "Service"
2. Select "Docker"
3. Point to `./backend/Dockerfile`
4. Add environment variables:
   ```
   SUPABASE_URL=https://rtaeoiwivovjovuimdue.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=sk-proj-...
   WHATSAPP_SALES_GUY_NUMBER=+37124811178
   FRONTEND_URL=https://your-frontend-railway.app
   ```
5. Deploy
6. Copy the backend URL (e.g., `https://backend-prod.railway.app`)

### Step 4: Configure Frontend Service
1. Click "New" → "Service"
2. Select "Docker"
3. Point to `./frontend/Dockerfile`
4. Add environment variables:
   ```
   VITE_API_URL=https://backend-prod.railway.app
   VITE_SUPABASE_URL=https://rtaeoiwivovjovuimdue.supabase.co
   VITE_SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
5. Deploy
6. Copy the frontend URL

### Step 5: Update Backend FRONTEND_URL
1. Go back to backend service
2. Update: `FRONTEND_URL=https://your-frontend-railway.app`
3. Redeploy

---

## ✅ Verify It Works

1. **Open** `https://your-frontend-railway.app`
2. **Login** with admin@example.com / password
3. **Upload** a test CSV with leads
4. **Check** if leads appear in dashboard
5. **View** real-time updates with Supabase subscriptions

---

## 📋 Test Checklist

- [ ] Dashboard loads
- [ ] Login works
- [ ] Can upload CSV
- [ ] Leads appear in table
- [ ] Can click lead and see details
- [ ] Chat viewer shows messages
- [ ] Stats update (Hot/Warm/Cold)
- [ ] Real-time updates work

---

## 🔌 Import n8n Workflows

After Railway deployment:

1. Go to n8n: `https://bgsystems.app.n8n.cloud`
2. Add environment variables:
   ```
   PHONE_NUMBER_ID=2001798287045224
   OPENAI_API_KEY=sk-proj-...
   SUPABASE_URL=https://rtaeoiwivovjovuimdue.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   BACKEND_URL=https://backend-prod.railway.app
   ```

3. Import workflows from `/n8n_workflows/` directory:
   - Click "Home" → "Import"
   - Select each workflow JSON
   - Deploy each workflow

---

## 🔐 Credentials Included

The system comes pre-configured with:
- ✅ Supabase project (rtaeoiwivovjovuimdue)
- ✅ Demo admin user (admin@example.com)
- ✅ OpenAI API key
- ✅ WhatsApp phone number

---

## 📚 API Documentation

**Backend API Docs:**
- Local: `http://localhost:8000/docs`
- Deployed: `https://backend-prod.railway.app/docs`

**Endpoints:**
- `POST /auth/login` - Login
- `POST /auth/register` - Register
- `GET /leads` - Get all leads
- `POST /sheets/upload` - Upload CSV
- `GET /dashboard/stats` - Get stats

---

## 🆘 Troubleshooting

**Issue: "Can't connect to Supabase"**
- Check SUPABASE_URL and SUPABASE_KEY are correct
- Verify Supabase project is online

**Issue: "Login fails"**
- Clear browser cache
- Check backend is running
- Verify JWT SECRET_KEY matches

**Issue: "Real-time updates not working"**
- Check Supabase realtime is enabled
- Verify SUPABASE_KEY has proper permissions
- Check browser console for errors

**Issue: "WhatsApp messages not sending"**
- Verify WhatsApp API token is valid
- Check phone number format (include country code)
- Check n8n workflows are deployed

---

## 📞 Support

- Supabase: https://app.supabase.com
- n8n: https://bgsystems.app.n8n.cloud
- Railway: https://railway.app/dashboard
- API Docs: `/docs` endpoint on backend

---

**You're all set! 🎉**

Deploy now and your WhatsApp Lead Gen system will be live!
