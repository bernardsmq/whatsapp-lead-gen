# Deployment Guide for WhatsApp Lead Generation System

## Railway Configuration

This project has two services: `frontend` and `backend`. Both need to be configured with environment variables for proper communication.

### Environment Variables Required

#### Backend Environment Variables

Set these in Railway for the `backend` service:

```
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-anon-key>
SECRET_KEY=<your-secret-key>
OPENAI_API_KEY=<your-openai-api-key>
WHATSAPP_SALES_GUY_NUMBER=+1234567890
FRONTEND_URL=<frontend-service-url>
```

**IMPORTANT:** `FRONTEND_URL` must be set to the exact URL where the frontend is deployed (e.g., `https://whatsapp-lead-gen-production.up.railway.app`)

#### Frontend Environment Variables

Set these in Railway for the `frontend` service:

```
VITE_API_URL=<backend-service-url>
VITE_SUPABASE_URL=<your-supabase-url>
VITE_SUPABASE_KEY=<your-supabase-anon-key>
```

**IMPORTANT:** `VITE_API_URL` must be set during build time to the exact backend API URL (e.g., `https://whatsapp-lead-gen-api.up.railway.app` or `https://whatsapp-lead-gen-production.up.railway.app`)

### Determining Service URLs

In Railway:

1. **Frontend Service URL:** Navigate to the frontend service in Railway dashboard → Settings → Networking → Copy the public URL
2. **Backend Service URL:** Navigate to the backend service in Railway dashboard → Settings → Networking → Copy the public URL

These URLs might be:
- Same domain with different services: `whatsapp-lead-gen-production.up.railway.app`
- Different subdomains: `whatsapp-lead-gen-production-frontend.up.railway.app` and `whatsapp-lead-gen-production-api.up.railway.app`
- Or any variation depending on Railway's routing configuration

### Testing the Configuration

After deploying, visit the debug page to verify connectivity:

```
https://<frontend-url>/debug
```

This page will show:
- ✅ Frontend URL (where you're accessing from)
- ✅ API Base URL (where the frontend will send requests)
- ✅ Auth Token (if logged in)
- ✅ Health Check results
- ✅ Leads Endpoint test
- ✅ Stats Endpoint test

All checks should return `Status: 200` for proper operation.

### If Leads Endpoint Shows Error

1. **Check the debug page** - Visit `/debug` page for detailed error messages
2. **Verify FRONTEND_URL** - Make sure `FRONTEND_URL` environment variable matches your frontend's actual URL
3. **Verify VITE_API_URL** - Make sure `VITE_API_URL` environment variable matches your backend's actual URL
4. **Check CORS** - Open browser DevTools (F12) → Network tab → Look for the `/leads` request
   - If it shows `(blocked...)`: CORS or mixed content issue
   - If it shows red error: Network/connection issue
   - If it shows `401`: Authentication issue
5. **Review Browser Console** - Open F12 → Console to see detailed error messages

### Common Issues

#### Mixed Content Error
- **Problem:** HTTPS frontend trying to fetch from HTTP backend
- **Solution:** Ensure all URLs use HTTPS in production

#### CORS Error
- **Problem:** Request from frontend domain blocked by backend CORS policy
- **Solution:** Verify `FRONTEND_URL` environment variable on backend matches frontend domain exactly

#### 401 Unauthorized
- **Problem:** Valid token becoming invalid after container restart
- **Solution:** Backend JWT secret may have changed. Re-login to get new token

#### 404 Not Found
- **Problem:** Endpoint path doesn't exist
- **Solution:** Check that backend routes are properly registered and accessible

## Local Development

### Running Both Services Locally

```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export FRONTEND_URL=http://localhost:3000
python main.py

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

Frontend will be at `http://localhost:5173` and backend at `http://localhost:8000`

The frontend's Vite dev server has a proxy that routes `/api` to the backend (see `frontend/vite.config.js`)

## Production Build

The Docker builds are configured in `Dockerfile` files:
- `frontend/Dockerfile` - Node.js app serving built React application
- `backend/Dockerfile` - Python/FastAPI application

Railway will automatically build and deploy these when you push code.
