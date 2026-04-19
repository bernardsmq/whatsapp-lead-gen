# 🚀 Deploy WhatsApp Lead Gen System - ONE COMMAND

## Option 1: Run Locally (1 minute) ⚡

```bash
cd /path/to/whatsapp-lead-gen
docker-compose up
```

Then open:
- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Login**: admin@example.com / password

---

## Option 2: Deploy to Railway (10 minutes) 🚄

### Prerequisites
- GitHub account
- Railway account (free: railway.app)

### Step 1: Push Code to GitHub

If you haven't already, create a GitHub repo and push:

```bash
cd /path/to/whatsapp-lead-gen
git remote add origin https://github.com/YOUR_USERNAME/whatsapp-lead-gen.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Railway (Using UI)

1. **Go to**: https://railway.app/dashboard
2. **Click**: "New Project"
3. **Select**: "Deploy from GitHub repo"
4. **Connect** your GitHub account and select your repo
5. **Wait** for it to auto-detect services

### Step 3: Configure Environment Variables

Railway will detect two services: `backend` and `frontend`

**For Backend service**, add these variables:
```
SUPABASE_URL=https://rtaeoiwivovjovuimdue.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0YWVvaXdpdm92anZvdWltZHVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE2NzE0NTAxNzgsImV4cCI6MTk4NzAyNjE3OH0.F40cZMZQfOcDFf7IuCz7P73KDPy-IWXO-hBlvwj9WQ8
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=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
WHATSAPP_SALES_GUY_NUMBER=+37124811178
FRONTEND_URL=https://your-frontend-railway.app
```

**For Frontend service**, add:
```
VITE_API_URL=https://your-backend-railway.app
VITE_SUPABASE_URL=https://rtaeoiwivovjovuimdue.supabase.co
VITE_SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ0YWVvaXdpdm92anZvdWltZHVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE2NzE0NTAxNzgsImV4cCI6MTk4NzAyNjE3OH0.F40cZMZQfOcDFf7IuCz7P73KDPy-IWXO-hBlvwj9WQ8
```

### Step 4: Deploy
- Click "Deploy" buttons for both services
- Wait for green checkmarks
- Copy the URLs

### Step 5: Set FRONTEND_URL
- Go back to Backend service
- Update: `FRONTEND_URL=https://your-frontend-url-from-step-4`
- Redeploy backend

---

## Step 6: Import n8n Workflows ✅

Once backend is live, import workflows:

1. **Go to**: https://bgsystems.app.n8n.cloud
2. **Click**: Home → Import
3. **Select** each workflow JSON from `/n8n_workflows/`:
   - workflow-1-trigger-send-leads.json
   - workflow-2-send-whatsapp-template.json
   - workflow-3-listen-whatsapp-replies.json
   - workflow-4-ai-qualify-lead.json
   - workflow-5-handoff-sales.json
   - workflow-6-send-ai-message.json

4. **For each workflow**, configure:
   - Supabase: URL + Key
   - OpenAI: API Key
   - Backend URL: `https://your-backend-railway.app`

---

## ✅ Done! Test It

1. **Open**: https://your-frontend-railway.app
2. **Login**: admin@example.com / password
3. **Upload** a CSV file
4. **See** leads appear live
5. **Check** real-time updates work

---

## 🔑 Pre-configured Credentials

Everything is already set up:
- ✅ Supabase project ready
- ✅ OpenAI API configured
- ✅ WhatsApp phone number set
- ✅ Demo admin user active
- ✅ Database schema deployed

Just follow the steps above and it's live!

---

## 💡 Pro Tips

- **Update Credentials**: Edit env vars in Railway → services → variables
- **View Logs**: Railway dashboard → service → logs
- **Scale**: Railway dashboard → service → deploy settings
- **API Docs**: `https://your-backend-railway.app/docs`
- **Supabase**: https://app.supabase.com → your project

---

## ❓ Need Help?

**Backend won't start?**
- Check SUPABASE_URL and SUPABASE_KEY in Railway
- Check OpenAI API key is valid
- View logs in Railway dashboard

**Frontend won't load?**
- Check VITE_API_URL points to correct backend
- Clear browser cache
- Check console errors (F12)

**n8n workflows failing?**
- Verify credentials are correct
- Check BACKEND_URL is set correctly in n8n env vars
- Test webhook URLs are accessible

---

**You're ready! Deploy now and your system is live in 10 minutes.** 🎉
