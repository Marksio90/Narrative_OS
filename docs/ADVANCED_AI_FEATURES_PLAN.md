# Advanced AI Features - Implementation Plan

**Date:** 2026-01-09
**Timeline:** 2-3 weeks
**Goal:** Implement unique AI features that competitors don't have

---

## 🎯 Overview

Three game-changing features that differentiate Narrative OS:

1. **Character Voice Fingerprinting** - Ensures dialogue consistency across 100k+ word novels
2. **Consequence Simulator** - Tracks how decisions ripple through the story
3. **Writers' Room Mode** - Interactive multi-agent feedback UI

---

## 🎭 Feature 1: Character Voice Fingerprinting

### What It Does
Analyzes a character's dialogue patterns and creates a unique "voice fingerprint" that ensures consistency throughout the novel.

### User Value
- **Problem:** Authors struggle to maintain consistent character voice across 300+ pages
- **Solution:** AI analyzes existing dialogue and scores new dialogue for consistency
- **Result:** Characters sound like themselves from chapter 1 to chapter 50

### Technical Architecture

#### Backend Components

**1. Voice Fingerprint Service** (`backend/services/ai/voice_fingerprint.py`)
```python
class VoiceFingerprint:
    """Linguistic fingerprint for a character"""
    character_id: int
    vocabulary_stats: Dict[str, Any]  # Word frequency, rarity scores
    sentence_patterns: Dict[str, Any]  # Length, complexity, structure
    linguistic_markers: List[str]     # Catchphrases, quirks, filler words
    emotional_range: Dict[str, float] # Emotion distribution
    formality_score: float            # 0-1 (casual to formal)
    consistency_baseline: float       # Self-consistency score

class VoiceFingerprintService:
    async def analyze_dialogue(
        self,
        character_id: int,
        dialogue_samples: List[str]
    ) -> VoiceFingerprint

    async def score_consistency(
        self,
        fingerprint: VoiceFingerprint,
        new_dialogue: str
    ) -> ConsistencyScore

    async def suggest_improvements(
        self,
        fingerprint: VoiceFingerprint,
        problematic_dialogue: str
    ) -> List[str]  # Suggested alternatives
```

**2. Dialogue Extraction Engine**
```python
class DialogueExtractor:
    """Extract and attribute dialogue from prose"""

    async def extract_from_scene(
        self,
        prose: str,
        character_mapping: Dict[str, int]
    ) -> List[DialogueLine]

    async def build_corpus(
        self,
        project_id: int,
        character_id: int,
        db: Session
    ) -> List[str]  # All dialogue for this character
```

**3. Linguistic Analysis**
```python
class LinguisticAnalyzer:
    """Deep linguistic pattern analysis"""

    def analyze_vocabulary(self, text: str) -> VocabularyProfile
    def analyze_syntax(self, text: str) -> SyntaxProfile
    def detect_quirks(self, samples: List[str]) -> List[LinguisticQuirk]
    def measure_formality(self, text: str) -> float
    def detect_emotion(self, text: str) -> Dict[str, float]
```

#### Frontend Components

**1. Voice Fingerprint Panel** (Story Bible → Character Details)
```tsx
<VoiceFingerprintPanel>
  <AnalysisButton>Analyze Character Voice</AnalysisButton>

  <FingerprintVisualization>
    <VocabularyChart />      {/* Word rarity distribution */}
    <SentencePatternChart /> {/* Avg length, complexity */}
    <QuirksList />           {/* Detected catchphrases */}
    <EmotionalRangeChart />  {/* Emotion distribution */}
    <FormalityMeter />       {/* Visual gauge */}
  </FingerprintVisualization>

  <ConsistencyHistory>
    {/* Recent scenes with consistency scores */}
    <SceneConsistencyCard scene="Chapter 5" score={0.87} />
    <SceneConsistencyCard scene="Chapter 8" score={0.92} />
  </ConsistencyHistory>
</VoiceFingerprintPanel>
```

**2. Live Consistency Checker** (AI Studio)
```tsx
<DialogueConsistencyAlert>
  <WarningIcon />
  <Message>
    This dialogue doesn't match Sarah's voice pattern (Score: 0.45)

    <Issues>
      - Too formal (she uses casual language)
      - Missing her signature "you know" filler
      - Vocabulary too complex (avg word length: 6.2 vs her 4.1)
    </Issues>

    <Suggestions>
      "I'm, like, totally overwhelmed by this, you know?"
      "This is way too much for me right now, honestly."
    </Suggestions>
  </Message>
</DialogueConsistencyAlert>
```

### Implementation Steps

**Week 1: Voice Fingerprinting**
- [ ] Day 1: Dialogue extraction engine
- [ ] Day 2: Linguistic analysis (vocabulary, syntax)
- [ ] Day 3: Voice fingerprint data model + database schema
- [ ] Day 4: Voice fingerprint service (analysis + scoring)
- [ ] Day 5: Frontend UI (Story Bible panel)
- [ ] Day 6: Live consistency checker in AI Studio
- [ ] Day 7: Testing + refinement

### Database Schema
```sql
CREATE TABLE character_voice_fingerprints (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id) ON DELETE CASCADE,
    vocabulary_profile JSONB,      -- Word frequency, rarity
    syntax_profile JSONB,           -- Sentence patterns
    linguistic_markers JSONB,       -- Quirks, catchphrases
    emotional_baseline JSONB,       -- Emotion distribution
    formality_score FLOAT,
    sample_count INTEGER,           -- How many dialogue samples
    last_analyzed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE dialogue_consistency_scores (
    id SERIAL PRIMARY KEY,
    scene_id INTEGER REFERENCES scenes(id) ON DELETE CASCADE,
    character_id INTEGER REFERENCES characters(id) ON DELETE CASCADE,
    fingerprint_id INTEGER REFERENCES character_voice_fingerprints(id),
    consistency_score FLOAT,        -- 0-1
    issues JSONB,                   -- Array of problems detected
    suggestions JSONB,              -- Array of improvements
    created_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints
```python
POST /api/canon/character/{id}/analyze-voice
  → Analyzes all dialogue for character, creates fingerprint

GET /api/canon/character/{id}/voice-fingerprint
  → Returns current fingerprint

POST /api/ai/check-dialogue-consistency
  Body: { character_id, dialogue, fingerprint_id }
  → Returns consistency score + suggestions

GET /api/canon/character/{id}/consistency-history
  → Returns recent consistency scores by scene
```

---

## ⚡ Feature 2: Consequence Simulator

### What It Does
Tracks how character decisions and story events ripple through the narrative, creating a "consequence graph" that helps maintain logical story progression.

### User Value
- **Problem:** Authors forget consequences of earlier events, creating plot holes
- **Solution:** AI tracks decisions and propagates their effects
- **Result:** Logically consistent stories where actions have lasting impact

### Technical Architecture

#### Backend Components

**1. Consequence Engine** (`backend/services/ai/consequence_engine.py`)
```python
@dataclass
class StoryEvent:
    """A significant event or decision"""
    id: int
    scene_id: int
    description: str
    event_type: str  # decision, revelation, conflict, resolution
    affected_entities: List[int]  # Characters, locations, threads
    magnitude: float  # 0-1, how impactful
    timestamp: datetime

@dataclass
class Consequence:
    """A consequence of an event"""
    id: int
    source_event_id: int
    target_event_id: Optional[int]  # If consequence is realized
    description: str
    affected_entities: List[int]
    probability: float  # 0-1, how likely
    timeframe: str  # immediate, short_term, long_term
    status: str  # potential, active, resolved, invalidated

class ConsequenceEngine:
    """Simulates and tracks story consequences"""

    async def analyze_scene_for_events(
        self,
        scene: Scene,
        db: Session
    ) -> List[StoryEvent]:
        """Extract significant events from a scene"""

    async def predict_consequences(
        self,
        event: StoryEvent,
        story_context: Dict[str, Any],
        db: Session
    ) -> List[Consequence]:
        """Use AI to predict likely consequences"""

    async def track_consequence_realization(
        self,
        consequence: Consequence,
        new_scene: Scene
    ) -> bool:
        """Check if a predicted consequence occurred"""

    async def build_consequence_graph(
        self,
        project_id: int,
        db: Session
    ) -> ConsequenceGraph:
        """Build complete event → consequence graph"""
```

**2. Consequence Validator**
```python
class ConsequenceValidator:
    """Validates that scenes respect established consequences"""

    async def validate_scene(
        self,
        scene: Scene,
        active_consequences: List[Consequence]
    ) -> ValidationResult:
        """Check if scene contradicts active consequences"""

    async def suggest_consequence_inclusion(
        self,
        scene_description: str,
        active_consequences: List[Consequence]
    ) -> List[str]:
        """Suggest consequences to weave into scene"""
```

#### Frontend Components

**1. Consequence Graph Visualization** (New page: `/consequences`)
```tsx
<ConsequenceGraphPage>
  <FilterPanel>
    <CharacterFilter />
    <ChapterRangeFilter />
    <EventTypeFilter />
  </FilterPanel>

  <GraphVisualization>
    {/* Interactive node graph */}
    <EventNode id="evt_1">
      Sarah discovers magic crystal
      → 3 consequences
    </EventNode>

    <ConsequenceEdge probability={0.8}>
      Crystal attracts dark forces
    </ConsequenceEdge>

    <EventNode id="evt_5">
      Dark forces attack village
      (Consequence realized ✓)
    </EventNode>
  </GraphVisualization>

  <ConsequenceTimeline>
    {/* Linear view of consequences over chapters */}
  </ConsequenceTimeline>
</ConsequenceGraphPage>
```

**2. Active Consequences Panel** (AI Studio)
```tsx
<ActiveConsequencesPanel>
  <Title>Active Consequences to Consider</Title>

  <ConsequenceCard probability={0.9} timeframe="immediate">
    Sarah's lie to Marcus will create trust issues
    <Badge>Chapter 3</Badge>

    <SuggestionButton>
      Weave into current scene
    </SuggestionButton>
  </ConsequenceCard>

  <ConsequenceCard probability={0.7} timeframe="long_term">
    Stolen artifact will be discovered missing
    <Badge>Chapter 2</Badge>
  </ConsequenceCard>
</ActiveConsequencesPanel>
```

### Implementation Steps

**Week 2: Consequence Simulator**
- [ ] Day 1: Event extraction from scenes (AI-powered)
- [ ] Day 2: Consequence prediction engine
- [ ] Day 3: Database schema + consequence tracking
- [ ] Day 4: Consequence graph builder
- [ ] Day 5: Frontend graph visualization (React Flow)
- [ ] Day 6: Active consequences panel in AI Studio
- [ ] Day 7: Validation + testing

### Database Schema
```sql
CREATE TABLE story_events (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    scene_id INTEGER REFERENCES scenes(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    event_type VARCHAR(50),  -- decision, revelation, conflict, etc.
    magnitude FLOAT,          -- Impact score 0-1
    extracted_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE event_entities (
    event_id INTEGER REFERENCES story_events(id) ON DELETE CASCADE,
    entity_type VARCHAR(50),  -- character, location, thread
    entity_id INTEGER,
    PRIMARY KEY (event_id, entity_type, entity_id)
);

CREATE TABLE consequences (
    id SERIAL PRIMARY KEY,
    source_event_id INTEGER REFERENCES story_events(id) ON DELETE CASCADE,
    target_event_id INTEGER REFERENCES story_events(id) ON DELETE SET NULL,
    description TEXT NOT NULL,
    probability FLOAT,        -- 0-1
    timeframe VARCHAR(50),    -- immediate, short_term, long_term
    status VARCHAR(50),       -- potential, active, resolved, invalidated
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);
```

### API Endpoints
```python
POST /api/consequences/analyze-scene
  Body: { scene_id }
  → Extracts events, predicts consequences

GET /api/consequences/active
  Query: { project_id, chapter_id? }
  → Returns active consequences for context

GET /api/consequences/graph
  Query: { project_id }
  → Returns full consequence graph

POST /api/consequences/{id}/mark-resolved
  Body: { scene_id }
  → Marks consequence as realized
```

---

## 🎬 Feature 3: Writers' Room Mode

### What It Does
Shows feedback from all AI agents simultaneously in an interactive "writers' room" interface, letting authors see different perspectives and choose which feedback to apply.

### User Value
- **Problem:** Current AI generation is a black box
- **Solution:** Transparent multi-agent feedback with agent personalities
- **Result:** Authors understand *why* AI makes choices and can guide the process

### Technical Architecture

#### Backend Components

**1. Writers' Room Orchestrator** (`backend/services/ai/writers_room.py`)
```python
@dataclass
class AgentFeedback:
    """Feedback from a single agent"""
    agent_name: str
    agent_role: str
    feedback_type: str  # critique, suggestion, approval, concern
    content: str
    severity: str  # info, warning, critical
    specific_issue: Optional[str]
    suggested_fix: Optional[str]
    confidence: float  # 0-1

class WritersRoomSession:
    """An interactive writers' room session"""
    session_id: str
    scene_description: str
    current_draft: str
    agent_feedbacks: List[AgentFeedback]
    consensus_score: float  # Agreement between agents
    iteration: int

class WritersRoomOrchestrator:
    """Manages interactive multi-agent collaboration"""

    async def start_session(
        self,
        scene_description: str,
        story_context: Dict[str, Any]
    ) -> WritersRoomSession:
        """Initialize writers' room session"""

    async def get_all_feedback(
        self,
        session: WritersRoomSession
    ) -> List[AgentFeedback]:
        """Get feedback from all agents in parallel"""

    async def apply_selected_feedback(
        self,
        session: WritersRoomSession,
        selected_feedback_ids: List[str]
    ) -> str:
        """Revise draft based on selected feedback"""

    async def poll_agents(
        self,
        question: str,
        current_draft: str,
        agents: List[str]
    ) -> Dict[str, str]:
        """Ask specific question to selected agents"""
```

**2. Agent Persona Definitions**
```python
AGENT_PERSONAS = {
    "planner": {
        "name": "Alex (Story Architect)",
        "avatar": "🏗️",
        "personality": "Analytical, big-picture thinker",
        "concerns": ["pacing", "structure", "plot logic"],
        "typical_feedback": [
            "This scene needs a clearer turning point",
            "Consider what this reveals about character motivation"
        ]
    },
    "writer": {
        "name": "Blake (Prose Master)",
        "avatar": "✍️",
        "personality": "Creative, passionate about craft",
        "concerns": ["show vs tell", "sensory details", "voice"],
        "typical_feedback": [
            "Too much telling here - show the emotion through action",
            "This dialogue feels flat - add subtext"
        ]
    },
    "critic": {
        "name": "Casey (Story Critic)",
        "avatar": "🔍",
        "personality": "Sharp, constructive but honest",
        "concerns": ["weaknesses", "clichés", "emotional impact"],
        "typical_feedback": [
            "This revelation falls flat - build more tension first",
            "The dialogue feels clichéd"
        ]
    },
    "editor": {
        "name": "Dana (Line Editor)",
        "avatar": "📝",
        "personality": "Meticulous, focused on craft",
        "concerns": ["word choice", "flow", "clarity"],
        "typical_feedback": [
            "This sentence is too long - break it up",
            "Consider a stronger verb here"
        ]
    },
    "canon_keeper": {
        "name": "Ellis (Canon Guardian)",
        "avatar": "📚",
        "personality": "Detail-oriented, protective of consistency",
        "concerns": ["continuity", "character consistency", "world rules"],
        "typical_feedback": [
            "Sarah wouldn't say this - too formal for her voice",
            "This contradicts the magic rules from Chapter 2"
        ]
    }
}
```

#### Frontend Components

**1. Writers' Room Page** (`/writers-room`)
```tsx
<WritersRoomPage>
  <TopBar>
    <SessionInfo>
      Scene: "Sarah discovers the truth"
      Iteration: 3
      Consensus: 78%
    </SessionInfo>
  </TopBar>

  <MainLayout>
    <LeftPanel width="40%">
      <DraftEditor>
        <TextArea value={currentDraft} onChange={...} />

        <InlineAnnotations>
          {/* Highlight issues inline */}
          <Issue agent="critic" line={5}>
            Weak verb choice
          </Issue>
        </InlineAnnotations>
      </DraftEditor>
    </LeftPanel>

    <RightPanel width="60%">
      <AgentFeedbackGrid>
        {agents.map(agent => (
          <AgentCard key={agent.name}>
            <Header>
              <Avatar>{agent.avatar}</Avatar>
              <Name>{agent.name}</Name>
              <Role>{agent.role}</Role>
            </Header>

            <FeedbackList>
              {agent.feedback.map(fb => (
                <FeedbackItem
                  type={fb.type}
                  severity={fb.severity}
                >
                  <Checkbox onChange={selectFeedback} />
                  <Content>{fb.content}</Content>

                  {fb.suggested_fix && (
                    <SuggestedFix>
                      {fb.suggested_fix}
                    </SuggestedFix>
                  )}
                </FeedbackItem>
              ))}
            </FeedbackList>

            <AskAgentButton>
              Ask {agent.name} a question
            </AskAgentButton>
          </AgentCard>
        ))}
      </AgentFeedbackGrid>
    </RightPanel>
  </MainLayout>

  <BottomBar>
    <ApplySelectedButton>
      Apply Selected Feedback (5 selected)
    </ApplySelectedButton>

    <RegenerateButton>
      Regenerate with Feedback
    </RegenerateButton>

    <ConsensusIndicator score={0.78}>
      Agents mostly agree (78%)
    </ConsensusIndicator>
  </BottomBar>
</WritersRoomPage>
```

**2. Consensus Visualization**
```tsx
<ConsensusVisualization>
  <AgentAgreementMatrix>
    {/* Shows which agents agree/disagree */}
    <Cell agent1="planner" agent2="writer" agreement={0.85} />
    <Cell agent1="critic" agent2="editor" agreement={0.92} />
    <Cell agent1="planner" agent2="critic" agreement={0.45} />
  </AgentAgreementMatrix>

  <ConflictAlert>
    ⚠️ Alex and Casey disagree about pacing

    Alex: "This scene needs more buildup"
    Casey: "Get to the revelation faster"

    <ResolveButton>Help me decide</ResolveButton>
  </ConflictAlert>
</ConsensusVisualization>
```

### Implementation Steps

**Week 3: Writers' Room Mode**
- [ ] Day 1: Writers' room orchestrator backend
- [ ] Day 2: Parallel agent feedback collection
- [ ] Day 3: Agent persona system + feedback categorization
- [ ] Day 4: Frontend page layout + agent cards
- [ ] Day 5: Interactive feedback selection + draft editing
- [ ] Day 6: Consensus visualization + conflict resolution
- [ ] Day 7: Polish + testing

### Database Schema
```sql
CREATE TABLE writers_room_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    scene_description TEXT,
    current_draft TEXT,
    iteration INTEGER DEFAULT 1,
    consensus_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE agent_feedback (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES writers_room_sessions(id) ON DELETE CASCADE,
    agent_name VARCHAR(50),
    agent_role VARCHAR(50),
    feedback_type VARCHAR(50),
    content TEXT,
    severity VARCHAR(20),
    specific_issue TEXT,
    suggested_fix TEXT,
    confidence FLOAT,
    is_applied BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints
```python
POST /api/writers-room/start-session
  Body: { scene_description, story_context }
  → Returns session_id + initial draft

GET /api/writers-room/session/{session_id}/feedback
  → Returns all agent feedback for current draft

POST /api/writers-room/session/{session_id}/apply-feedback
  Body: { feedback_ids: [1, 3, 5] }
  → Revises draft based on selected feedback

POST /api/writers-room/session/{session_id}/ask-agent
  Body: { agent_name, question }
  → Returns specific agent's response

GET /api/writers-room/session/{session_id}/consensus
  → Returns consensus metrics + disagreements
```

---

## 📊 Success Metrics

### Feature 1: Voice Fingerprinting
- **Accuracy:** 85%+ consistency detection rate
- **Performance:** Fingerprint analysis <30s for 50+ dialogue samples
- **User Value:** 90%+ consistency scores for experienced authors

### Feature 2: Consequence Simulator
- **Coverage:** Detect 80%+ of significant story events
- **Prediction Quality:** 70%+ of predicted consequences are plausible
- **Plot Hole Prevention:** Reduce continuity errors by 60%+

### Feature 3: Writers' Room Mode
- **Engagement:** 40%+ of users try writers' room
- **Retention:** 25%+ use it regularly
- **Quality:** 85%+ user satisfaction with transparency

---

## 🚀 Implementation Priority

**Week 1:** Character Voice Fingerprinting (Highest ROI)
- Most unique feature
- Immediate user value
- Builds on existing voice_profile data

**Week 2:** Consequence Simulator (Strategic Value)
- Solves real author pain point (plot holes)
- Creates vendor lock-in (valuable graph data)
- Differentiates from all competitors

**Week 3:** Writers' Room Mode (Polish & UX)
- Makes AI generation transparent
- Great marketing/demo material
- Builds trust with users

---

## 🎯 Next Actions

1. Review and approve this plan
2. Set up feature flags for gradual rollout
3. Create database migrations for new tables
4. Begin Week 1: Voice Fingerprinting implementation
5. Design UI mockups for all three features
6. Prepare marketing materials highlighting these features

---

**Built with precision. Designed for authors. Unlike anything else on the market.** 🚀✨
