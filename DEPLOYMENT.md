# TalentGrid Free Deployment Guide

This guide covers deploying TalentGrid for free (or nearly free) for about 1 week.

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│    Backend      │────▶│   PostgreSQL    │
│(Netlify/GitHub) │     │   (Railway)     │     │   (Railway)     │
│    FREE         │     │   $5 credit     │     │   included      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Option A: Railway + Netlify (Recommended - Simplest)

Railway gives $5 free credit = ~1 week of light usage.
Netlify is free forever for static sites.

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. You get $5 free credit (no credit card needed)

### Step 2: Deploy PostgreSQL

1. Click **"New Project"**
2. Select **"Provision PostgreSQL"**
3. Wait for it to deploy (~30 seconds)
4. Click on the PostgreSQL service
5. Go to **"Variables"** tab
6. Copy the `DATABASE_URL` value (you'll need this)

### Step 3: Deploy Backend

1. In the same project, click **"New Service"**
2. Select **"GitHub Repo"**
3. Connect your GitHub and select the TalentGrid repo
4. Set the **Root Directory** to `backend`
5. Railway will detect the Dockerfile

#### Add Environment Variables

Go to the **"Variables"** tab and add:

```
DATABASE_URL=<paste from PostgreSQL service>
SECRET_KEY=<generate-a-random-string>
MISTRAL_API_KEY=<your-mistral-key>
GROQ_API_KEY=<your-groq-key>
GEMINI_API_KEY=<your-gemini-key>
CHROMA_DB_PATH=/app/chroma_db
```

#### Add Persistent Volume (for ChromaDB)

1. Go to **"Settings"** tab
2. Scroll to **"Volumes"**
3. Add a volume:
   - Mount Path: `/app/chroma_db`
   - Size: 1GB (free tier allows this)

### Step 4: Get Your Backend URL

1. Go to **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. Copy the URL (e.g., `talentgrid-backend.up.railway.app`)

### Step 5: Deploy Frontend to Netlify

**Option A: Drag & Drop (Easiest)**
```bash
# Build locally
cd frontend
npm install
npm run build

# Then go to netlify.com and drag the 'dist' folder
```

**Option B: CLI**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Build and deploy
cd frontend
npm run build
netlify deploy --prod --dir=dist
```

**Option C: Connect GitHub**
1. Go to [netlify.com](https://netlify.com)
2. Sign up → "Add new site" → "Import from Git"
3. Select your TalentGrid repo
4. Configure:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
5. Add environment variable:
   - `VITE_API_URL` = `https://your-backend.up.railway.app/api`
6. Deploy!

---

## Option B: Railway + Cloudflare Pages

Cloudflare Pages has excellent global accessibility.

### Deploy Frontend to Cloudflare Pages

1. Go to [pages.cloudflare.com](https://pages.cloudflare.com)
2. Sign up with email
3. Click **"Create a project"** → **"Connect to Git"**
4. Select your TalentGrid repo
5. Configure build:
   - Framework preset: None
   - Build command: `cd frontend && npm install && npm run build`
   - Build output directory: `frontend/dist`
6. Add environment variable:
   - `VITE_API_URL` = `https://your-backend.up.railway.app/api`
7. Deploy!

---

## Option C: Railway + GitHub Pages

GitHub Pages is 100% free with no geographic restrictions.

### Deploy Frontend to GitHub Pages

1. Go to your GitHub repo → **Settings** → **Pages**
2. Source: **GitHub Actions**
3. Go to **Settings** → **Secrets and variables** → **Actions**
4. Add variable: `VITE_API_URL` = `https://your-backend.up.railway.app/api`
5. Push to main branch - deployment happens automatically!

The workflow file `.github/workflows/deploy-frontend.yml` is already set up.

---

## Option D: All-in-One Railway

Deploy both frontend and backend on Railway (uses more of your $5 credit).

### Deploy Frontend as Static Site

1. In your Railway project, click **"New Service"**
2. Select **"GitHub Repo"**
3. Set **Root Directory** to `frontend`
4. Add environment variable: `VITE_API_URL`
5. Railway will build and serve the static files

---

## Option B: Render (100% Free, but with limitations)

Render has a completely free tier but with cold starts (15 min timeout).

### Limitations
- Backend spins down after 15 min of inactivity
- First request after sleep takes 30-60 seconds
- Disk is ephemeral (ChromaDB resets on redeploy)

### Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub

### Step 2: Deploy PostgreSQL

1. Click **"New +"** → **"PostgreSQL"**
2. Name: `talentgrid-db`
3. Plan: **Free** (90 days)
4. Click **"Create Database"**
5. Copy the **External Database URL**

### Step 3: Deploy Backend

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repo
3. Configure:
   - **Name**: `talentgrid-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Docker`
   - **Plan**: Free

4. Add Environment Variables:
   ```
   DATABASE_URL=<external-database-url>
   SECRET_KEY=<random-string>
   MISTRAL_API_KEY=<your-key>
   GROQ_API_KEY=<your-key>
   ```

5. Click **"Create Web Service"**

### Step 4: Deploy Frontend

1. Click **"New +"** → **"Static Site"**
2. Connect repo, set root to `frontend`
3. Build command: `npm run build`
4. Publish directory: `dist`
5. Add env: `VITE_API_URL=https://your-backend.onrender.com`

---

## Option C: Fly.io (More Control)

Fly.io offers free tier with persistent volumes.

### Step 1: Install Fly CLI

```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

### Step 2: Login/Signup

```bash
fly auth signup  # or fly auth login
```

### Step 3: Create fly.toml

Create `backend/fly.toml`:

```toml
app = "talentgrid-backend"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"
  CHROMA_DB_PATH = "/data/chroma_db"

[http_service]
  internal_port = 8000
  force_https = true

[mounts]
  source = "chroma_data"
  destination = "/data"
```

### Step 4: Deploy

```bash
cd backend

# Create app
fly apps create talentgrid-backend

# Create PostgreSQL
fly postgres create --name talentgrid-db

# Attach database
fly postgres attach talentgrid-db

# Create volume for ChromaDB
fly volumes create chroma_data --size 1

# Set secrets
fly secrets set MISTRAL_API_KEY=xxx GROQ_API_KEY=xxx SECRET_KEY=xxx

# Deploy
fly deploy
```

---

## Getting Free API Keys

### 1. Mistral (Required for OCR)
- Go to: [console.mistral.ai](https://console.mistral.ai)
- Sign up → Create API key
- Free tier: Limited but sufficient for testing

### 2. Groq (Required for parsing - FREE)
- Go to: [console.groq.com](https://console.groq.com)
- Sign up → Create API key
- **14,400 requests/day FREE** ✨

### 3. Google Gemini (Fallback parser - FREE)
- Go to: [aistudio.google.com](https://aistudio.google.com)
- Sign up → Get API key
- Free tier generous

### 4. Cohere (Optional - re-ranking)
- Go to: [dashboard.cohere.com](https://dashboard.cohere.com)
- Free tier: 1000 calls/month

---

## Quick Cost Comparison

| Platform | Backend | Database | Duration | Cost |
|----------|---------|----------|----------|------|
| Railway | $5 credit | Included | ~1 week | FREE |
| Render | Free (cold starts) | Free 90 days | 90 days | FREE |
| Fly.io | Free tier | Free Postgres | Ongoing | FREE |
| Vercel | N/A (frontend) | N/A | Forever | FREE |

---

## Post-Deployment Checklist

- [ ] Backend responds at `/health`
- [ ] Database connected (check logs)
- [ ] Frontend loads and connects to backend
- [ ] CV upload works
- [ ] Search returns results
- [ ] Run reindex if needed: `POST /api/admin/reindex`

---

## Troubleshooting

### "Module not found" errors
- Ensure all dependencies are in `requirements.txt`
- Check Dockerfile installs all system dependencies

### Database connection errors
- Verify `DATABASE_URL` format: `postgresql://user:pass@host:port/dbname`
- Check database is running and accessible

### ChromaDB errors on Render
- Free tier has ephemeral disk - data resets on redeploy
- Solution: Use Railway with persistent volume or accept reindexing

### Cold start timeouts (Render)
- First request after 15 min may timeout
- Increase client timeout or use Railway

### Out of memory
- SentenceTransformers needs ~500MB-1GB
- Ensure your plan has sufficient RAM
- Railway/Fly.io free tiers should work

---

## My Recommendation

For a 1-week demo:

1. **Railway** - Simplest, $5 credit covers it
2. **Frontend on Vercel** - Always free, fast CDN
3. **Use Groq** - 14,400 free requests/day is plenty

Total cost: **$0** (within Railway's free credit)
