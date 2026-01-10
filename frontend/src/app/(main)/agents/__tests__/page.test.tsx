/**
 * Tests for Agent Dashboard component
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AgentDashboard from '../page'

// Mock fetch globally
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>

// Mock data
const mockAgents = [
  {
    id: 1,
    project_id: 1,
    name: 'Plot Master',
    agent_type: 'plotting',
    role: 'contributor',
    description: 'Plot analysis agent',
    is_active: true,
    is_busy: false,
    tasks_completed: 10,
    tasks_failed: 1,
    user_satisfaction_score: 0.85,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    project_id: 1,
    name: 'Character Developer',
    agent_type: 'character',
    role: 'contributor',
    description: 'Character development',
    is_active: true,
    is_busy: true,
    tasks_completed: 8,
    tasks_failed: 0,
    user_satisfaction_score: 0.92,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
]

const mockTaskQueue = {
  tasks: [
    {
      id: 1,
      project_id: 1,
      agent_id: 1,
      title: 'Analyze plot structure',
      description: 'Review chapters 1-5',
      task_type: 'analyze_plot',
      status: 'assigned',
      priority: 'high',
      assigned_at: '2024-01-01T00:00:00Z',
      started_at: null,
      completed_at: null,
      deadline: null,
      user_approved: null,
      user_rating: null,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    },
  ],
  total: 1,
  pending_count: 0,
  in_progress_count: 0,
  completed_count: 5,
}

const mockProjectStats = {
  total_agents: 2,
  active_agents: 2,
  busy_agents: 1,
  agents_by_type: {
    plotting: 1,
    character: 1,
  },
  total_tasks: 6,
  completed_tasks: 5,
  failed_tasks: 1,
  average_satisfaction: 0.88,
}

describe('AgentDashboard', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  // Helper to setup successful fetch responses
  const setupMockFetch = () => {
    mockFetch.mockImplementation((url: string | URL | Request) => {
      const urlString = url.toString()

      if (urlString.includes('/agents?')) {
        return Promise.resolve({
          ok: true,
          json: async () => mockAgents,
        } as Response)
      }

      if (urlString.includes('/agents') && !urlString.includes('statistics')) {
        return Promise.resolve({
          ok: true,
          json: async () => mockAgents,
        } as Response)
      }

      if (urlString.includes('/tasks')) {
        return Promise.resolve({
          ok: true,
          json: async () => mockTaskQueue,
        } as Response)
      }

      if (urlString.includes('/statistics')) {
        return Promise.resolve({
          ok: true,
          json: async () => mockProjectStats,
        } as Response)
      }

      return Promise.reject(new Error('Unknown URL'))
    })
  }

  describe('Rendering', () => {
    it('should render loading state initially', () => {
      setupMockFetch()
      render(<AgentDashboard />)

      expect(screen.getByText(/Loading Agent Dashboard/i)).toBeInTheDocument()
    })

    it('should render dashboard after loading', async () => {
      setupMockFetch()
      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText(/Agent Collaboration/i)).toBeInTheDocument()
      })
    })

    it('should display project statistics', async () => {
      setupMockFetch()
      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText('Total Agents')).toBeInTheDocument()
        expect(screen.getByText('2')).toBeInTheDocument()
        expect(screen.getByText('Active')).toBeInTheDocument()
        expect(screen.getByText('Busy')).toBeInTheDocument()
        expect(screen.getByText('1')).toBeInTheDocument()
      })
    })

    it('should display agent list', async () => {
      setupMockFetch()
      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText('Plot Master')).toBeInTheDocument()
        expect(screen.getByText('Character Developer')).toBeInTheDocument()
      })
    })

    it('should display task queue', async () => {
      setupMockFetch()
      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText('Analyze plot structure')).toBeInTheDocument()
      })
    })
  })

  describe('Agent List', () => {
    it('should show agent completion stats', async () => {
      setupMockFetch()
      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText('10')).toBeInTheDocument() // completed tasks
        expect(screen.getByText('completed')).toBeInTheDocument()
      })
    })

    it('should show busy indicator for busy agents', async () => {
      setupMockFetch()
      render(<AgentDashboard />)

      await waitFor(() => {
        const busyIndicators = screen.getAllByTestId('busy-icon')
        expect(busyIndicators.length).toBeGreaterThan(0)
      })
    })

    it('should show satisfaction score', async () => {
      setupMockFetch()
      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText(/85%/)).toBeInTheDocument() // 0.85 * 100
      })
    })

    it('should display empty state when no agents', async () => {
      mockFetch.mockImplementation((url: string | URL | Request) => {
        const urlString = url.toString()

        if (urlString.includes('/agents')) {
          return Promise.resolve({
            ok: true,
            json: async () => [],
          } as Response)
        }

        if (urlString.includes('/tasks')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ tasks: [], total: 0, pending_count: 0, in_progress_count: 0, completed_count: 0 }),
          } as Response)
        }

        if (urlString.includes('/statistics')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ ...mockProjectStats, total_agents: 0 }),
          } as Response)
        }

        return Promise.reject(new Error('Unknown URL'))
      })

      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText(/No agents yet/i)).toBeInTheDocument()
      })
    })
  })

  describe('Agent Interaction', () => {
    it('should select agent on click', async () => {
      setupMockFetch()
      const user = userEvent.setup()
      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText('Plot Master')).toBeInTheDocument()
      })

      const agentCard = screen.getByText('Plot Master').closest('div')
      if (agentCard) {
        await user.click(agentCard)
      }

      // Check if agent is selected (would need data-testid or class check)
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('agent_id=1'),
        )
      })
    })

    it('should toggle agent active status', async () => {
      setupMockFetch()
      mockFetch.mockImplementationOnce((url: string | URL | Request) => {
        const urlString = url.toString()
        if (urlString.includes('/agents') && !urlString.includes('statistics')) {
          return Promise.resolve({
            ok: true,
            json: async () => mockAgents,
          } as Response)
        }
        return Promise.reject(new Error('Unknown URL'))
      })

      const user = userEvent.setup()
      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText('Plot Master')).toBeInTheDocument()
      })

      // Find and click active toggle button
      const toggleButtons = screen.getAllByRole('button')
      const activeToggle = toggleButtons.find(btn =>
        btn.className.includes('bg-green-500')
      )

      if (activeToggle) {
        await user.click(activeToggle)

        await waitFor(() => {
          expect(mockFetch).toHaveBeenCalledWith(
            expect.stringContaining('/agents/'),
            expect.objectContaining({
              method: 'PATCH',
            })
          )
        })
      }
    })
  })

  describe('Task Management', () => {
    it('should start an assigned task', async () => {
      setupMockFetch()
      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: async () => ({ ...mockTaskQueue.tasks[0], status: 'in_progress' }),
        } as Response)
      )

      const user = userEvent.setup()
      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText('Analyze plot structure')).toBeInTheDocument()
      })

      const startButton = screen.getByText('Start')
      await user.click(startButton)

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/tasks/1/start'),
          expect.objectContaining({
            method: 'POST',
          })
        )
      })
    })

    it('should display task priority badges', async () => {
      setupMockFetch()
      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText('high')).toBeInTheDocument()
      })
    })

    it('should display task status badges', async () => {
      setupMockFetch()
      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText('assigned')).toBeInTheDocument()
      })
    })

    it('should show empty state when no tasks', async () => {
      mockFetch.mockImplementation((url: string | URL | Request) => {
        const urlString = url.toString()

        if (urlString.includes('/agents')) {
          return Promise.resolve({
            ok: true,
            json: async () => mockAgents,
          } as Response)
        }

        if (urlString.includes('/tasks')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({
              tasks: [],
              total: 0,
              pending_count: 0,
              in_progress_count: 0,
              completed_count: 0,
            }),
          } as Response)
        }

        if (urlString.includes('/statistics')) {
          return Promise.resolve({
            ok: true,
            json: async () => mockProjectStats,
          } as Response)
        }

        return Promise.reject(new Error('Unknown URL'))
      })

      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText(/No tasks in queue/i)).toBeInTheDocument()
      })
    })
  })

  describe('Statistics', () => {
    it('should calculate and display success rate', async () => {
      setupMockFetch()
      render(<AgentDashboard />)

      await waitFor(() => {
        // 5 completed / 6 total = 83.3%
        expect(screen.getByText(/83/)).toBeInTheDocument()
      })
    })

    it('should display average satisfaction score', async () => {
      setupMockFetch()
      render(<AgentDashboard />)

      await waitFor(() => {
        // 0.88 * 100 = 88%
        expect(screen.getByText(/88%/)).toBeInTheDocument()
      })
    })

    it('should show N/A for missing satisfaction', async () => {
      mockFetch.mockImplementation((url: string | URL | Request) => {
        const urlString = url.toString()

        if (urlString.includes('/statistics')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ ...mockProjectStats, average_satisfaction: null }),
          } as Response)
        }

        if (urlString.includes('/agents')) {
          return Promise.resolve({
            ok: true,
            json: async () => mockAgents,
          } as Response)
        }

        if (urlString.includes('/tasks')) {
          return Promise.resolve({
            ok: true,
            json: async () => mockTaskQueue,
          } as Response)
        }

        return Promise.reject(new Error('Unknown URL'))
      })

      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText('N/A')).toBeInTheDocument()
      })
    })
  })

  describe('Actions', () => {
    it('should initialize default agents', async () => {
      setupMockFetch()
      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: async () => mockAgents,
        } as Response)
      )

      const user = userEvent.setup()
      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText(/Initialize Agent Team/i)).toBeInTheDocument()
      })

      const initButton = screen.getByText(/Initialize Agent Team/i)
      await user.click(initButton)

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/agents/initialize'),
          expect.objectContaining({
            method: 'POST',
          })
        )
      })
    })

    it('should show create task button', async () => {
      setupMockFetch()
      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText(/Create Task/i)).toBeInTheDocument()
      })
    })
  })

  describe('Auto-refresh', () => {
    it('should set up interval for auto-refresh', async () => {
      jest.useFakeTimers()
      setupMockFetch()

      render(<AgentDashboard />)

      await waitFor(() => {
        expect(screen.getByText('Agent Collaboration')).toBeInTheDocument()
      })

      const initialCallCount = mockFetch.mock.calls.length

      // Fast-forward 10 seconds
      jest.advanceTimersByTime(10000)

      await waitFor(() => {
        // Should have made additional API calls
        expect(mockFetch.mock.calls.length).toBeGreaterThan(initialCallCount)
      })

      jest.useRealTimers()
    })
  })
})
