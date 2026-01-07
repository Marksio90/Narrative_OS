# 🎨 **NARRATIVE OS - Kompletny Przewodnik Użytkownika**

## 📋 **Spis Treści**

1. [Czym jest Narrative OS?](#czym-jest-narrative-os)
2. [Architektura Systemu](#architektura-systemu)
3. [Desktop Environment](#desktop-environment)
4. [Story Bible](#story-bible)
5. [AI Features](#ai-features)
6. [Export/Import](#exportimport)
7. [Relationships Graph](#relationships-graph)
8. [Backend API](#backend-api)
9. [Przepływ Pracy](#przepływ-pracy)
10. [Skróty Klawiszowe](#skróty-klawiszowe)

---

## 🎯 **Czym jest Narrative OS?**

**Narrative OS** to pełnowymiarowy **system operacyjny dla pisarzy**, który zamienia proces pisania powieści w zorganizowany, AI-wspomagany workflow.

### **Kluczowe Komponenty:**

```
┌─────────────────────────────────────────┐
│         NARRATIVE OS v2.0               │
├─────────────────────────────────────────┤
│  🖥️  Desktop Environment               │
│  📖  Story Bible (Canon Management)     │
│  🤖  AI Copilot & Tools                 │
│  📊  Analytics & Insights               │
│  🕸️  Relationships Graph                │
│  📦  Export/Import System               │
│  ✍️  Writing Studio (Coming Soon)       │
└─────────────────────────────────────────┘
```

---

## 🏗️ **Architektura Systemu**

### **Tech Stack:**

#### **Frontend:**
- **Next.js 14** - App Router (Server + Client Components)
- **React 18** - UI z hooks (useState, useEffect)
- **TypeScript** - Type-safe development
- **TailwindCSS** - Utility-first styling
- **Lucide React** - Icon library
- **NextAuth.js** - Authentication

#### **Backend:**
- **FastAPI** - Modern Python API framework
- **SQLAlchemy** - ORM dla bazy danych
- **Pydantic** - Request/Response validation
- **PostgreSQL** - Main database
- **FastAPI-Users** - Auth & permissions

#### **AI Integration:**
- **OpenAI GPT-4** - Text generation
- **Claude Opus 4** - Premium quality
- **RAG Engine** - Canon-aware AI
- **Multi-Agent System** - Planner, Writer, Critic, Editor

---

## 🖥️ **Desktop Environment**

**Route:** `/desktop`

### **Co to jest?**

Desktop to **centralny hub** Narrative OS - Twój command center dla pisania.

### **Komponenty Desktop:**

#### **1. Stats Cards** (4 gradient widgets)

```typescript
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   🌟 DZIŚ    │   🔥 PASSA   │   🎯 POSTĘP  │  ✅ GOTOWE   │
│              │              │              │              │
│  1,250 słów │   12 dni     │    45%       │ 8 rozdziałów │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

**Stats pochodzą z:**
- `today_words` - Dzisiejsze słowa (tracking sesji)
- `streak_days` - Passa pisania (🔥 fire streak!)
- `progress_percent` - % completion projektu
- `chapters_completed` - Ukończone rozdziały

#### **2. Quick Start Widget**

4 duże przyciski do najczęstszych akcji:

```typescript
┌─────────────┬─────────────┐
│ ✍️ Nowy     │ 📖 Biblia   │
│ Rozdział    │ Fabuły      │
├─────────────┼─────────────┤
│ 🤖 AI       │ 📊 Stats    │
│ Asystent    │             │
└─────────────┴─────────────┘
```

#### **3. Recent Activity Feed**

Timeline ostatnich działań:

```
🟢 Dodano postać "Elara" - 2h temu
🔵 Ukończono rozdział 8 - 5h temu
🟣 AI sprawdził spójność - wczoraj
🟠 Eksport biblii fabuły - 2 dni temu
```

**Activity Types:**
- `character_added` - Nowa postać
- `chapter_completed` - Ukończony rozdział
- `ai_consistency_check` - Sprawdzenie AI
- `canon_export` - Eksport danych

#### **4. Weekly Activity Chart**

Bar graph pokazujący produktywność:

```
  │
  │     ▄▄
  │  ▄▄ ██ ▄▄
  │  ██ ██ ██ ▄▄
  │  ██ ██ ██ ██ ▄▄
  └──────────────────
    Mo Tu We Th Fr Sa Su
```

#### **5. Quick Actions Modal** (Ctrl+K)

Spotlight-like search:

```
┌─────────────────────────────────────┐
│ Szukaj akcji, rozdziałów...         │
├─────────────────────────────────────┤
│ 📄 Nowy Rozdział           Ctrl+N   │
│ 📖 Biblia Fabuły           Ctrl+B   │
│ 🤖 AI Asystent             Ctrl+K   │
│ 📊 Statystyki              Ctrl+A   │
│ 🕸️ Graf Relacji            Ctrl+R   │
│ ⏰ Oś Czasu                Ctrl+T   │
└─────────────────────────────────────┘
```

### **Backend API dla Desktop:**

```python
# Główny endpoint
GET /api/desktop/dashboard
Response: DashboardResponse {
  stats: WritingStats
  projects: List[ProjectSummary]
  recent_activity: List[RecentActivity]
  daily_activity: List[DailyActivity]
  quick_actions: List[QuickAction]
}

# Tracking sesji pisania
POST /api/desktop/track-session
Body: {
  words_written: 1250,
  minutes_spent: 45,
  chapter_id: 8
}
Response: {
  success: true,
  new_streak: 12
}
```

---

## 📖 **Story Bible**

**Route:** `/story-bible`

### **Co to jest?**

Story Bible to **kompletny system zarządzania kanonem** - Twoja baza wiedzy o świecie, postaciach, regułach.

### **5 Głównych Tabów:**

#### **1. 👥 Postacie (Characters)**

**Pola:**
- `name` - Imię postaci
- `role` - Rola (protagonist, antagonist, mentor, etc.)
- `goals` - Cele postaci
- `values` - Wartości
- `fears` - Lęki
- `secrets` - Sekrety
- `behavioral_limits` - **HARD LIMITS** - czego NIE może zrobić
- `behavioral_patterns` - Wzorce zachowań
- `voice_profile` - Profil głosu (vocabulary, sentence structure)
- `relationships` - Relacje z innymi (dla grafu)
- `arc` - Rozwój postaci (starting_state → goal_state)

**API:**
```python
POST   /api/canon/character      # Create
GET    /api/canon/character/:id  # Read
GET    /api/canon/character?project_id=1  # List
PUT    /api/canon/character/:id  # Update
DELETE /api/canon/character/:id  # Delete
```

#### **2. 🗺️ Lokacje (Locations)**

**Pola:**
- `name` - Nazwa lokacji
- `geography` - Geografia (góry, lasy, miasta)
- `climate` - Klimat
- `social_rules` - **Zasady społeczne** (obowiązkowe)
- `power_structure` - Struktura władzy
- `restrictions` - **Restrykcje** (kto może wejść, kiedy)
- `access_control` - Kontrola dostępu
- `atmosphere` - Atmosfera (mroczna, przyjazna)
- `connected_to` - Połączone lokacje

**Przykład:**
```json
{
  "name": "Mroczna Forteca",
  "social_rules": [
    "Zakazane wypowiadanie imienia Króla",
    "Magia tylko w wyznaczonych strefach"
  ],
  "restrictions": [
    "Wejście tylko za dnia",
    "Cudzoziemcy potrzebują pozwolenia"
  ],
  "power_structure": {
    "ruler": "Lord Vex",
    "council": ["Rada Magów", "Gildia Wojowników"]
  }
}
```

#### **3. ✨ Wątki Fabularne (Plot Threads)**

**Pola:**
- `thread_type` - Typ (main, subplot, character_arc, mystery, romance)
- `start_chapter` / `end_chapter` - Zasięg
- `status` - Status (active, resolved, abandoned)
- `tension_level` - Poziom napięcia (0-100)
- `stakes` - Stawka
- `deadline` - Deadline (rozdział)
- `milestones` - Kamienie milowe
- `related_characters` - Powiązane postacie
- `related_promises` - Powiązane obietnice

**Wykorzystanie:**
```
Thread: "Poszukiwanie Artefaktu"
├─ Start: Rozdział 3
├─ End: Rozdział 15
├─ Tension: 75/100
├─ Milestones:
│  ├─ Ch 3: Odkrycie mapy
│  ├─ Ch 7: Pierwsza wskazówka
│  ├─ Ch 12: Znalezienie lokacji
│  └─ Ch 15: Zdobycie artefaktu
└─ Related: Elara, Marcus, Lord Vex
```

#### **4. 🪄 Magia i Zasady (Magic & Rules)**

**Pola:**
- `rule_type` - Typ (magic, physics, divine, curse, technology, psychic)
- `laws` - **Prawa** (ZAWSZE obowiązują)
- `costs` - **Koszty** (co trzeba zapłacić)
- `limitations` - **Ograniczenia** (czego NIE MOŻNA)
- `exceptions` - Wyjątki (RZADKIE przypadki)
- `prohibitions` - **Zakazy** (BEZWZGLĘDNE)
- `mechanics` - Jak to działa
- `manifestation` - Jak wygląda/brzmi

**Przykład Hard Magic System:**
```json
{
  "name": "Magia Krwi",
  "rule_type": "magic",
  "laws": [
    "Każde zaklęcie wymaga krwi",
    "Moc proporcjonalna do ilości krwi",
    "Nie można użyć cudzej krwi bez zgody"
  ],
  "costs": [
    "Utrata krwi = osłabienie",
    "Zbyt wiele krwi = śmierć",
    "Każde zaklęcie skraca życie o 1 dzień"
  ],
  "limitations": [
    "Nie można wskrzeszać umarłych",
    "Nie można kontrolować umysłów",
    "Maksymalnie 3 zaklęcia dziennie"
  ],
  "prohibitions": [
    "Magia na dzieciach",
    "Rytuały ofiarnicze"
  ]
}
```

**Dlaczego to ważne?**
- AI używa tego do **consistency checking**
- Zapobiega plot holes
- Zapewnia spójność worldbuildingu

#### **5. ⏰ Oś Czasu (Timeline)**

**Pola:**
- `event_type` - Typ (plot, backstory, world, character)
- `chapter_number` / `scene_number` - Kiedy
- `relative_time` - Czas względny ("3 dni przed Rozdziałem 1")
- `participants` - Uczestnicy
- `location` - Gdzie
- `causes` / `effects` - Przyczynowość (Event IDs)
- `consequences` - Konsekwencje
- `impact_level` - Wpływ (0-100)

**Przykład Timeline:**
```
⏪ BACKSTORY: Wielki Kataklizm (500 lat temu)
    ↓ causes
🌍 WORLD: Powstanie Mrocznej Fortecy (490 lat temu)
    ↓ causes
👤 CHARACTER: Narodziny Elary (18 lat temu)
    ↓ causes
📖 PLOT: Odkrycie mocy (Rozdział 1)
    ↓ causes
📖 PLOT: Bitwa o Cytadelę (Rozdział 8)
```

---

## 🤖 **AI Features**

**Route:** AI Tools modal (button w Story Bible)

### **1. Sprawdzanie Spójności (Consistency Checker)**

**Endpoint:**
```python
POST /projects/{id}/ai/check-consistency
Body: {
  text: "Tekst do sprawdzenia...",
  chapter_number: 8,
  check_character_voice: true,
  check_worldbuilding: true,
  check_plot_continuity: true
}
```

**Co sprawdza?**

#### **Character Canon:**
```python
# AI porównuje tekst z kanonem postaci
if "Elara użyła magii krwi na dziecku":
  # CRITICAL: behavioral_limits violation!
  issue = {
    "type": "character",
    "severity": "critical",
    "description": "Elara NIE MOŻE używać magii na dzieciach",
    "text_excerpt": "Elara użyła magii krwi na dziecku",
    "canon_reference": "behavioral_limits: 'Nigdy nie skrzywdzi dziecka'",
    "suggestion": "Zmień cel zaklęcia na dorosłą postać"
  }
```

#### **Worldbuilding Canon:**
```python
# AI sprawdza zasady świata
if "W Mrocznej Fortecy wypowiedziano imię Króla":
  # WARNING: social_rules violation
  issue = {
    "type": "worldbuilding",
    "severity": "warning",
    "description": "W Mrocznej Fortecy zakazane jest wypowiadanie imienia Króla",
    "canon_reference": "social_rules: ['Zakazane wypowiadanie imienia Króla']"
  }
```

#### **Plot Continuity:**
```python
# AI sprawdza obietnice i wątki
if promise.status == "unfulfilled" and current_chapter > promise.deadline:
  issue = {
    "type": "promise",
    "severity": "critical",
    "description": "Obietnica nie spełniona przed deadline",
    "suggestion": "Dodaj scenę spełniającą obietnicę lub przesuń deadline"
  }
```

**Response:**
```json
{
  "overall_score": 92,
  "critical_count": 1,
  "warning_count": 3,
  "suggestion_count": 5,
  "summary": "Wykryto 1 krytyczny problem ze spójnością postaci...",
  "issues": [...]
}
```

### **2. Sugestie AI (AI Suggestions)**

**Endpoint:**
```python
POST /projects/{id}/ai/suggest
Body: {
  text: "Tekst do analizy...",
  focus_areas: ["pacing", "dialogue", "description", "emotion"]
}
```

**Kategorie Sugestii:**

#### **Pacing:**
```json
{
  "category": "pacing",
  "priority": "high",
  "suggestion": "Scena dialogu jest za długa - przyspiesz tempo",
  "rationale": "10 wymian replik bez akcji - czytelnik może się nudzić",
  "example": "Przerwij dialog akcją: 'Sarah sięgnęła po broń podczas gdy Marcus mówił'"
}
```

#### **Dialogue:**
```json
{
  "category": "dialogue",
  "priority": "medium",
  "suggestion": "Voice postaci Marcus nie pasuje do kanonu",
  "rationale": "Marcus używa skomplikowanych słów, ale w kanonie ma 'simple vocabulary'",
  "example": "Zamiast 'to niezwykle enigmatyczne' użyj 'to dziwne'"
}
```

#### **Show vs Tell:**
```json
{
  "category": "description",
  "priority": "high",
  "suggestion": "Show, don't tell - pokaż strach zamiast go opisywać",
  "example": "Zamiast 'Sarah była przerażona' → 'Ręce Sarah drżały. Oddech zatrzymał się w gardle.'"
}
```

**Response:**
```json
{
  "summary": "Tekst ma mocne dialogi, ale tempo wymaga poprawy",
  "strengths": [
    "Świetny voice postaci",
    "Ciekawe detale świata"
  ],
  "opportunities": [
    "Przyspiesz tempo scen dialogowych",
    "Dodaj więcej show, less tell"
  ],
  "suggestions": [...]
}
```

---

## 📦 **Export/Import**

### **Export Canon**

**Flow:**
```
1. User clicks "Eksportuj"
2. GET /api/canon/export/1
3. Backend:
   - Pobiera ALL entities (characters, locations, magic, events, threads, promises)
   - Konwertuje do JSON
   - Dodaje metadata (project_id, timestamp, version, stats)
4. Frontend:
   - Tworzy Blob z JSON
   - Auto-download: biblia-fabuly-2026-01-07.json
```

**Struktura pliku:**
```json
{
  "project_id": 1,
  "exported_at": "2026-01-07T10:30:00Z",
  "version": "1.0",
  "stats": {
    "character": 15,
    "location": 8,
    "magic_rule": 3,
    "event": 24,
    "promise": 7,
    "thread": 5,
    "total": 62
  },
  "entities": {
    "character": [...],
    "location": [...],
    "magic_rule": [...],
    "event": [...],
    "promise": [...],
    "thread": [...]
  }
}
```

### **Import Canon**

**2 Tryby:**

#### **Tryb Normalny** (overwrite: false):
```
1. User wybiera plik JSON
2. POST /api/canon/import/1 {entities, overwrite: false}
3. Backend:
   - Dodaje entities do existing
   - Usuwa metadata (id, created_at, updated_at)
   - Tworzy nowe entities
4. Response: {
     success: true,
     imported_counts: {character: 15, ...},
     errors: [],
     warnings: []
   }
```

#### **Tryb Nadpisywania** (overwrite: true):
```
⚠️ DESTRUCTIVE!

1. User zaznacza checkbox "Tryb nadpisywania"
2. Confirmation: "UWAGA: Usunie WSZYSTKIE dane!"
3. POST /api/canon/import/1 {entities, overwrite: true}
4. Backend:
   - DELETE wszystkie existing entities
   - Import nowych z pliku
5. Warning: "Deleted all existing canon entities"
```

**Use Cases:**
- **Backup**: Export przed dużymi zmianami
- **Templates**: Export generic fantasy world → import do nowego projektu
- **Sharing**: Dzielenie się światem z beta readerami
- **Version Control**: Git-like snapshots kanonu

---

## 🕸️ **Relationships Graph**

**Komponent:** `RelationshipsGraph.tsx`

### **Jak działa?**

#### **1. Data Preparation**

```typescript
// Z kanonu postaci
character.relationships = {
  "Marcus": {
    type: "ally",
    description: "Towarzysz broni",
    strength: 8
  },
  "Lord Vex": {
    type: "enemy",
    description: "Główny antagonista",
    strength: 10
  }
}

// Konwersja do grafu
nodes = characters.map(char => ({
  id: char.id,
  name: char.name,
  x: random_position,
  y: random_position,
  vx: 0,  // velocity x
  vy: 0   // velocity y
}))

edges = relationships.map(rel => ({
  source: char.id,
  target: other_char.id,
  type: rel.type,
  strength: rel.strength
}))
```

#### **2. Force Simulation**

**Physics Engine:**

```typescript
// Każda klatka (50ms):

// A) Repulsion Force (nodes push each other away)
for each pair (node_i, node_j):
  distance = sqrt((xi - xj)² + (yi - yj)²)
  force = 200 / distance²  // Coulomb's law
  node_i.vx -= force * (dx/distance)
  node_i.vy -= force * (dy/distance)
  node_j.vx += force * (dx/distance)
  node_j.vy += force * (dy/distance)

// B) Spring Force (edges pull nodes together)
for each edge:
  distance = actual_distance(source, target)
  target_distance = 150  // ideal spring length
  force = (distance - target_distance) * 0.1  // Hooke's law
  source.vx += force * (dx/distance)
  source.vy += force * (dy/distance)
  target.vx -= force * (dx/distance)
  target.vy -= force * (dy/distance)

// C) Center Gravity (keep graph centered)
for each node:
  node.vx += (0 - node.x) * 0.01
  node.vy += (0 - node.y) * 0.01

// D) Apply Velocities
for each node:
  node.x += node.vx
  node.y += node.vy
  node.vx *= 0.8  // damping
  node.vy *= 0.8
```

#### **3. Rendering (Canvas)**

```typescript
// Clear canvas
ctx.clearRect(0, 0, width, height)

// Transform (pan + zoom)
ctx.save()
ctx.translate(width/2 + pan.x, height/2 + pan.y)
ctx.scale(zoom, zoom)

// Draw edges with arrows
edges.forEach(edge => {
  ctx.strokeStyle = getEdgeColor(edge.type)
  ctx.lineWidth = edge.strength / 2
  ctx.beginPath()
  ctx.moveTo(source.x, source.y)
  ctx.lineTo(target.x, target.y)
  ctx.stroke()

  // Arrow at midpoint
  drawArrow(midpoint, angle, edge.color)
})

// Draw nodes
nodes.forEach(node => {
  // Circle
  ctx.fillStyle = isSelected ? '#6366f1' : '#8b5cf6'
  ctx.arc(node.x, node.y, 28, 0, Math.PI * 2)
  ctx.fill()

  // Label
  ctx.fillText(node.name, node.x, node.y)
})

ctx.restore()
```

#### **4. Interakcje**

**Drag Node:**
```typescript
onMouseDown(e) {
  clicked_node = findNodeAt(mouse.x, mouse.y)
  if (clicked_node) {
    clicked_node.fx = mouse.x  // fix position
    clicked_node.fy = mouse.y
  }
}

onMouseMove(e) {
  if (dragging_node) {
    node.x = mouse.x
    node.y = mouse.y
    // Simulation będzie próbować przesunąć, ale fx/fy override
  }
}

onMouseUp() {
  node.fx = undefined  // release fix
  node.fy = undefined
}
```

**Zoom:**
```typescript
onWheel(e) {
  delta = e.deltaY > 0 ? 0.9 : 1.1
  zoom = clamp(zoom * delta, 0.3, 3.0)
}
```

**Pan:**
```typescript
onMouseDown(e) {
  if (!clicked_node) {
    start_panning = true
  }
}

onMouseMove(e) {
  if (panning) {
    pan.x += e.clientX - last_mouse.x
    pan.y += e.clientY - last_mouse.y
  }
}
```

### **Edge Colors:**

```typescript
const edgeColors = {
  ally: '#10b981',    // green
  friend: '#3b82f6',  // blue
  family: '#8b5cf6',  // purple
  enemy: '#ef4444',   // red
  rival: '#f59e0b',   // orange
  mentor: '#14b8a6',  // teal
  romance: '#ec4899', // pink
  neutral: '#6b7280'  // gray
}
```

---

## 🔧 **Backend API - Kompletny Overview**

### **Authentication**

```python
# JWT Authentication
POST /api/auth/jwt/login
Body: {username, password}
Response: {access_token, token_type}

# Registration
POST /api/auth/register
Body: {email, password}

# Current User
GET /api/users/me
Headers: Authorization: Bearer {token}
```

### **Canon Entities**

**Pattern: CRUD dla każdego typu**

```python
# Characters
POST   /api/canon/character
GET    /api/canon/character/:id
GET    /api/canon/character?project_id=1&tags=protagonist
PUT    /api/canon/character/:id
DELETE /api/canon/character/:id

# Locations
POST   /api/canon/location
GET    /api/canon/location/:id
GET    /api/canon/location?project_id=1
PUT    /api/canon/location/:id
DELETE /api/canon/location/:id

# Magic Rules
POST   /api/canon/magic
GET    /api/canon/magic/:id
GET    /api/canon/magic?project_id=1&rule_type=magic
PUT    /api/canon/magic/:id
DELETE /api/canon/magic/:id

# Events (Timeline)
POST   /api/canon/event
GET    /api/canon/event/:id
GET    /api/canon/event?project_id=1&chapter_number=8
PUT    /api/canon/event/:id
DELETE /api/canon/event/:id

# Promises
POST   /api/canon/promise
GET    /api/canon/promise/:id
GET    /api/canon/promise?project_id=1&status=open
PUT    /api/canon/promise/:id
DELETE /api/canon/promise/:id

# Threads
POST   /api/canon/thread
GET    /api/canon/thread/:id
GET    /api/canon/thread?project_id=1&status=active
PUT    /api/canon/thread/:id
DELETE /api/canon/thread/:id
```

### **Canon Utilities**

```python
# Validation
GET /api/canon/validate/{type}/{id}
Response: {
  valid: true,
  issues: ["Missing required field: goals"]
}

# Version History (Git-like)
GET /api/canon/versions/{project_id}
Response: [
  {
    id: 42,
    version_number: 15,
    commit_message: "Added new character Elara",
    changes: {...},
    created_at: "2026-01-07T10:00:00Z"
  }
]

# Statistics
GET /api/canon/stats/{project_id}
Response: {
  character: 15,
  location: 8,
  magic_rule: 3,
  event: 24,
  promise: 7,
  thread: 5,
  total: 62
}

# Export/Import
GET  /api/canon/export/{project_id}
POST /api/canon/import/{project_id}
```

### **AI Writing Assistant**

```python
# Scene Generation
POST /projects/{id}/ai/generate-scene
Body: {
  scene_description: "Sarah discovers her magic powers",
  pov_character_id: 42,
  target_word_count: 1000,
  preset: "balanced"
}

# Expand Beats
POST /projects/{id}/ai/expand-beats
Body: {
  beats: [
    "Sarah wakes up",
    "She discovers glowing hands",
    "Panic sets in"
  ],
  words_per_beat: 200
}

# Continue Text
POST /projects/{id}/ai/continue
Body: {
  existing_text: "Sarah stared at her hands...",
  continuation_prompt: "She realizes what this means",
  target_word_count: 500
}

# Refine Prose
POST /projects/{id}/ai/refine
Body: {
  prose: "Sarah was scared. She looked at her hands.",
  refinement_goals: [
    "Show don't tell",
    "Add sensory details"
  ]
}
Response: {
  text: "Sarah's breath caught in her throat. The trembling in her hands spread through her arms, a cold wave that made her skin prickle.",
  model_used: "claude-opus-4",
  tokens_used: 1245,
  cost: 0.03
}

# Consistency Check
POST /projects/{id}/ai/check-consistency
Body: {text, chapter_number, check_character_voice: true}

# Suggestions
POST /projects/{id}/ai/suggest
Body: {text, focus_areas: ["pacing", "dialogue"]}

# Presets
GET /ai/presets
Response: {
  presets: [
    {id: "fast_draft", model: "gpt-4o-mini"},
    {id: "balanced", model: "claude-sonnet-3.5"},
    {id: "premium", model: "claude-opus-4"},
    {id: "creative_burst", model: "gpt-4o"},
    {id: "canon_strict", model: "claude-opus-4"}
  ]
}
```

### **Desktop Dashboard**

```python
# Full Dashboard
GET /api/desktop/dashboard
Response: {
  stats: WritingStats,
  projects: [ProjectSummary],
  recent_activity: [RecentActivity],
  daily_activity: [DailyActivity],
  quick_actions: [QuickAction]
}

# Stats Only
GET /api/desktop/stats?project_id=1
Response: {
  today_words: 1250,
  week_words: 7890,
  streak_days: 12,
  total_words: 245830,
  chapters_completed: 8,
  avg_words_per_day: 982,
  best_day_words: 3450
}

# Activity Feed
GET /api/desktop/activity?limit=20
Response: [
  {
    type: "character_added",
    description: "Dodano postać 'Elara'",
    timestamp: "2026-01-07T08:00:00Z",
    metadata: {character_id: 42}
  }
]

# Track Session
POST /api/desktop/track-session
Body: {
  words_written: 1250,
  minutes_spent: 45,
  chapter_id: 8
}
Response: {
  success: true,
  new_streak: 13
}
```

---

## 🎯 **Przepływ Pracy (Workflow)**

### **Scenariusz 1: Nowy Projekt**

```
1. Desktop → Quick Start → "Nowy Projekt"
   ↓
2. Create Project
   - Nazwa: "Mroczna Forteca"
   - Gatunek: Fantasy
   - Target: 100,000 słów
   ↓
3. Story Bible → Dodaj Postacie
   - Protagonist: Sarah (goals, fears, behavioral limits)
   - Antagonist: Lord Vex
   - Mentor: Marcus
   ↓
4. Story Bible → Dodaj Lokacje
   - Mroczna Forteca (social rules, restrictions)
   - Królewska Przystań
   ↓
5. Story Bible → Magia i Zasady
   - Magia Krwi (laws, costs, limitations)
   ↓
6. Story Bible → Timeline
   - Backstory events
   - Plot events plan
   ↓
7. Story Bible → Export
   - Backup: biblia-fabuly-2026-01-07.json
   ↓
8. Writing Studio → Nowy Rozdział
   - AI Generate Scene (uses canon!)
   - Manual writing
   ↓
9. AI Tools → Consistency Check
   - Fix issues
   ↓
10. Desktop → Track progress
    - Update streak 🔥
```

### **Scenariusz 2: Import Template**

```
1. Download: "generic-fantasy-world.json"
   ↓
2. Story Bible → Importuj
   - Tryb: Normalny (dodaj do existing)
   - Import: 25 characters, 15 locations, 5 magic systems
   ↓
3. Customize:
   - Zmień nazwy postaci
   - Dostosuj magie do swojego świata
   ↓
4. Story Bible → Graf Relacji
   - Wizualizuj imported relationships
   - Dodaj nowe relacje
   ↓
5. Export własny template
```

### **Scenariusz 3: Consistency Checking**

```
Napisałeś rozdział 8:

1. Copy tekst
   ↓
2. AI Tools → Sprawdzanie Spójności
   ↓
3. AI znajduje problemy:

   🔴 CRITICAL:
   "Elara użyła magii krwi 4 razy"
   → Canon: "Maksymalnie 3 zaklęcia dziennie"
   → Fix: Usuń jedno zaklęcie

   🟡 WARNING:
   "Marcus powiedział: 'To enigmatyczne'"
   → Canon voice: "simple vocabulary"
   → Fix: "To dziwne"

   🔵 SUGGESTION:
   "Za dużo dialogue, przyspiesz tempo"
   → Add action between lines
   ↓
4. Fix wszystkie CRITICAL
   ↓
5. Re-check → Score: 95/100 ✅
```

---

## ⌨️ **Skróty Klawiszowe**

```
Ctrl+K  → Quick Actions (Spotlight)
Ctrl+N  → Nowy Rozdział
Ctrl+B  → Biblia Fabuły
Ctrl+A  → Statystyki
Ctrl+R  → Graf Relacji
Ctrl+T  → Oś Czasu
Ctrl+S  → Save (auto-save)
Ctrl+E  → Export Canon
Ctrl+I  → Import Canon
```

---

## 🎨 **Design System**

### **Kolory:**

```scss
// Desktop - Dark Theme
bg-gradient: slate-900 → purple-900 → indigo-900
cards: white + bg-opacity-10 + backdrop-blur

// Story Bible - Light Theme
bg-gradient: slate-50 → blue-50 → indigo-50
cards: white + border-gray-200

// Gradient Cards
green:  from-green-500 to-emerald-600   // Today words
orange: from-orange-500 to-red-600      // Streak
blue:   from-blue-500 to-indigo-600     // Progress
purple: from-purple-500 to-pink-600     // Completed
```

### **Typography:**

```scss
h1: text-3xl font-bold
h2: text-2xl font-bold
h3: text-lg font-semibold
body: text-sm text-gray-600
label: text-sm font-medium text-gray-700
```

### **Components:**

```tsx
// Button Primary
className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600
           text-white rounded-lg hover:from-indigo-700 hover:to-purple-700"

// Button Secondary
className="px-4 py-2 border border-gray-300 text-gray-700
           rounded-lg hover:bg-gray-50"

// Card
className="bg-white rounded-xl shadow-sm border border-gray-200
           hover:shadow-md transition p-6"

// Modal
className="fixed inset-0 bg-black bg-opacity-50 flex items-center
           justify-center z-50"
```

---

## 🚀 **Co Dalej? (Roadmap)**

### **Phase 2: Writing Studio**
- Integrated Markdown Editor
- Live word count + goals tracking
- Auto-save + version history
- Distraction-free mode
- Split view (outline | prose)

### **Phase 3: AI Copilot**
- Floating assistant widget
- Context-aware autocomplete
- Voice commands
- Real-time suggestions podczas pisania

### **Phase 4: Analytics**
- Writing productivity heatmap
- Character arc visualizer
- Emotional arc tracker
- Story health dashboard
- Pacing analyzer

### **Phase 5: Collaboration**
- Real-time co-writing (WebSockets)
- Comments & annotations
- Beta readers portal
- Writing groups
- Feedback system

### **Phase 6: Publishing**
- Export to EPUB/MOBI/PDF
- Amazon KDP integration
- Cover generator
- Marketing tools

---

## 📚 **Podsumowanie**

**Narrative OS to kompletny ekosystem dla pisarzy:**

✅ **Desktop** - Command center z stats i quick actions
✅ **Story Bible** - Canon management (5 tabs)
✅ **AI Tools** - Consistency + Suggestions
✅ **Export/Import** - Backup i templates
✅ **Relationships Graph** - Interactive visualization
✅ **Backend API** - RESTful endpoints
✅ **100% Polonizacja** - Wszystko po polsku

**Tech Stack:**
- Next.js 14 + React 18 + TypeScript
- FastAPI + SQLAlchemy + PostgreSQL
- OpenAI + Claude + RAG Engine

**Wszystko gotowe do użycia!** 🎉
