'use client'

import { useState, useEffect, useRef } from 'react'
import { MessageCircle, Send, ThumbsUp, ThumbsDown, Brain, Vote, CheckCircle } from 'lucide-react'

// ==================== TYPES ====================

interface Agent {
  id: number
  name: string
  agent_type: string
}

interface Message {
  id: number
  conversation_id: number
  agent_id: number | null
  content: string
  message_type: string
  is_suggestion: boolean
  suggestion_data: any
  reply_to_message_id: number | null
  reactions: Record<string, number[]>
  created_at: string
}

interface Conversation {
  id: number
  project_id: number
  title: string
  topic: string | null
  participant_agent_ids: number[]
  moderator_agent_id: number | null
  is_active: boolean
  is_resolved: boolean
  has_conflict: boolean
  started_at: string
  ended_at: string | null
  created_at: string
}

interface ConversationDetail extends Conversation {
  messages: Message[]
  resolution_summary: string | null
  conflict_type: string | null
  resolution_strategy: string | null
  voting_options: VotingOption[] | null
}

interface VotingOption {
  id: number
  description: string
  proposed_by_agent_id: number
}

interface Vote {
  id: number
  conversation_id: number
  agent_id: number
  option_id: number
  confidence: number | null
  reasoning: string | null
  created_at: string
}

interface Memory {
  id: number
  agent_id: number
  content: string
  memory_type: string
  importance: number
  access_count: number
  created_at: string
}

// ==================== PROPS ====================

interface CollaborationWorkspaceProps {
  projectId: number
  agents: Agent[]
}

// ==================== MAIN COMPONENT ====================

export default function CollaborationWorkspace({ projectId, agents }: CollaborationWorkspaceProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [selectedConversation, setSelectedConversation] = useState<ConversationDetail | null>(null)
  const [votes, setVotes] = useState<Vote[]>([])
  const [memories, setMemories] = useState<Memory[]>([])
  const [selectedAgent, setSelectedAgent] = useState<number | null>(null)

  const [showNewConversation, setShowNewConversation] = useState(false)
  const [showMemories, setShowMemories] = useState(false)

  const [newMessage, setNewMessage] = useState('')
  const [selectedMessageAgent, setSelectedMessageAgent] = useState<number | null>(null)

  const messagesEndRef = useRef<HTMLDivElement>(null)

  // ==================== DATA FETCHING ====================

  useEffect(() => {
    fetchConversations()
  }, [projectId])

  useEffect(() => {
    if (selectedConversation) {
      fetchConversationDetail(selectedConversation.id)
    }
  }, [selectedConversation?.id])

  useEffect(() => {
    if (selectedAgent && showMemories) {
      fetchMemories(selectedAgent)
    }
  }, [selectedAgent, showMemories])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [selectedConversation?.messages])

  const fetchConversations = async () => {
    const res = await fetch(`/api/projects/${projectId}/conversations`)
    const data = await res.json()
    setConversations(data)
  }

  const fetchConversationDetail = async (conversationId: number) => {
    const res = await fetch(`/api/projects/${projectId}/conversations/${conversationId}`)
    const data = await res.json()
    setSelectedConversation(data)

    // Fetch votes if conversation has voting
    if (data.has_conflict && data.voting_options) {
      // Note: Would need votes endpoint in backend
      setVotes([])
    }
  }

  const fetchMemories = async (agentId: number) => {
    const res = await fetch(`/api/projects/${projectId}/agents/${agentId}/memories?limit=20`)
    const data = await res.json()
    setMemories(data)
  }

  // ==================== ACTIONS ====================

  const createConversation = async (title: string, participantIds: number[]) => {
    const res = await fetch(`/api/projects/${projectId}/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        participant_agent_ids: participantIds,
        topic: 'collaboration',
      }),
    })

    if (res.ok) {
      const newConv = await res.json()
      await fetchConversations()
      setSelectedConversation(newConv)
      setShowNewConversation(false)
    }
  }

  const sendMessage = async () => {
    if (!selectedConversation || !newMessage.trim() || !selectedMessageAgent) return

    const res = await fetch(
      `/api/projects/${projectId}/conversations/${selectedConversation.id}/messages`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: selectedMessageAgent,
          content: newMessage,
          message_type: 'comment',
        }),
      }
    )

    if (res.ok) {
      setNewMessage('')
      await fetchConversationDetail(selectedConversation.id)
    }
  }

  const initiateVoting = async (options: VotingOption[]) => {
    if (!selectedConversation) return

    const res = await fetch(
      `/api/projects/${projectId}/conversations/${selectedConversation.id}/vote`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          voting_options: options,
          resolution_strategy: 'voting',
        }),
      }
    )

    if (res.ok) {
      await fetchConversationDetail(selectedConversation.id)
    }
  }

  const castVote = async (optionId: number, agentId: number) => {
    if (!selectedConversation) return

    const res = await fetch(
      `/api/projects/${projectId}/conversations/${selectedConversation.id}/cast-vote`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: agentId,
          option_id: optionId,
          confidence: 0.8,
        }),
      }
    )

    if (res.ok) {
      await fetchConversationDetail(selectedConversation.id)
    }
  }

  const resolveConversation = async (summary: string) => {
    if (!selectedConversation) return

    const res = await fetch(
      `/api/projects/${projectId}/conversations/${selectedConversation.id}/resolve?resolution_summary=${encodeURIComponent(summary)}`,
      { method: 'POST' }
    )

    if (res.ok) {
      await fetchConversationDetail(selectedConversation.id)
      await fetchConversations()
    }
  }

  // ==================== RENDER ====================

  const getAgentName = (agentId: number | null) => {
    if (!agentId) return 'Nieznany'
    return agents.find(a => a.id === agentId)?.name || `Agent ${agentId}`
  }

  const getAgentColor = (agentId: number | null) => {
    if (!agentId) return 'bg-gray-100 text-gray-700'
    const colors = [
      'bg-blue-100 text-blue-700',
      'bg-purple-100 text-purple-700',
      'bg-green-100 text-green-700',
      'bg-yellow-100 text-yellow-700',
      'bg-red-100 text-red-700',
      'bg-indigo-100 text-indigo-700',
    ]
    return colors[agentId % colors.length]
  }

  return (
    <div className="h-full flex">
      {/* Left Sidebar: Conversations List */}
      <div className="w-80 border-r border-gray-200 bg-white flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <MessageCircle className="w-5 h-5" />
              Konwersacje
            </h2>
            <button
              onClick={() => setShowNewConversation(true)}
              className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg"
              title="Nowa Konwersacja"
            >
              <MessageCircle className="w-5 h-5" />
            </button>
          </div>

          <div className="flex gap-2 text-xs">
            <button
              onClick={() => setShowMemories(false)}
              className={`flex-1 px-3 py-2 rounded ${
                !showMemories ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-700'
              }`}
            >
              Dyskusje
            </button>
            <button
              onClick={() => setShowMemories(true)}
              className={`flex-1 px-3 py-2 rounded flex items-center justify-center gap-1 ${
                showMemories ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-700'
              }`}
            >
              <Brain className="w-3 h-3" />
              Pamięć
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {!showMemories ? (
            // Conversations list
            conversations.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <MessageCircle className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                <p>Brak konwersacji</p>
              </div>
            ) : (
              conversations.map(conv => (
                <div
                  key={conv.id}
                  onClick={() => setSelectedConversation(conv as any)}
                  className={`p-3 rounded-lg cursor-pointer transition-colors ${
                    selectedConversation?.id === conv.id
                      ? 'bg-indigo-50 border-indigo-200'
                      : 'hover:bg-gray-50 border-transparent'
                  } border`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-medium text-gray-900 text-sm">{conv.title}</h3>
                    {conv.has_conflict && <Vote className="w-4 h-4 text-orange-500" />}
                    {conv.is_resolved && <CheckCircle className="w-4 h-4 text-green-500" />}
                  </div>
                  <p className="text-xs text-gray-600">
                    {conv.participant_agent_ids.length} agents participating
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(conv.created_at).toLocaleString()}
                  </p>
                </div>
              ))
            )
          ) : (
            // Memories list
            <div className="space-y-3">
              <div className="mb-3">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Wybierz Agenta
                </label>
                <select
                  value={selectedAgent || ''}
                  onChange={(e) => setSelectedAgent(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                >
                  <option value="">Wybierz agenta...</option>
                  {agents.map(agent => (
                    <option key={agent.id} value={agent.id}>
                      {agent.name}
                    </option>
                  ))}
                </select>
              </div>

              {memories.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Brain className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                  <p className="text-sm">
                    {selectedAgent ? 'Brak wspomnień' : 'Wybierz agenta'}
                  </p>
                </div>
              ) : (
                memories.map(memory => (
                  <div key={memory.id} className="p-3 border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-indigo-600 uppercase">
                        {memory.memory_type}
                      </span>
                      <span className="text-xs text-gray-500">
                        {memory.access_count} access
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 line-clamp-3">{memory.content}</p>
                    <div className="mt-2 flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                        <div
                          className="bg-indigo-600 h-1.5 rounded-full"
                          style={{ width: `${memory.importance * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500">
                        {(memory.importance * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* Main Content: Messages or Voting */}
      <div className="flex-1 flex flex-col bg-gray-50">
        {selectedConversation ? (
          <>
            {/* Header */}
            <div className="bg-white border-b border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">
                    {selectedConversation.title}
                  </h2>
                  <p className="text-sm text-gray-600">
                    {selectedConversation.participant_agent_ids.length} agentów uczestniczy
                  </p>
                </div>
                <div className="flex gap-2">
                  {selectedConversation.has_conflict ? (
                    <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-lg text-sm flex items-center gap-1">
                      <Vote className="w-4 h-4" />
                      Głosowanie Aktywne
                    </span>
                  ) : selectedConversation.is_resolved ? (
                    <span className="px-3 py-1 bg-green-100 text-green-700 rounded-lg text-sm flex items-center gap-1">
                      <CheckCircle className="w-4 h-4" />
                      Rozwiązane
                    </span>
                  ) : (
                    <button
                      onClick={() => resolveConversation('Consensus reached')}
                      className="px-3 py-1 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700"
                    >
                      Rozwiąż
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Voting Panel (if active) */}
            {selectedConversation.has_conflict && selectedConversation.voting_options && (
              <div className="bg-yellow-50 border-b border-yellow-200 p-4">
                <h3 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                  <Vote className="w-5 h-5 text-orange-600" />
                  Głosuj na Opcje
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {selectedConversation.voting_options.map((option) => (
                    <div key={option.id} className="bg-white border border-gray-200 rounded-lg p-3">
                      <p className="text-sm text-gray-900 mb-2">{option.description}</p>
                      <p className="text-xs text-gray-600 mb-2">
                        Zaproponowane przez {getAgentName(option.proposed_by_agent_id)}
                      </p>
                      <div className="flex gap-2">
                        {agents.map(agent => (
                          <button
                            key={agent.id}
                            onClick={() => castVote(option.id, agent.id)}
                            className="flex-1 px-2 py-1 bg-indigo-100 text-indigo-700 rounded text-xs hover:bg-indigo-200"
                          >
                            {agent.name}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {selectedConversation.messages.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <MessageCircle className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                  <p>Brak wiadomości</p>
                </div>
              ) : (
                selectedConversation.messages.map(message => (
                  <div key={message.id} className="flex gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${
                      getAgentColor(message.agent_id)
                    }`}>
                      {getAgentName(message.agent_id).charAt(0)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-gray-900 text-sm">
                          {getAgentName(message.agent_id)}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(message.created_at).toLocaleTimeString()}
                        </span>
                        {message.is_suggestion && (
                          <span className="px-2 py-0.5 bg-yellow-100 text-yellow-700 rounded text-xs">
                            Suggestion
                          </span>
                        )}
                      </div>
                      <div className="bg-white border border-gray-200 rounded-lg p-3">
                        <p className="text-sm text-gray-900">{message.content}</p>
                      </div>
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            {!selectedConversation.is_resolved && (
              <div className="bg-white border-t border-gray-200 p-4">
                <div className="flex gap-3">
                  <select
                    value={selectedMessageAgent || ''}
                    onChange={(e) => setSelectedMessageAgent(Number(e.target.value))}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value="">Wybierz agenta...</option>
                    {agents
                      .filter(a => selectedConversation.participant_agent_ids.includes(a.id))
                      .map(agent => (
                        <option key={agent.id} value={agent.id}>
                          {agent.name}
                        </option>
                      ))}
                  </select>
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Wpisz wiadomość..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!newMessage.trim() || !selectedMessageAgent}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    <Send className="w-4 h-4" />
                    Wyślij
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <MessageCircle className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <p className="text-lg">Wybierz konwersację lub utwórz nową</p>
            </div>
          </div>
        )}
      </div>

      {/* New Conversation Modal */}
      {showNewConversation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Nowa Konwersacja</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tytuł</label>
                <input
                  type="text"
                  id="conv-title"
                  placeholder="Temat dyskusji..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Wybierz Agentów (min 2)
                </label>
                <div className="space-y-2">
                  {agents.map(agent => (
                    <label key={agent.id} className="flex items-center gap-2">
                      <input type="checkbox" value={agent.id} className="rounded" />
                      <span className="text-sm">{agent.name}</span>
                    </label>
                  ))}
                </div>
              </div>
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setShowNewConversation(false)}
                  className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  Anuluj
                </button>
                <button
                  onClick={() => {
                    const title = (document.getElementById('conv-title') as HTMLInputElement).value
                    const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked')
                    const participantIds = Array.from(checkboxes).map(cb => Number((cb as HTMLInputElement).value))
                    if (title && participantIds.length >= 2) {
                      createConversation(title, participantIds)
                    }
                  }}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Utwórz
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
