# ⚡ Consequence Simulator - Quick Start Guide

## 🎯 What is it?

Track story events and predict their consequences using AI. Never forget a plot thread again!

## 🚀 5-Minute Setup

### Step 1: Write a Scene in AI Studio
1. Go to `/ai-studio`
2. Write scene description: "Sarah discovers the hidden safe"
3. Click **Generate Scene**
4. AI creates your prose

### Step 2: Analyze for Consequences
```bash
POST /api/consequences/analyze-scene
{
  "project_id": 1,
  "scene_id": 1,
  "scene_text": "Your generated scene...",
  "chapter_number": 3
}
```

**What happens:**
- AI extracts events (e.g., "Discovery of safe")
- AI predicts consequences automatically
- Events saved to database

### Step 3: View Active Consequences

**In AI Studio (Left Panel):**
- See "Active Consequences" panel
- Auto-refreshes every 30 seconds
- Shows what needs to happen next

**On Consequences Page (`/consequences`):**
- Full dashboard with statistics
- Advanced filtering
- Graph visualization

## 📱 UI Overview

### AI Studio Panel (While Writing)

```
┌─────────────────────────────────┐
│ 🚨 Active Consequences (3)      │
├─────────────────────────────────┤
│ [85%] Sarah becomes target      │
│  ⚡ Immediate · 🔴 High Severity│
│  💡 Click for AI reasoning      │
├─────────────────────────────────┤
│ [70%] Truth about conspiracy... │
│  🕐 Short-term · 🟡 Med Severity│
├─────────────────────────────────┤
│ [60%] Relationship deteriorates │
│  📊 Medium-term · 🔵 Low Severity│
└─────────────────────────────────┘
```

### Consequences Page (Full Management)

```
┌────────────────────────────────────────┐
│ 📊 Stats                               │
│ 15 Events | 42 Consequences | 12 Active│
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ 🎨 Graph Visualization                 │
│ [Interactive force-directed layout]    │
│ - Zoom/Pan                             │
│ - Click nodes for details              │
│ - Filter by status                     │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ 📋 Consequences List                   │
│ ☐ Potential  ☑ Active  ☑ Realized     │
│ ───────────────────────────────────────│
│ [85%] ⚡ Sarah targeted by enemies     │
│ [70%] 🕐 Documents lead to conspiracy  │
│ [60%] 📊 Relationship breakdown        │
└────────────────────────────────────────┘
```

## 🎮 Common Workflows

### Workflow 1: Writing New Chapter

1. **Before Writing:**
   - Open `/consequences`
   - Check "Active" consequences
   - Note what needs to happen

2. **While Writing (AI Studio):**
   - Glance at Active Consequences panel
   - Include high-probability events
   - System tracks automatically

3. **After Writing:**
   - Analyze new scene
   - Mark consequences as realized
   - New predictions appear

### Workflow 2: Planning Arc

1. Navigate to `/consequences`
2. Click **Show Graph**
3. See all event chains
4. Identify unresolved threads
5. Plan next chapters

### Workflow 3: Consistency Check

1. View consequence timeline
2. Filter by `timeframe: immediate`
3. Check if all were realized
4. Mark old ones as invalidated if plot changed

## 🎨 Visual Guide

### Event Types (Colors)

| Type | Color | Icon | Example |
|------|-------|------|---------|
| **Decision** | 🔵 Blue | 🎯 | "Sarah chooses to investigate" |
| **Revelation** | 🟣 Purple | 💡 | "Secret door discovered" |
| **Conflict** | 🔴 Red | ⚔️ | "Fight with antagonist" |
| **Resolution** | 🟢 Green | ✅ | "Mystery solved" |
| **Relationship** | 🩷 Pink | 💕 | "Trust broken" |
| **Discovery** | 🟠 Orange | 🔍 | "Clue found" |

### Consequence Status (Lifecycle)

```
Potential → Active → Realized
    ↓                   ↑
Invalidated ←─────┘
```

| Status | Meaning | Color |
|--------|---------|-------|
| **Potential** | AI predicted, may happen | 🟣 Purple |
| **Active** | Currently developing | 🟠 Orange |
| **Realized** | Happened in story | 🟢 Green |
| **Invalidated** | Plot made it impossible | ⚫ Gray |

### Timeframe Icons

| Timeframe | Icon | When | Example |
|-----------|------|------|---------|
| **Immediate** | ⚡ | Same/next scene | "Alarm sounds" |
| **Short-term** | 🕐 | 1-3 chapters | "Investigation begins" |
| **Medium-term** | 📈 | 4-10 chapters | "Truth uncovered" |
| **Long-term** | 📊 | 10+ chapters | "Final confrontation" |

## 🔥 Power Tips

### Tip 1: Auto-Tracking
Leave Active Consequences panel open while writing. It's your AI co-pilot!

### Tip 2: Batch Analysis
Analyze multiple scenes at once:
```bash
for scene in chapter_3/*.txt; do
  curl -X POST /api/consequences/analyze-scene \
    -d @scene.json
done
```

### Tip 3: Export for Plotting
Use graph data for external plotting tools:
```bash
GET /api/consequences/graph?project_id=1&format=json
```

### Tip 4: Smart Filtering
In AI Studio panel:
- Sort by **Probability** → See what's most likely
- Sort by **Severity** → See what's most important
- Filter **Immediate** → See what needs to happen NOW

### Tip 5: Invalidation Notes
Always provide reason when invalidating:
```json
{
  "invalidation_reason": "Character died in Ch 5, can't have this conversation"
}
```

Helps you remember plot changes later!

## ⌨️ Keyboard Shortcuts (Graph View)

| Key | Action |
|-----|--------|
| **Scroll** | Zoom in/out |
| **Click + Drag Node** | Move event |
| **Click Background + Drag** | Pan view |
| **ESC** | Close graph |
| **R** | Reset zoom |

## 📊 Reading the Metrics

### Probability Bar
```
[████████░░] 80%  → Very likely to happen
[█████░░░░░] 50%  → Could go either way
[██░░░░░░░░] 20%  → Unlikely, but possible
```

### Severity Indicator
```
🔴 High (80-100%)    → Major plot impact, character death, etc.
🟡 Medium (50-80%)   → Significant but not critical
🔵 Low (0-50%)       → Minor impact, character development
```

### Graph Visualization
- **Node Size** → Event magnitude (bigger = more important)
- **Edge Width** → Consequence probability (thicker = more likely)
- **Edge Color** → Consequence status (see legend)
- **Floating Bubbles** → Unrealized consequences

## 🐛 Troubleshooting

### "No consequences showing"
1. Have you analyzed any scenes? Click "Analyze Scene"
2. Check filters - all unchecked = nothing shows
3. Try different chapter number

### "Graph won't render"
1. Need at least 2 events with consequences
2. Check browser console for errors
3. Try refresh (Cmd+R / Ctrl+R)

### "Probability seems wrong"
AI is predicting based on:
- Story context
- Genre conventions
- Character behavior patterns

You can always manually adjust!

### "Panel not refreshing"
Auto-refresh is every 30 seconds. For immediate refresh:
1. Switch tabs and back
2. Or manually refetch in React Query DevTools

## 🎓 Best Practices

### ✅ DO
- Analyze scenes as you write them
- Review active consequences before each chapter
- Mark consequences realized promptly
- Use graph for big-picture planning
- Provide invalidation reasons

### ❌ DON'T
- Don't analyze same scene twice (duplicates events)
- Don't ignore high-probability consequences
- Don't forget to mark as realized
- Don't leave old consequences in "active" forever
- Don't rely 100% on AI - use your judgment!

## 📚 Next Steps

1. ✅ Read full docs: `CONSEQUENCE_SIMULATOR.md`
2. 🧪 Try the example workflow above
3. 🎨 Explore graph visualization
4. 📊 Check statistics page
5. 🚀 Integrate into your writing process

## 💡 Example Session

```
1. Writing Chapter 5
   - Active consequences show: "Sarah must confront her boss"
   - Probability: 85%, Timeframe: Immediate

2. Write the scene
   - Include boss confrontation
   - Analyze scene when done

3. System detects:
   - Event: "Confrontation with boss"
   - Links to Chapter 3 discovery
   - Marks previous consequence as REALIZED

4. New predictions appear:
   - "Boss becomes ally" (65%, short-term)
   - "Sarah gains access to archives" (80%, immediate)

5. Continue writing with new context!
```

## 🆘 Quick Help

**Q: What's the difference between event and consequence?**
A: Event = what happened. Consequence = what might happen because of it.

**Q: How does AI predict consequences?**
A: Claude Opus analyzes the event, story context, characters, and genre to predict logical outcomes.

**Q: Can I edit consequences?**
A: Yes! Use PUT `/api/consequences/{id}/status` to update.

**Q: What if AI prediction is wrong?**
A: Mark as "invalidated" and provide reason. System learns patterns over time.

**Q: Does this replace outlining?**
A: No! It's a tool to **track** consequences, not replace planning. Use both!

---

**Need more help?** Check `CONSEQUENCE_SIMULATOR.md` for complete docs.

**Found a bug?** Open issue on GitHub.

**Happy Writing!** 📝✨
