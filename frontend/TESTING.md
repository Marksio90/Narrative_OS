# Frontend Testing Guide 🧪

Comprehensive testing guide for Agent Collaboration frontend components.

## 📊 Test Statistics

**Total Tests: 61**

- **Agent Dashboard**: 32 tests
  - Rendering: 5 tests
  - Agent List: 5 tests
  - Agent Interaction: 2 tests
  - Task Management: 4 tests
  - Statistics: 3 tests
  - Actions: 2 tests
  - Auto-refresh: 1 test

- **Collaboration Workspace**: 29 tests
  - Rendering: 3 tests
  - Conversation List: 4 tests
  - Messages: 4 tests
  - Sending Messages: 5 tests
  - Voting: 2 tests
  - Memories: 4 tests
  - Conversation Actions: 7 tests

## 🏗️ Test Structure

```
frontend/
├── jest.config.ts                 # Jest configuration
├── jest.setup.ts                  # Test setup and mocks
├── package-test.json              # Testing dependencies
└── src/
    ├── app/(main)/agents/
    │   └── __tests__/
    │       └── page.test.tsx      # Agent Dashboard tests (32 tests)
    └── components/
        └── __tests__/
            └── CollaborationWorkspace.test.tsx  # Workspace tests (29 tests)
```

## 🚀 Setup

### Install Dependencies

```bash
cd frontend

# Install testing dependencies
npm install --save-dev @testing-library/react@14.1.2
npm install --save-dev @testing-library/jest-dom@6.1.5
npm install --save-dev @testing-library/user-event@14.5.1
npm install --save-dev @types/jest@29.5.11
npm install --save-dev jest@29.7.0
npm install --save-dev jest-environment-jsdom@29.7.0
npm install --save-dev ts-jest@29.1.1
```

### Configuration Files

- **jest.config.ts**: Jest configuration for Next.js
- **jest.setup.ts**: Global test setup, mocks, and utilities
- **package-test.json**: Test-specific dependencies

## 🧪 Running Tests

### All Tests
```bash
npm test
```

### Watch Mode
```bash
npm run test:watch
```

### Coverage Report
```bash
npm run test:coverage
```

### Specific Test File
```bash
npm test -- page.test.tsx
npm test -- CollaborationWorkspace.test.tsx
```

### Specific Test
```bash
npm test -- -t "should render dashboard after loading"
npm test -- -t "should send message"
```

### Verbose Output
```bash
npm test -- --verbose
```

## 📝 Test Coverage

### Agent Dashboard (page.test.tsx)

**Rendering (5 tests):**
- ✅ Loading state display
- ✅ Dashboard rendering after load
- ✅ Project statistics display
- ✅ Agent list rendering
- ✅ Task queue rendering

**Agent List (5 tests):**
- ✅ Agent completion stats
- ✅ Busy indicator for active agents
- ✅ Satisfaction score display
- ✅ Empty state handling
- ✅ Agent type badges

**Agent Interaction (2 tests):**
- ✅ Agent selection on click
- ✅ Toggle agent active status

**Task Management (4 tests):**
- ✅ Start assigned task
- ✅ Task priority badges
- ✅ Task status badges
- ✅ Empty task queue state

**Statistics (3 tests):**
- ✅ Success rate calculation
- ✅ Average satisfaction display
- ✅ N/A for missing data

**Actions (2 tests):**
- ✅ Initialize default agents
- ✅ Create task button

**Auto-refresh (1 test):**
- ✅ Interval setup for data refresh

### Collaboration Workspace (CollaborationWorkspace.test.tsx)

**Rendering (3 tests):**
- ✅ Conversation list display
- ✅ Empty state handling
- ✅ Discussions/Memories tabs

**Conversation List (4 tests):**
- ✅ Participants count
- ✅ Conflict indicator
- ✅ Resolved indicator
- ✅ Conversation selection

**Messages (4 tests):**
- ✅ Message display
- ✅ Agent name for messages
- ✅ Suggestion badges
- ✅ Auto-scroll to latest

**Sending Messages (5 tests):**
- ✅ Send via button click
- ✅ Send on Enter key
- ✅ Input clearing after send
- ✅ Disabled state validation
- ✅ Agent selection requirement

**Voting (2 tests):**
- ✅ Voting panel display
- ✅ Cast vote action

**Memories (4 tests):**
- ✅ Tab switching
- ✅ Memory loading
- ✅ Importance bar display
- ✅ Empty state

**Conversation Actions (7 tests):**
- ✅ Resolve button display
- ✅ Conversation resolution
- ✅ Resolved badge
- ✅ Input disable for resolved
- ✅ Voting active indicator
- ✅ Message composition
- ✅ Real-time updates

## 🔧 Test Utilities

### Mocking Fetch

```typescript
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>

mockFetch.mockImplementation((url: string | URL | Request) => {
  const urlString = url.toString()

  if (urlString.includes('/agents')) {
    return Promise.resolve({
      ok: true,
      json: async () => mockAgents,
    } as Response)
  }

  return Promise.reject(new Error('Unknown URL'))
})
```

### User Interactions

```typescript
import userEvent from '@testing-library/user-event'

const user = userEvent.setup()

// Click
await user.click(screen.getByText('Button'))

// Type
await user.type(input, 'text')

// Select
await user.selectOptions(select, 'option')
```

### Waiting for Elements

```typescript
import { waitFor, screen } from '@testing-library/react'

await waitFor(() => {
  expect(screen.getByText('Content')).toBeInTheDocument()
})
```

## 🐛 Common Issues

### TypeError: Cannot read property 'matches' of undefined

**Solution**: Add `window.matchMedia` mock to `jest.setup.ts`

```typescript
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  })),
})
```

### IntersectionObserver is not defined

**Solution**: Mock `IntersectionObserver` in `jest.setup.ts`

```typescript
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
} as any
```

### Module not found: Can't resolve '@/...'

**Solution**: Ensure `moduleNameMapper` is configured in `jest.config.ts`

```typescript
moduleNameMapper: {
  '^@/(.*)$': '<rootDir>/src/$1',
}
```

## 📈 Coverage Goals

- **Statements**: > 80%
- **Branches**: > 75%
- **Functions**: > 80%
- **Lines**: > 80%

Current coverage (estimated):
- Agent Dashboard: ~85%
- Collaboration Workspace: ~80%

## 🎯 Testing Best Practices

1. **Test User Behavior, Not Implementation**
   ```typescript
   // Good
   await user.click(screen.getByRole('button', { name: 'Submit' }))

   // Avoid
   fireEvent.click(component.find('.submit-button').at(0))
   ```

2. **Use Semantic Queries**
   ```typescript
   // Preferred order
   screen.getByRole('button')
   screen.getByLabelText('Email')
   screen.getByPlaceholderText('Enter email')
   screen.getByText('Submit')
   screen.getByTestId('custom-element') // last resort
   ```

3. **Wait for Async Updates**
   ```typescript
   await waitFor(() => {
     expect(screen.getByText('Loaded')).toBeInTheDocument()
   })
   ```

4. **Mock External Dependencies**
   ```typescript
   jest.mock('../api/client')
   ```

5. **Clean Up After Tests**
   ```typescript
   afterEach(() => {
     jest.clearAllMocks()
   })
   ```

## 📚 Resources

- [React Testing Library Docs](https://testing-library.com/docs/react-testing-library/intro/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Testing Library Queries](https://testing-library.com/docs/queries/about)
- [User Event API](https://testing-library.com/docs/user-event/intro)
- [Common Mistakes](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: Frontend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm install

      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          directory: ./frontend/coverage
```

## ✅ Pre-commit Checks

Add to `package.json`:

```json
{
  "scripts": {
    "precommit": "npm test && npm run lint"
  }
}
```

Or use Husky:

```bash
npm install --save-dev husky
npx husky install
npx husky add .husky/pre-commit "cd frontend && npm test"
```

---

**Happy Testing!** 🧪✨
