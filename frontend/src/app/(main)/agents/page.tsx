'use client'

import { useState, useEffect } from 'react'
import { Plus, Bot, CheckCircle2, XCircle, Clock, AlertCircle, TrendingUp, Users } from 'lucide-react'
import { useTranslations } from 'next-intl'

// ==================== TYPES ====================

interface Agent {
  id: number
  project_id: number
  name: string
  agent_type: string
  role: string
  description: string | null
  is_active: boolean
  is_busy: boolean
  tasks_completed: number
  tasks_failed: number
  user_satisfaction_score: number | null
  created_at: string
  updated_at: string
}

interface Task {
  id: number
  project_id: number
  agent_id: number | null
  title: string
  description: string
  task_type: string | null
  status: string
  priority: string
  assigned_at: string | null
  started_at: string | null
  completed_at: string | null
  deadline: string | null
  user_approved: boolean | null
  user_rating: number | null
  created_at: string
  updated_at: string
}

interface TaskQueue {
  tasks: Task[]
  total: number
  pending_count: number
  in_progress_count: number
  completed_count: number
}

interface ProjectStats {
  total_agents: number
  active_agents: number
  busy_agents: number
  agents_by_type: Record<string, number>
  total_tasks: number
  completed_tasks: number
  failed_tasks: number
  average_satisfaction: number | null
}

// ==================== CONSTANTS ====================

const AGENT_TYPE_COLORS: Record<string, string> = {
  plotting: 'bg-blue-100 text-blue-700 border-blue-300',
  character: 'bg-purple-100 text-purple-700 border-purple-300',
  dialogue: 'bg-green-100 text-green-700 border-green-300',
  continuity: 'bg-yellow-100 text-yellow-700 border-yellow-300',
  qc: 'bg-red-100 text-red-700 border-red-300',
  pacing: 'bg-indigo-100 text-indigo-700 border-indigo-300',
  theme: 'bg-pink-100 text-pink-700 border-pink-300',
  worldbuilding: 'bg-teal-100 text-teal-700 border-teal-300',
}

const PRIORITY_COLORS: Record<string, string> = {
  low: 'bg-gray-100 text-gray-600',
  medium: 'bg-blue-100 text-blue-600',
  high: 'bg-orange-100 text-orange-600',
  critical: 'bg-red-100 text-red-600',
}

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-gray-100 text-gray-700',
  assigned: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-yellow-100 text-yellow-700',
  completed: 'bg-green-100 text-green-700',
  failed: 'bg-red-100 text-red-700',
  cancelled: 'bg-gray-100 text-gray-500',
  blocked: 'bg-orange-100 text-orange-700',
}

// ==================== MAIN COMPONENT ====================

export default function AgentDashboard() {
  const t = useTranslations('agents')
  const tCommon = useTranslations('common')

  const [agents, setAgents] = useState<Agent[]>([])
  const [taskQueue, setTaskQueue] = useState<TaskQueue | null>(null)
  const [projectStats, setProjectStats] = useState<ProjectStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedAgent, setSelectedAgent] = useState<number | null>(null)
  const [showCreateTask, setShowCreateTask] = useState(false)

  const projectId = 1 // TODO: Get from context

  // ==================== DATA FETCHING ====================

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 10000) // Refresh every 10s
    return () => clearInterval(interval)
  }, [selectedAgent])

  const fetchData = async () => {
    try {
      await Promise.all([
        fetchAgents(),
        fetchTaskQueue(),
        fetchProjectStats(),
      ])
    } finally {
      setLoading(false)
    }
  }

  const fetchAgents = async () => {
    const res = await fetch(`/api/projects/${projectId}/agents`)
    const data = await res.json()
    setAgents(data)
  }

  const fetchTaskQueue = async () => {
    const params = new URLSearchParams()
    if (selectedAgent) params.append('agent_id', selectedAgent.toString())

    const res = await fetch(`/api/projects/${projectId}/tasks?${params}`)
    const data = await res.json()
    setTaskQueue(data)
  }

  const fetchProjectStats = async () => {
    const res = await fetch(`/api/projects/${projectId}/agent-collaboration/statistics`)
    const data = await res.json()
    setProjectStats(data)
  }

  // ==================== ACTIONS ====================

  const initializeAgents = async () => {
    const res = await fetch(`/api/projects/${projectId}/agents/initialize`, {
      method: 'POST',
    })
    if (res.ok) {
      await fetchAgents()
    }
  }

  const toggleAgentActive = async (agentId: number, isActive: boolean) => {
    await fetch(`/api/projects/${projectId}/agents/${agentId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_active: !isActive }),
    })
    await fetchAgents()
  }

  const startTask = async (taskId: number) => {
    await fetch(`/api/projects/${projectId}/tasks/${taskId}/start`, {
      method: 'POST',
    })
    await fetchTaskQueue()
  }

  const completeTask = async (taskId: number) => {
    await fetch(`/api/projects/${projectId}/tasks/${taskId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ result: {}, user_rating: 4.0 }),
    })
    await fetchTaskQueue()
    await fetchAgents()
  }

  // ==================== RENDER ====================

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">{t('loading')}</p>
        </div>
      </div>
    )
  }

  const successRate = projectStats && projectStats.total_tasks > 0
    ? ((projectStats.completed_tasks / projectStats.total_tasks) * 100).toFixed(1)
    : 0

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Bot className="w-8 h-8 text-indigo-600" />
              {t('title')}
            </h1>
            <p className="text-gray-600 mt-1">{t('subtitle')}</p>
          </div>
          <div className="flex gap-3">
            {agents.length === 0 && (
              <button
                onClick={initializeAgents}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
              >
                <Users className="w-4 h-4" />
                {t('initializeTeam')}
              </button>
            )}
            <button
              onClick={() => setShowCreateTask(true)}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              {t('createTask')}
            </button>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      {projectStats && (
        <div className="grid grid-cols-6 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{t('stats.totalAgents')}</p>
                <p className="text-2xl font-bold text-gray-900">{projectStats.total_agents}</p>
              </div>
              <Bot className="w-8 h-8 text-indigo-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{t('stats.active')}</p>
                <p className="text-2xl font-bold text-green-600">{projectStats.active_agents}</p>
              </div>
              <CheckCircle2 className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{t('stats.busy')}</p>
                <p className="text-2xl font-bold text-yellow-600">{projectStats.busy_agents}</p>
              </div>
              <Clock className="w-8 h-8 text-yellow-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{t('stats.totalTasks')}</p>
                <p className="text-2xl font-bold text-gray-900">{projectStats.total_tasks}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{t('stats.successRate')}</p>
                <p className="text-2xl font-bold text-green-600">{successRate}%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">{t('stats.satisfaction')}</p>
                <p className="text-2xl font-bold text-indigo-600">
                  {projectStats.average_satisfaction
                    ? (projectStats.average_satisfaction * 100).toFixed(0) + '%'
                    : 'N/A'
                  }
                </p>
              </div>
              <CheckCircle2 className="w-8 h-8 text-indigo-600" />
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-6">
        {/* Left Panel: Agent List */}
        <div className="col-span-1">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Bot className="w-5 h-5" />
                {t('agentsTitle')} ({agents.length})
              </h2>
            </div>
            <div className="p-4 space-y-3 max-h-[calc(100vh-400px)] overflow-y-auto">
              {agents.length === 0 ? (
                <div className="text-center py-8">
                  <Bot className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-600 mb-3">{t('noAgents')}</p>
                  <button
                    onClick={initializeAgents}
                    className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
                  >
                    {t('initializeTeam')}
                  </button>
                </div>
              ) : (
                agents.map(agent => (
                  <div
                    key={agent.id}
                    onClick={() => setSelectedAgent(agent.id === selectedAgent ? null : agent.id)}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedAgent === agent.id
                        ? 'border-indigo-300 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-gray-900">{agent.name}</h3>
                      <div className="flex items-center gap-2">
                        {agent.is_busy && (
                          <Clock className="w-4 h-4 text-yellow-600" />
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            toggleAgentActive(agent.id, agent.is_active)
                          }}
                          className={`w-2 h-2 rounded-full ${
                            agent.is_active ? 'bg-green-500' : 'bg-gray-300'
                          }`}
                        />
                      </div>
                    </div>

                    <div className={`inline-block px-2 py-1 rounded text-xs font-medium mb-2 ${
                      AGENT_TYPE_COLORS[agent.agent_type] || 'bg-gray-100 text-gray-700'
                    }`}>
                      {t(`agentTypes.${agent.agent_type}`)}
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 mt-2">
                      <div>
                        <span className="text-green-600 font-medium">{agent.tasks_completed}</span> {tCommon('completed')}
                      </div>
                      <div>
                        <span className="text-red-600 font-medium">{agent.tasks_failed}</span> {tCommon('failed')}
                      </div>
                    </div>

                    {agent.user_satisfaction_score && (
                      <div className="mt-2 text-xs text-gray-600">
                        {t('satisfactionLabel')}: <span className="font-medium text-indigo-600">
                          {(agent.user_satisfaction_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Panel: Task Queue */}
        <div className="col-span-2">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <AlertCircle className="w-5 h-5" />
                  {t('taskQueue')}
                  {selectedAgent && (
                    <span className="text-sm font-normal text-gray-600">
                      ({t('filteredByAgent')})
                    </span>
                  )}
                </h2>
                {taskQueue && (
                  <div className="flex gap-4 text-sm">
                    <span className="text-gray-600">
                      <span className="font-medium text-gray-900">{taskQueue.pending_count}</span> {t('queueStats.pending')}
                    </span>
                    <span className="text-gray-600">
                      <span className="font-medium text-yellow-600">{taskQueue.in_progress_count}</span> {t('queueStats.inProgress')}
                    </span>
                    <span className="text-gray-600">
                      <span className="font-medium text-green-600">{taskQueue.completed_count}</span> {t('queueStats.completed')}
                    </span>
                  </div>
                )}
              </div>
            </div>

            <div className="p-4 max-h-[calc(100vh-400px)] overflow-y-auto">
              {taskQueue && taskQueue.tasks.length === 0 ? (
                <div className="text-center py-12">
                  <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-600">{t('noTasks')}</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {taskQueue?.tasks.map(task => (
                    <div
                      key={task.id}
                      className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900 mb-1">{task.title}</h3>
                          <p className="text-sm text-gray-600 line-clamp-2">{task.description}</p>
                        </div>
                        <div className="flex gap-2 ml-4">
                          {task.status === 'assigned' && (
                            <button
                              onClick={() => startTask(task.id)}
                              className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded text-sm hover:bg-yellow-200"
                            >
                              {t('actions.start')}
                            </button>
                          )}
                          {task.status === 'in_progress' && (
                            <button
                              onClick={() => completeTask(task.id)}
                              className="px-3 py-1 bg-green-100 text-green-700 rounded text-sm hover:bg-green-200"
                            >
                              {t('actions.complete')}
                            </button>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 text-xs">
                        <span className={`px-2 py-1 rounded font-medium ${
                          PRIORITY_COLORS[task.priority] || 'bg-gray-100 text-gray-600'
                        }`}>
                          {t(`priority.${task.priority}`)}
                        </span>
                        <span className={`px-2 py-1 rounded font-medium ${
                          STATUS_COLORS[task.status] || 'bg-gray-100 text-gray-600'
                        }`}>
                          {t(`status.${task.status}`)}
                        </span>
                        {task.task_type && (
                          <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded">
                            {task.task_type}
                          </span>
                        )}
                        {task.agent_id && (
                          <span className="text-gray-600">
                            {t('agentLabel')}: {agents.find(a => a.id === task.agent_id)?.name || task.agent_id}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
