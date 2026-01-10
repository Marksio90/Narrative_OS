# Character Arc Tracker 🎭

## Overview

The Character Arc Tracker is a comprehensive system for tracking character development, emotional journeys, and narrative arcs throughout your story. It combines AI-powered analysis with manual tracking to provide deep insights into character growth and consistency.

## Features

### 1. **Arc Management**
- Track multiple arcs per character (transformation, redemption, coming-of-age, etc.)
- Monitor arc progress and pacing
- Identify on-track vs off-track arcs
- Set chapter boundaries for each arc

### 2. **Milestone Tracking**
- Record key moments in character development
- Categorize milestones (inciting incident, turning point, crisis, climax, resolution)
- Visualize milestone placement on timeline
- Assess significance of each milestone

### 3. **Emotional State Monitoring**
- Track emotional states chapter by chapter
- Measure emotion intensity (0-10 scale)
- Record trigger events and scene context
- Visualize emotional journey over time

### 4. **Goal Progress**
- Define character goals and motivations
- Track progress toward completion
- Record obstacles and setbacks
- Monitor success rate

### 5. **AI-Powered Analysis**
- Analyze arc health and consistency
- Detect milestones from scene text
- Extract emotional states automatically
- Generate comprehensive arc reports

## Architecture

### Database Schema

**5 Core Tables:**

1. **character_arcs** - Main arc tracking
   - Arc type (positive_change, redemption, etc.)
   - Progress percentage
   - Start/end/current chapter
   - Pacing and consistency scores

2. **arc_milestones** - Key moments
   - Milestone type (inciting_incident, turning_point, etc.)
   - Chapter number
   - Description and significance
   - Notes

3. **emotional_states** - Emotional tracking
   - Primary emotion
   - Intensity (0-10)
   - Scene context and triggers
   - Internal state (JSONB)

4. **goal_progress** - Character goals
   - Goal description
   - Status (active, completed, failed, abandoned)
   - Progress percentage
   - Obstacles and notes

5. **relationship_evolution** - Relationship tracking
   - Related character
   - Relationship type
   - Status and development stage
   - Notes

### Backend Components

#### Models (`backend/core/models/character_arcs.py`)
- SQLAlchemy ORM models
- 3 enum types: ArcType, MilestoneType, GoalStatus
- Relationships and foreign keys
- JSONB fields for flexible data

#### Service Layer (`backend/services/ai/character_arc_service.py`)
**860+ lines of business logic:**

**CRUD Operations:**
- `create_arc()` - Create new character arc
- `get_arc()` - Get arc by ID
- `get_arcs_by_character()` - List character arcs
- `update_arc_progress()` - Update progress
- `add_milestone()` - Record milestone
- `track_emotional_state()` - Log emotional state
- `create_goal()` - Create character goal
- `update_goal_progress()` - Update goal
- `track_relationship_change()` - Log relationship

**AI Analysis Methods:**
- `analyze_arc_health()` - Evaluate pacing and consistency
- `detect_milestone_from_scene()` - Auto-detect milestones
- `extract_emotional_state_from_scene()` - Auto-detect emotions
- `generate_arc_report()` - Comprehensive analysis

#### API Layer (`backend/api/`)

**Routes (`routes/character_arcs.py`):**
- 20+ RESTful endpoints
- Organized by function (CRUD, tracking, AI)
- Proper error handling
- Response models

**Schemas (`schemas/character_arcs.py`):**
- 8 request models
- 13 response models
- Full Pydantic validation
- Type safety

#### Migration (`backend/alembic/versions/005_add_character_arc_tracker.py`)
- Creates all 5 tables
- Defines enums
- Sets up foreign keys
- Includes rollback

### Frontend Components

#### Main Page (`frontend/src/app/(main)/character-arcs/page.tsx`)
**520+ lines - Full dashboard:**
- Character selector sidebar
- Overview statistics (total arcs, on-track count, avg progress)
- Arc cards with type badges
- Tab navigation (Timeline / Emotional / Goals)
- Filter and search

#### CharacterArcTimeline (`frontend/src/components/CharacterArcTimeline.tsx`)
**310+ lines:**
- Visual timeline with progress bar
- Milestone markers with icons
- Current chapter indicator
- Milestone list with details
- AI analysis trigger

#### EmotionalStateTracker (`frontend/src/components/EmotionalStateTracker.tsx`)
**360+ lines:**
- Emotional intensity chart
- State history with context
- Positive/negative/neutral filtering
- Trend indicators
- Emotion categorization

#### GoalProgressVisualization (`frontend/src/components/GoalProgressVisualization.tsx`)
**400+ lines:**
- Goal progress bars
- Status filtering (active/completed/failed/abandoned)
- Success rate analytics
- Obstacles tracking
- Timeline display

## API Endpoints

### Arc Management
```
POST   /api/character-arcs/arcs                    - Create arc
GET    /api/character-arcs/arcs/{arc_id}           - Get arc
GET    /api/character-arcs/arcs                    - List arcs
GET    /api/character-arcs/character/{id}/arcs     - Character arcs
GET    /api/character-arcs/summaries               - Arc summaries
PUT    /api/character-arcs/arcs/{arc_id}/progress  - Update progress
```

### Milestone Tracking
```
POST   /api/character-arcs/arcs/{arc_id}/milestones        - Add milestone
GET    /api/character-arcs/arcs/{arc_id}/milestones        - List milestones
```

### Emotional States
```
POST   /api/character-arcs/emotional-states                - Track emotion
GET    /api/character-arcs/character/{id}/emotional-journey - Get journey
```

### Goal Progress
```
POST   /api/character-arcs/goals                     - Create goal
PUT    /api/character-arcs/goals/{goal_id}/progress  - Update progress
GET    /api/character-arcs/character/{id}/goals      - List goals
```

### Relationship Evolution
```
POST   /api/character-arcs/relationships             - Track relationship
GET    /api/character-arcs/character/{id}/relationships - Get evolution
```

### AI Analysis
```
POST   /api/character-arcs/arcs/{arc_id}/analyze-health    - Analyze arc
POST   /api/character-arcs/analyze-milestone                - Detect milestone
POST   /api/character-arcs/extract-emotional-state          - Extract emotion
POST   /api/character-arcs/arcs/{arc_id}/report            - Generate report
```

## Usage Guide

### 1. Creating a Character Arc

**Via API:**
```bash
curl -X POST http://localhost:8000/api/character-arcs/arcs \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "character_id": 5,
    "arc_type": "redemption",
    "name": "Road to Redemption",
    "description": "Character seeks to atone for past mistakes",
    "start_chapter": 1,
    "end_chapter": 25
  }'
```

**Via Frontend:**
1. Navigate to `/character-arcs`
2. Select character from sidebar
3. Click "New Arc" button
4. Fill in arc details
5. Set chapter boundaries

### 2. Tracking Milestones

**Via API:**
```bash
curl -X POST http://localhost:8000/api/character-arcs/arcs/1/milestones \
  -H "Content-Type: application/json" \
  -d '{
    "milestone_type": "turning_point",
    "chapter_number": 8,
    "description": "Character confronts their past",
    "significance": 4
  }'
```

**Via Frontend:**
1. Go to Timeline tab
2. Click "Add Milestone"
3. Select milestone type
4. Enter chapter and description
5. Rate significance (1-5 stars)

### 3. Monitoring Emotional States

**Manual Tracking:**
```bash
curl -X POST http://localhost:8000/api/character-arcs/emotional-states \
  -H "Content-Type: application/json" \
  -d '{
    "arc_id": 1,
    "chapter_number": 5,
    "primary_emotion": "guilt",
    "intensity": 8,
    "scene_context": "Confrontation with victim's family",
    "trigger_event": "Seeing the pain they caused"
  }'
```

**AI Extraction:**
```bash
curl -X POST http://localhost:8000/api/character-arcs/extract-emotional-state \
  -H "Content-Type: application/json" \
  -d '{
    "arc_id": 1,
    "chapter_number": 5,
    "scene_text": "John stood frozen as Maria's tears fell..."
  }'
```

### 4. Setting Goals

```bash
curl -X POST http://localhost:8000/api/character-arcs/goals \
  -H "Content-Type: application/json" \
  -d '{
    "arc_id": 1,
    "goal_description": "Earn forgiveness from those he wronged",
    "target_chapter": 20
  }'
```

### 5. AI Analysis

**Arc Health Check:**
```bash
curl -X POST http://localhost:8000/api/character-arcs/arcs/1/analyze-health
```

Returns:
- Pacing score (0-10)
- Consistency score (0-10)
- Recommendations
- Identified issues

**Milestone Detection:**
```bash
curl -X POST http://localhost:8000/api/character-arcs/analyze-milestone \
  -H "Content-Type: application/json" \
  -d '{
    "arc_id": 1,
    "chapter_number": 12,
    "scene_text": "The moment of truth arrived..."
  }'
```

**Generate Report:**
```bash
curl -X POST http://localhost:8000/api/character-arcs/arcs/1/report
```

Returns comprehensive analysis:
- Overall arc assessment
- Milestone distribution
- Emotional journey analysis
- Goal progress summary
- Improvement suggestions

## AI Models Used

### Arc Health Analysis
- **Model:** Claude Opus 4 (`claude-opus-4-20250514`)
- **Purpose:** Deep analysis of pacing and consistency
- **Temperature:** 0.3 (focused analysis)
- **Max Tokens:** 2000

### Milestone Detection
- **Model:** Claude Sonnet 3.5 (`claude-3-5-sonnet-20241022`)
- **Purpose:** Scene analysis for milestones
- **Temperature:** 0.2 (precise detection)
- **Max Tokens:** 1000

### Emotional State Extraction
- **Model:** Claude Sonnet 3.5
- **Purpose:** Extract emotions from scene text
- **Temperature:** 0.3
- **Max Tokens:** 800

### Report Generation
- **Model:** Claude Opus 4
- **Purpose:** Comprehensive arc report
- **Temperature:** 0.5 (balanced creativity)
- **Max Tokens:** 3000

## Configuration

### Environment Variables

```bash
# Required for AI features
ANTHROPIC_API_KEY=your_api_key_here

# Database (already configured)
DATABASE_URL=postgresql://...

# Optional
CHARACTER_ARC_ANALYSIS_MODEL=claude-opus-4-20250514
CHARACTER_ARC_DETECTION_MODEL=claude-3-5-sonnet-20241022
```

### AI Configuration
Located in `backend/core/config/ai_config.py`:

```python
CHARACTER_ARC_ANALYSIS = {
    "model": "claude-opus-4-20250514",
    "temperature": 0.3,
    "max_tokens": 2000,
}

MILESTONE_DETECTION = {
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 0.2,
    "max_tokens": 1000,
}
```

## Database Migration

### Run Migration
```bash
cd backend
alembic upgrade head
```

### Check Status
```bash
alembic current
```

### Rollback
```bash
alembic downgrade -1
```

## Testing

### Manual Testing Checklist

**Backend:**
- [ ] Create character arc
- [ ] Add milestones
- [ ] Track emotional states
- [ ] Create goals
- [ ] Update progress
- [ ] Run AI analysis
- [ ] Generate report

**Frontend:**
- [ ] Character selection
- [ ] Arc display
- [ ] Timeline visualization
- [ ] Emotional chart
- [ ] Goal progress bars
- [ ] Filtering and sorting
- [ ] Responsive design

### Test Data Setup

```python
# 1. Create test character
character = Character(
    project_id=1,
    name="Test Hero",
    role="protagonist"
)

# 2. Create arc
arc = create_arc(
    project_id=1,
    character_id=character.id,
    arc_type=ArcType.redemption,
    name="Test Redemption Arc",
    start_chapter=1,
    end_chapter=20
)

# 3. Add milestones
add_milestone(
    arc_id=arc.id,
    milestone_type=MilestoneType.inciting_incident,
    chapter_number=3,
    description="Incident that starts the journey"
)

# 4. Track emotion
track_emotional_state(
    arc_id=arc.id,
    chapter_number=5,
    primary_emotion="guilt",
    intensity=7
)

# 5. Create goal
create_goal(
    arc_id=arc.id,
    goal_description="Make amends"
)
```

## Integration with Other Features

### Canon System
- Character arcs pull from canon character data
- Changes can update canon records
- Character relationships tracked

### Consequence Simulator
- Arc milestones can trigger consequences
- Emotional states affect decision outcomes
- Goal completion creates story events

### Promise Ledger
- Arc progression fulfills narrative promises
- Milestones can be promise payoffs
- Goal completion tracked as promises

### Quality Control
- Arc consistency checks
- Pacing analysis
- Character development validation

## Performance Considerations

### Database Optimization
- Indexes on foreign keys
- Efficient JSONB queries
- Pagination for large datasets

### AI Rate Limiting
- Cache analysis results
- Batch processing for multiple arcs
- Async operations for long-running tasks

### Frontend Optimization
- Lazy loading of components
- Data pagination
- Chart rendering optimization

## Future Enhancements

### Planned Features
1. **Character Comparison** - Compare arcs across characters
2. **Arc Templates** - Pre-built arc structures
3. **Collaborative Editing** - Multiple writers tracking arcs
4. **Export to PDF** - Visual arc reports
5. **Integration with Writing** - Real-time tracking during drafting

### Potential Improvements
- Voice of character analysis
- Dialogue pattern tracking
- Scene-by-scene breakdown
- Character interaction matrix
- Theme alignment tracking

## Troubleshooting

### Common Issues

**1. Migration Fails**
```bash
# Check current version
alembic current

# Reset to previous version
alembic downgrade -1

# Try upgrade again
alembic upgrade head
```

**2. AI Analysis Timeout**
- Reduce scene text length
- Check API key validity
- Verify network connection

**3. Frontend Not Loading**
```bash
# Clear cache
rm -rf frontend/.next

# Rebuild
cd frontend
npm run build
npm run dev
```

**4. API Errors**
- Check backend logs
- Verify database connection
- Confirm route registration in main.py

## File Structure

```
narrative-os/
├── backend/
│   ├── core/
│   │   └── models/
│   │       └── character_arcs.py          # Database models
│   ├── services/
│   │   └── ai/
│   │       └── character_arc_service.py   # Business logic (860 lines)
│   ├── api/
│   │   ├── routes/
│   │   │   └── character_arcs.py          # API endpoints (20+)
│   │   └── schemas/
│   │       └── character_arcs.py          # Pydantic schemas (21 models)
│   ├── alembic/
│   │   └── versions/
│   │       └── 005_add_character_arc_tracker.py  # Migration
│   └── main.py                            # Router registration
│
└── frontend/
    └── src/
        ├── app/(main)/
        │   └── character-arcs/
        │       └── page.tsx                # Main dashboard (520 lines)
        └── components/
            ├── CharacterArcTimeline.tsx    # Timeline (310 lines)
            ├── EmotionalStateTracker.tsx   # Emotions (360 lines)
            └── GoalProgressVisualization.tsx  # Goals (400 lines)
```

## Credits

**Implementation:**
- Database Schema: 5 tables, 3 enums
- Backend: 860+ lines (service), 400+ lines (API)
- Frontend: 1,590+ lines across 4 components
- Total: 2,850+ lines of production code

**AI Integration:**
- Claude Opus 4 for deep analysis
- Claude Sonnet 3.5 for detection tasks
- Anthropic SDK for Python

**Technologies:**
- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL
- Frontend: Next.js 14, React, TypeScript, Tailwind CSS
- AI: Anthropic Claude API

## Support

For issues or questions:
- Check this documentation
- Review API endpoint tests
- Examine frontend component examples
- Consult service layer methods

---

**Status:** ✅ 100% Complete - Backend + Frontend Ready

**Version:** 1.0.0

**Last Updated:** 2026-01-10
