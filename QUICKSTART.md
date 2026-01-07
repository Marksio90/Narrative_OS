# Narrative OS - Quick Start Guide

Get up and running with Narrative OS in **5 minutes**.

## Prerequisites

- **Docker & Docker Compose** (for backend infrastructure)
- **Python 3.11+** (for backend)
- **Node.js 18+** (for frontend)
- **Git**

## Step 1: Clone & Setup Infrastructure

```bash
# Clone the repository
git clone https://github.com/Marksio90/Narrative_OS.git
cd Narrative_OS

# Start infrastructure (PostgreSQL + Redis)
docker-compose up -d

# Wait for services to be healthy (~10 seconds)
```

## Step 2: Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Edit .env and add your LLM API keys:
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-your-key-here
# Or use ANTHROPIC_API_KEY for Claude

# Run database migrations
alembic upgrade head

# Start backend server
python main.py
```

Backend will run at: **http://localhost:8000**

## Step 3: Frontend Setup

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start frontend development server
npm run dev
```

Frontend will run at: **http://localhost:3000**

## Step 4: Verify Installation

Open your browser to **http://localhost:3000** and you should see:

- **Home page** with 4 module cards
- Navigation to Canon, Planner, Editor, and Promises
- All pages should load (they'll be empty initially)

## Step 5: Create Your First Project

Currently, the system uses project_id=1 by default. Start creating content:

### 1. Define Your World (Canon Studio)

Navigate to **Canon** tab:

- **Add a Character:**
  - Name: "Elena"
  - Goals: "Master her craft", "Protect her village"
  - Behavioral Limits: "Never abandons friends"

- **Add a Location:**
  - Name: "The Forge"
  - Atmosphere: "Hot, smoky, filled with the ring of hammers"

- **Add a Canon Contract:**
  - Name: "No Deus Ex Machina"
  - Rule: "All powers must be established before use"
  - Severity: Must

### 2. Plan Your Story (Planner)

Navigate to **Planner** tab:

- **Create Book Arc:**
  - Premise: "A blacksmith discovers she's the chosen one"
  - Protagonist Goal: "Master mysterious powers while protecting her village"
  - Central Conflict: "Ancient evil awakens"
  - Stakes: "Village will be destroyed if she fails"
  - Act breaks: 6, 12, 18, 23

- **Add Chapter 1:**
  - Title: "The Ordinary World"
  - Summary: "Elena works at her forge when a stranger arrives"
  - POV Character: "Elena"
  - Location: "The Forge"

### 3. Generate Prose (Editor)

Navigate to **Editor** tab:

*Note: You'll need to create scene cards first via API (scene creation UI coming soon)*

Once you have a scene:
- Enter the Scene ID
- Click "Generate"
- View generated prose
- Review QC Report with scores
- See extracted facts

### 4. Track Promises (Promise Ledger)

Navigate to **Promises** tab:

- View automatically detected narrative promises
- Filter by status (open/fulfilled/abandoned)
- Track deadlines
- See confidence scores

## API Documentation

Backend API docs available at: **http://localhost:8000/docs** (FastAPI Swagger UI)

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `docker ps`
- Verify database migrations: `alembic current`
- Check .env has valid LLM API keys

### Frontend won't connect
- Verify backend is running at http://localhost:8000
- Check browser console for CORS errors
- Verify NEXT_PUBLIC_API_URL in frontend/.env

### Database errors
```bash
# Reset database
docker-compose down -v
docker-compose up -d
cd backend && alembic upgrade head
```

## Next Steps

1. **Read the full docs:**
   - `docs/SETUP.md` - Detailed setup instructions
   - `docs/MVP_STATUS.md` - Feature overview
   - `docs/END_TO_END_TEST.md` - Complete example workflow

2. **Explore the API:**
   - Visit http://localhost:8000/docs
   - Try the example requests from `END_TO_END_TEST.md`

3. **Plan your novel:**
   - Define all your characters and locations
   - Create canon contracts for consistency
   - Plan your book arc and chapters
   - Generate scenes one by one

## Need Help?

- **Issues:** https://github.com/Marksio90/Narrative_OS/issues
- **Documentation:** See `docs/` folder
- **API Reference:** http://localhost:8000/docs

## What Makes This Special?

- **Canon Contracts** - Hard rules AI cannot break
- **Promise Ledger** - Never abandon a narrative setup
- **Writers' Room QC** - Multi-agent quality validation
- **Scene-by-Scene** - Granular control over generation

Built for **serious fantasy/thriller authors** writing 300-600 page novels.

---

**You're ready to write!** 📖✨
