# Narrative OS Frontend

Next.js 14 frontend for Narrative OS - AI-powered narrative platform for serious fiction writers.

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client for API calls
- **Lucide React** - Icon library

## Project Structure

```
frontend/
├── src/
│   ├── app/                # Next.js 14 App Router pages
│   │   ├── canon/          # Canon Studio page
│   │   ├── planner/        # Planner page
│   │   ├── editor/         # Editor page
│   │   ├── promises/       # Promise Ledger page
│   │   └── page.tsx        # Home page
│   ├── components/         # Reusable UI components
│   │   ├── canon/          # Canon-specific components
│   │   ├── planner/        # Planner-specific components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Textarea.tsx
│   │   └── Layout.tsx
│   ├── types/              # TypeScript type definitions
│   │   ├── canon.ts
│   │   ├── planner.ts
│   │   └── draft.ts
│   └── lib/                # Utilities and API client
│       ├── api.ts          # Axios instance with interceptors
│       └── utils.ts        # Helper functions
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## Features

### 1. Canon Studio
- Manage story bible entities (Characters, Locations, Factions, Magic Rules, Items, Events)
- Create and edit Canon Contracts (hard consistency rules)
- Git-like versioning for all changes
- Claims vs Unknowns distinction

### 2. Planner
- 3-level story structure:
  - **Book Arc** - Overall story structure with act breaks
  - **Chapters** - Chapter-by-chapter planning with goals and POV
  - **Scene Cards** - Scene-by-scene breakdown with value changes
- Visual scene card display with entering/exiting values

### 3. Editor
- Generate prose scene-by-scene
- Multi-agent Quality Control (Continuity, Character, Plot editors)
- Real-time validation with QC reports
- Fact extraction from generated prose
- Issue tracking with severity levels (blocker/warning/suggestion)

### 4. Promise Ledger
- Automatic promise detection during generation
- Track narrative setups and payoffs
- Filter by status (open/fulfilled/abandoned)
- Deadline tracking per promise
- Confidence scoring

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Update .env with your backend URL
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

### Building for Production

```bash
# Create production build
npm run build

# Start production server
npm start
```

## API Integration

The frontend connects to the Narrative OS backend API (default: `http://localhost:8000`).

All API calls go through the centralized `api.ts` client with:
- Automatic error handling
- Request/response interceptors
- Future auth token support

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend API URL
```

## Development Notes

### Project ID
Currently hardcoded to `1` in all pages. TODO: Implement proper project context/auth.

### Type Safety
All API responses are typed using TypeScript interfaces matching the backend Pydantic schemas.

### Styling
- Tailwind CSS for utility classes
- Dark mode support built-in
- Responsive design for mobile/tablet/desktop

## Next Steps

- [ ] Add authentication/authorization
- [ ] Implement project switcher
- [ ] Add scene creation UI in Planner
- [ ] Add faction/magic/item/event forms in Canon Studio
- [ ] Implement chapter draft generation in Editor
- [ ] Add export functionality (DOCX/EPUB)
- [ ] Add error boundaries
- [ ] Add loading skeletons
- [ ] Implement optimistic UI updates
- [ ] Add toast notifications

## License

Proprietary
