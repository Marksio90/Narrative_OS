/**
 * Tests for CollaborationWorkspace component
 */

import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CollaborationWorkspace from '../CollaborationWorkspace'

// Mock fetch
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>

// Mock data
const mockAgents = [
  { id: 1, name: 'Plot Master', agent_type: 'plotting' },
  { id: 2, name: 'Character Developer', agent_type: 'character' },
  { id: 3, name: 'Dialogue Specialist', agent_type: 'dialogue' },
]

const mockConversations = [
  {
    id: 1,
    project_id: 1,
    title: 'Plot vs Character Priority',
    topic: 'priority',
    participant_agent_ids: [1, 2],
    moderator_agent_id: 1,
    is_active: true,
    is_resolved: false,
    has_conflict: false,
    started_at: '2024-01-01T00:00:00Z',
    ended_at: null,
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    project_id: 1,
    title: 'Dialogue Review Discussion',
    topic: 'dialogue',
    participant_agent_ids: [2, 3],
    moderator_agent_id: 3,
    is_active: false,
    is_resolved: true,
    has_conflict: false,
    started_at: '2024-01-01T00:00:00Z',
    ended_at: '2024-01-02T00:00:00Z',
    created_at: '2024-01-01T00:00:00Z',
  },
]

const mockMessages = [
  {
    id: 1,
    conversation_id: 1,
    agent_id: 1,
    content: 'I think we should focus on plot structure first.',
    message_type: 'comment',
    is_suggestion: true,
    suggestion_data: null,
    reply_to_message_id: null,
    reactions: {},
    created_at: '2024-01-01T10:00:00Z',
  },
  {
    id: 2,
    conversation_id: 1,
    agent_id: 2,
    content: 'Character motivation is more important at this stage.',
    message_type: 'comment',
    is_suggestion: true,
    suggestion_data: null,
    reply_to_message_id: null,
    reactions: {},
    created_at: '2024-01-01T10:05:00Z',
  },
]

const mockConversationDetail = {
  ...mockConversations[0],
  messages: mockMessages,
  resolution_summary: null,
  conflict_type: null,
  resolution_strategy: null,
  voting_options: null,
}

const mockMemories = [
  {
    id: 1,
    agent_id: 1,
    content: 'User prefers three-act structure',
    memory_type: 'feedback',
    importance: 0.8,
    access_count: 5,
    created_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    agent_id: 1,
    content: 'Foreshadowing is important',
    memory_type: 'episodic',
    importance: 0.6,
    access_count: 2,
    created_at: '2024-01-01T00:00:00Z',
  },
]

describe('CollaborationWorkspace', () => {
  const defaultProps = {
    projectId: 1,
    agents: mockAgents,
  }

  beforeEach(() => {
    mockFetch.mockClear()
  })

  const setupMockFetch = () => {
    mockFetch.mockImplementation((url: string | URL | Request) => {
      const urlString = url.toString()

      if (urlString.includes('/conversations') && !urlString.includes('/messages')) {
        if (urlString.match(/\/conversations\/\d+$/)) {
          return Promise.resolve({
            ok: true,
            json: async () => mockConversationDetail,
          } as Response)
        }
        return Promise.resolve({
          ok: true,
          json: async () => mockConversations,
        } as Response)
      }

      if (urlString.includes('/memories')) {
        return Promise.resolve({
          ok: true,
          json: async () => mockMemories,
        } as Response)
      }

      return Promise.reject(new Error('Unknown URL'))
    })
  }

  describe('Rendering', () => {
    it('should render conversation list', async () => {
      setupMockFetch()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Conversations')).toBeInTheDocument()
        expect(screen.getByText('Plot vs Character Priority')).toBeInTheDocument()
      })
    })

    it('should show empty state when no conversations', async () => {
      mockFetch.mockImplementation(() =>
        Promise.resolve({
          ok: true,
          json: async () => [],
        } as Response)
      )

      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText(/No conversations yet/i)).toBeInTheDocument()
      })
    })

    it('should render tabs for Discussions and Memories', () => {
      setupMockFetch()
      render(<CollaborationWorkspace {...defaultProps} />)

      expect(screen.getByText('Discussions')).toBeInTheDocument()
      expect(screen.getByText('Memories')).toBeInTheDocument()
    })
  })

  describe('Conversation List', () => {
    it('should display conversation participants count', async () => {
      setupMockFetch()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText(/2 agents participating/i)).toBeInTheDocument()
      })
    })

    it('should show conflict indicator for conversations with conflicts', async () => {
      mockFetch.mockImplementation(() =>
        Promise.resolve({
          ok: true,
          json: async () => [
            { ...mockConversations[0], has_conflict: true },
          ],
        } as Response)
      )

      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        const voteIcons = screen.getAllByTestId('vote-icon')
        expect(voteIcons.length).toBeGreaterThan(0)
      })
    })

    it('should show resolved indicator for resolved conversations', async () => {
      setupMockFetch()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        const checkIcons = screen.getAllByTestId('check-icon')
        expect(checkIcons.length).toBeGreaterThan(0)
      })
    })

    it('should select conversation on click', async () => {
      setupMockFetch()
      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Plot vs Character Priority')).toBeInTheDocument()
      })

      const conversation = screen.getByText('Plot vs Character Priority')
      await user.click(conversation)

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/conversations/1')
        )
      })
    })
  })

  describe('Messages', () => {
    it('should display messages when conversation selected', async () => {
      setupMockFetch()
      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Plot vs Character Priority')).toBeInTheDocument()
      })

      const conversation = screen.getByText('Plot vs Character Priority')
      await user.click(conversation)

      await waitFor(() => {
        expect(screen.getByText(/focus on plot structure/i)).toBeInTheDocument()
        expect(screen.getByText(/Character motivation/i)).toBeInTheDocument()
      })
    })

    it('should show agent name for each message', async () => {
      setupMockFetch()
      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Plot vs Character Priority')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Plot vs Character Priority'))

      await waitFor(() => {
        expect(screen.getByText('Plot Master')).toBeInTheDocument()
        expect(screen.getByText('Character Developer')).toBeInTheDocument()
      })
    })

    it('should show suggestion badge for suggestion messages', async () => {
      setupMockFetch()
      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Plot vs Character Priority')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Plot vs Character Priority'))

      await waitFor(() => {
        const suggestionBadges = screen.getAllByText('Suggestion')
        expect(suggestionBadges.length).toBe(2) // Both messages are suggestions
      })
    })

    it('should auto-scroll to latest message', async () => {
      setupMockFetch()
      const scrollIntoViewMock = jest.fn()
      Element.prototype.scrollIntoView = scrollIntoViewMock

      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Plot vs Character Priority')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Plot vs Character Priority'))

      await waitFor(() => {
        expect(scrollIntoViewMock).toHaveBeenCalled()
      })
    })
  })

  describe('Sending Messages', () => {
    it('should send message when clicking Send button', async () => {
      setupMockFetch()
      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: async () => ({ id: 3, content: 'New message', ...mockMessages[0] }),
        } as Response)
      )

      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Plot vs Character Priority')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Plot vs Character Priority'))

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Type a message/i)).toBeInTheDocument()
      })

      // Select agent
      const agentSelect = screen.getByRole('combobox')
      await user.selectOptions(agentSelect, '1')

      // Type message
      const input = screen.getByPlaceholderText(/Type a message/i)
      await user.type(input, 'New message')

      // Send
      const sendButton = screen.getByText('Send')
      await user.click(sendButton)

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/conversations/1/messages'),
          expect.objectContaining({
            method: 'POST',
          })
        )
      })
    })

    it('should send message on Enter key', async () => {
      setupMockFetch()
      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: async () => ({ id: 3, ...mockMessages[0] }),
        } as Response)
      )

      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Plot vs Character Priority')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Plot vs Character Priority'))

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Type a message/i)).toBeInTheDocument()
      })

      // Select agent
      const agentSelect = screen.getByRole('combobox')
      await user.selectOptions(agentSelect, '1')

      // Type and press Enter
      const input = screen.getByPlaceholderText(/Type a message/i)
      await user.type(input, 'New message{Enter}')

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/messages'),
          expect.objectContaining({
            method: 'POST',
          })
        )
      })
    })

    it('should clear input after sending', async () => {
      setupMockFetch()
      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: async () => ({ id: 3, ...mockMessages[0] }),
        } as Response)
      )

      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Plot vs Character Priority')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Plot vs Character Priority'))

      const agentSelect = screen.getByRole('combobox')
      await user.selectOptions(agentSelect, '1')

      const input = screen.getByPlaceholderText(/Type a message/i) as HTMLInputElement
      await user.type(input, 'Test message')
      await user.click(screen.getByText('Send'))

      await waitFor(() => {
        expect(input.value).toBe('')
      })
    })

    it('should disable send button when no message or agent', () => {
      setupMockFetch()
      render(<CollaborationWorkspace {...defaultProps} />)

      const sendButton = screen.queryByText('Send')
      if (sendButton) {
        expect(sendButton).toBeDisabled()
      }
    })
  })

  describe('Voting', () => {
    it('should display voting panel when conflict active', async () => {
      const conversationWithVoting = {
        ...mockConversationDetail,
        has_conflict: true,
        voting_options: [
          { id: 1, description: 'Option A', proposed_by_agent_id: 1 },
          { id: 2, description: 'Option B', proposed_by_agent_id: 2 },
        ],
      }

      mockFetch.mockImplementation((url: string | URL | Request) => {
        const urlString = url.toString()
        if (urlString.match(/\/conversations\/\d+$/)) {
          return Promise.resolve({
            ok: true,
            json: async () => conversationWithVoting,
          } as Response)
        }
        if (urlString.includes('/conversations')) {
          return Promise.resolve({
            ok: true,
            json: async () => mockConversations,
          } as Response)
        }
        return Promise.reject(new Error('Unknown URL'))
      })

      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Plot vs Character Priority')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Plot vs Character Priority'))

      await waitFor(() => {
        expect(screen.getByText(/Vote on Options/i)).toBeInTheDocument()
        expect(screen.getByText('Option A')).toBeInTheDocument()
        expect(screen.getByText('Option B')).toBeInTheDocument()
      })
    })

    it('should cast vote when clicking option', async () => {
      const conversationWithVoting = {
        ...mockConversationDetail,
        has_conflict: true,
        voting_options: [
          { id: 1, description: 'Option A', proposed_by_agent_id: 1 },
        ],
      }

      mockFetch.mockImplementation((url: string | URL | Request) => {
        const urlString = url.toString()
        if (urlString.match(/\/conversations\/\d+$/)) {
          return Promise.resolve({
            ok: true,
            json: async () => conversationWithVoting,
          } as Response)
        }
        if (urlString.includes('/cast-vote')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ id: 1, option_id: 1, agent_id: 1 }),
          } as Response)
        }
        if (urlString.includes('/conversations')) {
          return Promise.resolve({
            ok: true,
            json: async () => mockConversations,
          } as Response)
        }
        return Promise.reject(new Error('Unknown URL'))
      })

      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Plot vs Character Priority')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Plot vs Character Priority'))

      await waitFor(() => {
        expect(screen.getByText('Option A')).toBeInTheDocument()
      })

      // Click vote button for an agent
      const voteButtons = screen.getAllByText(/Plot Master|Character Developer/i)
      if (voteButtons.length > 0) {
        await user.click(voteButtons[0])

        await waitFor(() => {
          expect(mockFetch).toHaveBeenCalledWith(
            expect.stringContaining('/cast-vote'),
            expect.objectContaining({
              method: 'POST',
            })
          )
        })
      }
    })
  })

  describe('Memories', () => {
    it('should switch to memories tab', async () => {
      setupMockFetch()
      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      const memoriesTab = screen.getByText('Memories')
      await user.click(memoriesTab)

      await waitFor(() => {
        expect(screen.getByText(/Select Agent/i)).toBeInTheDocument()
      })
    })

    it('should load memories when agent selected', async () => {
      setupMockFetch()
      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await user.click(screen.getByText('Memories'))

      await waitFor(() => {
        expect(screen.getByText(/Select Agent/i)).toBeInTheDocument()
      })

      const agentSelect = screen.getByRole('combobox')
      await user.selectOptions(agentSelect, '1')

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/agents/1/memories')
        )
      })
    })

    it('should display memory importance bar', async () => {
      setupMockFetch()
      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await user.click(screen.getByText('Memories'))

      const agentSelect = screen.getByRole('combobox')
      await user.selectOptions(agentSelect, '1')

      await waitFor(() => {
        expect(screen.getByText('User prefers three-act structure')).toBeInTheDocument()
        expect(screen.getByText(/80%/)).toBeInTheDocument() // 0.8 * 100
      })
    })

    it('should show empty state when no agent selected', async () => {
      setupMockFetch()
      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await user.click(screen.getByText('Memories'))

      await waitFor(() => {
        expect(screen.getByText(/Select an agent/i)).toBeInTheDocument()
      })
    })
  })

  describe('Conversation Actions', () => {
    it('should show resolve button for active conversations', async () => {
      setupMockFetch()
      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Plot vs Character Priority')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Plot vs Character Priority'))

      await waitFor(() => {
        expect(screen.getByText('Resolve')).toBeInTheDocument()
      })
    })

    it('should resolve conversation', async () => {
      setupMockFetch()
      mockFetch.mockImplementationOnce(() =>
        Promise.resolve({
          ok: true,
          json: async () => ({ ...mockConversationDetail, is_resolved: true }),
        } as Response)
      )

      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Plot vs Character Priority')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Plot vs Character Priority'))

      await waitFor(() => {
        expect(screen.getByText('Resolve')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Resolve'))

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/conversations/1/resolve'),
          expect.objectContaining({
            method: 'POST',
          })
        )
      })
    })

    it('should show resolved badge for resolved conversations', async () => {
      setupMockFetch()
      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Dialogue Review Discussion')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Dialogue Review Discussion'))

      await waitFor(() => {
        expect(screen.getByText('Resolved')).toBeInTheDocument()
      })
    })

    it('should disable message input for resolved conversations', async () => {
      mockFetch.mockImplementation((url: string | URL | Request) => {
        const urlString = url.toString()
        if (urlString.match(/\/conversations\/2$/)) {
          return Promise.resolve({
            ok: true,
            json: async () => ({ ...mockConversationDetail, id: 2, is_resolved: true }),
          } as Response)
        }
        if (urlString.includes('/conversations')) {
          return Promise.resolve({
            ok: true,
            json: async () => mockConversations,
          } as Response)
        }
        return Promise.reject(new Error('Unknown URL'))
      })

      const user = userEvent.setup()
      render(<CollaborationWorkspace {...defaultProps} />)

      await waitFor(() => {
        expect(screen.getByText('Dialogue Review Discussion')).toBeInTheDocument()
      })

      await user.click(screen.getByText('Dialogue Review Discussion'))

      await waitFor(() => {
        // Message input should not be present for resolved conversations
        expect(screen.queryByPlaceholderText(/Type a message/i)).not.toBeInTheDocument()
      })
    })
  })
})
