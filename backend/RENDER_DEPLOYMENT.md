# Render.com Deployment Guide for Kindo Backend

This guide walks you through deploying the Kindo FastAPI backend to Render.com and setting up the frontend as a static site.

## Prerequisites

- GitHub account with the Kindo backend repository
- Render.com account (free tier available)

## Part 1: Prepare Backend for Deployment

### 1.1 Verify Backend Configuration

✅ **render.yaml** - Already configured with:
- Python 3.13
- Auto-build from `requirements.txt`
- Auto-start command using Uvicorn on PORT $PORT
- Production environment variables

✅ **app/core/config.py** - Supports environment-based CORS:
- Development: allows all origins (`*`)
- Production: restricts to `["https://kindo-frontend.onrender.com", "https://kindo.com"]`

✅ **.env** - Development configuration
✅ **.env.example** - Template for shared settings
✅ **.gitignore** - Protects secrets (`.env`, `.env.local`, `*.db`)

### 1.2 Commit to GitHub

```bash
cd /Users/campidelli/projects/kindo
git add backend/
git commit -m "Backend ready for Render deployment"
git push origin main  # or your branch name
```

## Part 2: Deploy Backend to Render

### 2.1 Create Web Service on Render

1. Go to [render.com](https://render.com)
2. Sign up or log in
3. Click **"New +"** → **"Web Service"**
4. Select **"Deploy an existing repository"**
5. Connect your GitHub account and select the Kindo repo
6. Configure:
   - **Name**: `kindo-api`
   - **Branch**: `main` (or your branch)
   - **Runtime**: Python 3 (auto-detected)
   - **Build Command**: `pip install -r requirements.txt` (from render.yaml)
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (from render.yaml)
   - **Plan**: Free tier (adequate for development)

### 2.2 Environment Variables

In Render dashboard, add environment variables:
- `LOG_LEVEL` = `INFO`
- `ENVIRONMENT` = `production`
- `CORS_ORIGINS` = `["https://kindo.onrender.com"]` (update with your frontend URL)

**Note**: render.yaml already defines these defaults; Render UI values override them.

### 2.3 Deploy

1. Click **"Create Web Service"**
2. Render starts the build process (takes 2-5 minutes)
3. Wait for green checkmark: **"Your service is live"**
4. Copy the service URL (e.g., `https://kindo-api.onrender.com`)

### 2.4 Verify Backend

Test your backend deployment:

```bash
# Health check
curl https://kindo-api-3y26.onrender.com/admin/health

# Get API docs
curl https://kindo-api-3y26.onrender.com/docs

# Seed the database with sample data
curl -X POST https://kindo-api-3y26.onrender.com/admin/seed

# List trips
curl https://kindo-api-3y26.onrender.com/api/v1/trips

# Should return: [seeded trip object]
```

**Note**: The `/admin/seed` endpoint creates a sample trip if none exist. It's safe to call multiple times (idempotent).

## Part 3: Frontend Deployment (Static Site)

Once backend is deployed, set up Render static site for the frontend.

### 3.1 Create render.yaml in Frontend Root

Create `/frontend/render.yaml`:

```yaml
services:
  - type: static_site
    name: kindo-frontend
    env: static
    buildCommand: npm run build
    staticPublishPath: dist
    envVars:
      - key: VITE_API_URL
        value: https://kindo-api-3y26.onrender.com
```

### 3.2 Create Web Service for Frontend

1. In Render dashboard: **"New +"** → **"Web Service"** → Deploy frontend repo
2. Configure:
   - **Name**: `kindo-frontend`
   - **Branch**: `main`
   - **Build Command**: `npm run build`
   - **Start Command**: `npm run preview` (or serve from `dist/`)
   - **Plan**: Free tier
3. Add environment variable:
   - `VITE_API_URL` = `https://kindo-api-3y26.onrender.com`

### 3.3 Verify Frontend

Once deployed:
- Visit `https://kindo-frontend.onrender.com`
- Try creating a trip and payment
- Backend should respond with 201 PENDING status
- Polling `/api/v1/payments/{id}` should show status updates

## Important Notes

### SQLite Database on Free Tier

⚠️ **Database won't persist between redeploys** on Render free tier.

Each time you deploy, SQLite is reset. For production:

1. **Suggested**: Upgrade to PostgreSQL
   ```bash
   # Add to requirements.txt
   psycopg2-binary==2.9.9  # PostgreSQL driver
   ```
   
2. Update `app/core/database.py` to use PostgreSQL URL from `DATABASE_URL` env var.
3. Add PostgreSQL database on Render ($7/month) or use free tier (limited).

### Custom Domain (Optional)

In Render dashboard for both services:
- **Settings** → **Custom Domain**
- Add your domain (e.g., `api.kindo.com`)
- Configure DNS records as shown by Render

### Monitoring & Logs

- **Logs**: Render dashboard → Service → Logs tab
- **Metrics**: Dashboard shows uptime, response times, error rates
- Backend logs via structured logging (see `app/core/logging.py`)

### Environment Auto-Spindown

On free tier, service spins down after 15 min inactivity. First request after spindown takes ~30s. For production use, upgrade to paid tier or use keep-alive service.

### Post-Deployment Seeding

After your backend is live, seed the database with sample data:

```bash
curl -X POST https://kindo-api-3y26.onrender.com/admin/seed
```

**Response**:
```json
{"status": "seeded", "message": "Database seeded successfully"}
```

This creates a sample trip (Wellington Zoo Field Trip) in the database. The endpoint is idempotent—calling it multiple times is safe (subsequent calls skip if data exists).

**⚠️ Security Note**: The `/admin/seed` endpoint has **no authentication**. In production:
1. Add API key or JWT authentication
2. Or remove the endpoint from deployed environment
3. Or protect with a secret query parameter

## Troubleshooting

### Build Fails

1. Check **Logs** in Render dashboard
2. Common issues:
   - Missing `requirements.txt` in root → ensure in backend/ root
   - Python version mismatch → render.yaml specifies 3.13
   - Missing dependency → `pip freeze > requirements.txt` locally, commit, retry

### Backend Returns 500 Error

1. Check **Logs** in Render dashboard
2. Look for error traceback
3. Common issues:
   - SQLite path doesn't exist → `app/data/` is created on first startup
   - Missing `.env` variables → Verify environment variables in Render

### CORS Errors on Frontend

Frontend requests blocked? Production CORS is restricted to specific origins:
1. Update `CORS_ORIGINS` in Render environment variables or `.env.example`
2. Redeploy backend
3. Verify frontend URL matches CORS allowlist

### Tests Fail on Local But Pass on Render

Common causes:
- Different dependency versions → pin versions in `requirements.txt`
- Timezone issues → all timestamps use UTC (already handled)
- Database path differs → using absolute path (already fixed)

## Next Steps

1. ✅ Push backend to GitHub
2. 🚀 Deploy backend Web Service to Render
3. 🚀 Deploy frontend Web Service to Render (optional static site)
4. 🔗 Update frontend `.env` with backend URL
5. 📊 Monitor logs and uptime in Render dashboard
6. 💾 Plan PostgreSQL migration for production persistence
7. 🎯 Add custom domains (optional)

## Resources

- [Render.com Docs](https://render.com/docs)
- [Deploy Python FastAPI](https://render.com/docs/deploy-fastapi)
- [Environment Variables](https://render.com/docs/environment-variables)
- [Custom Domains](https://render.com/docs/custom-domains)
- [Static Sites](https://render.com/docs/static-sites)

---

**Questions?** Render support: support@render.com
