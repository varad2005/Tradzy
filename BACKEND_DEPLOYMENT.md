# Backend Deployment Guide

## Problem
Your frontend is deployed on Netlify (static hosting), but it needs a backend API to handle login, database operations, etc. Currently, the `BASE_URL` in `frontend/static/api.js` points to a placeholder URL, causing the "JSON.parse: unexpected character" error.

## Solution: Deploy Backend Separately

### Option 1: Deploy to Render (Recommended - Free Tier)

1. **Create a Render account**: https://render.com/

2. **Create a new Web Service**:
   - Connect your GitHub repository
   - Select `Tradzy` repository
   - Settings:
     - **Name**: `tradzy-backend` (or any name)
     - **Root Directory**: `backend`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r ../requirements.txt`
     - **Start Command**: `gunicorn app:app`
     - **Instance Type**: Free

3. **Add Environment Variables** in Render dashboard:
   ```
   FLASK_ENV=production
   SECRET_KEY=<generate-a-long-random-string>
   JWT_SECRET_KEY=<generate-another-random-string>
   CORS_WHITELIST=https://your-netlify-site.netlify.app,https://tradzy.netlify.app
   DATABASE_URL=<Render will provide SQLite or use PostgreSQL>
   ```

4. **Install Gunicorn** (add to requirements.txt):
   ```
   gunicorn==21.2.0
   ```

5. **Get your backend URL** (e.g., `https://tradzy-backend.onrender.com`)

### Option 2: Deploy to Railway

1. **Create a Railway account**: https://railway.app/

2. **Deploy from GitHub**:
   - Connect repository
   - Set root directory to `backend`
   - Railway auto-detects Python

3. **Set Environment Variables** (same as Render)

4. **Get your backend URL**

### Option 3: Deploy to PythonAnywhere (Free Tier)

1. **Create account**: https://www.pythonanywhere.com/

2. **Upload backend code** via web interface or git

3. **Configure WSGI file** to point to your Flask app

4. **Get your URL**: `http://yourusername.pythonanywhere.com`

---

## After Deploying Backend

### Step 1: Update api.js with your backend URL

Edit `frontend/static/api.js` and replace:
```javascript
const BASE_URL = 'https://your-backend-api.onrender.com/api';
```

With your actual backend URL:
```javascript
const BASE_URL = 'https://tradzy-backend.onrender.com/api';  // Your Render URL
```

### Step 2: Update CORS in backend

Edit `backend/config.py` and update `CORS_WHITELIST`:
```python
CORS_WHITELIST = [
    origin.strip()
    for origin in os.getenv(
        "CORS_WHITELIST", 
        "https://your-site.netlify.app,http://localhost:5000"  # Add your Netlify URL
    ).split(",")
    if origin.strip()
]
```

Or set the `CORS_WHITELIST` environment variable in your backend hosting platform to include your Netlify URL.

### Step 3: Test locally (optional)

Before committing, test that the URLs are correct:
```bash
# Update api.js with your backend URL
# Commit changes
git add frontend/static/api.js
git commit -m "feat: Connect frontend to deployed backend API"
git push origin main
```

Netlify will automatically rebuild and deploy.

### Step 4: Initialize Database on Backend

After deploying backend, run these commands on your backend server:

**For Render/Railway** (use their shell):
```bash
python
>>> from db import init_db
>>> init_db()
>>> exit()
```

**For PythonAnywhere** (use Bash console):
```bash
cd backend
python -c "from db import init_db; init_db()"
```

---

## Quick Start Commands

### Install Gunicorn (for production)
```bash
pip install gunicorn
pip freeze > requirements.txt
```

### Test Backend Locally
```bash
cd backend
python app.py
# Visit http://127.0.0.1:5000/api/health (should return JSON)
```

### Generate Secret Keys
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Troubleshooting

### Error: "JSON.parse: unexpected character"
- ✅ **Fixed by**: Deploying backend and updating `BASE_URL` in api.js

### Error: "CORS policy blocked"
- ✅ **Fix**: Add your Netlify URL to `CORS_WHITELIST` in backend config

### Error: "Failed to fetch"
- ✅ **Fix**: Check that backend URL is correct and backend is running
- ✅ **Fix**: Make sure backend URL uses `https://` not `http://`

### Database not initialized
- ✅ **Fix**: Run `init_db()` on your backend server (see Step 4 above)

---

## Architecture After Deployment

```
┌─────────────────────┐
│   Netlify           │
│   (Static Frontend) │
│   your-site.netlify │
└──────────┬──────────┘
           │
           │ API Calls (HTTPS)
           │
┌──────────▼──────────┐
│   Render/Railway    │
│   (Flask Backend)   │
│   tradzy-backend    │
│   + SQLite/Postgres │
└─────────────────────┘
```

---

## Current Status

- ✅ Frontend deployed to Netlify
- ❌ Backend NOT deployed (needed for login/data)
- ❌ `BASE_URL` still pointing to placeholder

**Next Action**: Deploy backend to Render, then update `api.js` with the URL.
