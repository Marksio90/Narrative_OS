'use client'

import { useState, useEffect } from 'react'
import { Target, CheckCircle, XCircle, Clock, AlertCircle, TrendingUp, Award } from 'lucide-react'

interface Goal {
  id: number
  arc_id: number
  goal_description: string
  status: string
  progress_percentage: number
  target_chapter?: number
  completed_chapter?: number
  obstacles?: string
  notes?: string
  created_at: string
  updated_at: string
}

interface GoalProgressVisualizationProps {
  characterId: number
}

export default function GoalProgressVisualization({ characterId }: GoalProgressVisualizationProps) {
  const [goals, setGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'active' | 'completed' | 'failed' | 'abandoned'>('all')

  useEffect(() => {
    fetchGoals()
  }, [characterId])

  const fetchGoals = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/character-arcs/character/${characterId}/goals`)
      if (response.ok) {
        const data = await response.json()
        setGoals(data.goals || [])
      }
    } catch (error) {
      console.error('Failed to fetch goals:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    const icons: Record<string, any> = {
      active: Clock,
      completed: CheckCircle,
      failed: XCircle,
      abandoned: AlertCircle,
    }
    const Icon = icons[status] || Target
    return <Icon className="w-5 h-5" />
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'bg-blue-100 text-blue-700 border-blue-200',
      completed: 'bg-green-100 text-green-700 border-green-200',
      failed: 'bg-red-100 text-red-700 border-red-200',
      abandoned: 'bg-gray-100 text-gray-700 border-gray-200',
    }
    return colors[status] || 'bg-gray-100 text-gray-700 border-gray-200'
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      active: 'Active',
      completed: 'Completed',
      failed: 'Failed',
      abandoned: 'Abandoned',
    }
    return labels[status] || status
  }

  const getProgressColor = (progress: number) => {
    if (progress >= 75) return 'bg-green-600'
    if (progress >= 50) return 'bg-blue-600'
    if (progress >= 25) return 'bg-yellow-600'
    return 'bg-gray-400'
  }

  const filteredGoals = goals.filter((goal) => {
    if (filter === 'all') return true
    return goal.status === filter
  })

  const sortedGoals = [...filteredGoals].sort((a, b) => {
    // Sort by status priority (active > completed > failed > abandoned)
    const statusPriority: Record<string, number> = {
      active: 1,
      completed: 2,
      failed: 3,
      abandoned: 4,
    }
    const priorityDiff = (statusPriority[a.status] || 5) - (statusPriority[b.status] || 5)
    if (priorityDiff !== 0) return priorityDiff

    // Then by progress (descending)
    return b.progress_percentage - a.progress_percentage
  })

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-600">Loading goals...</div>
      </div>
    )
  }

  if (goals.length === 0) {
    return (
      <div className="text-center py-12">
        <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No goals tracked yet</p>
        <p className="text-sm text-gray-500 mt-2">Create goals to track character motivations and objectives</p>
      </div>
    )
  }

  // Calculate statistics
  const activeGoals = goals.filter((g) => g.status === 'active')
  const completedGoals = goals.filter((g) => g.status === 'completed')
  const failedGoals = goals.filter((g) => g.status === 'failed')
  const avgProgress = activeGoals.length > 0
    ? activeGoals.reduce((sum, g) => sum + g.progress_percentage, 0) / activeGoals.length
    : 0

  return (
    <div className="space-y-6">
      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
          <div className="flex items-center gap-2 mb-1">
            <Clock className="w-4 h-4 text-blue-600" />
            <span className="text-xs font-medium text-gray-600">Active Goals</span>
          </div>
          <div className="text-2xl font-bold text-blue-600">{activeGoals.length}</div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
          <div className="flex items-center gap-2 mb-1">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <span className="text-xs font-medium text-gray-600">Completed</span>
          </div>
          <div className="text-2xl font-bold text-green-600">{completedGoals.length}</div>
        </div>

        <div className="bg-gradient-to-br from-red-50 to-rose-50 rounded-lg p-4 border border-red-200">
          <div className="flex items-center gap-2 mb-1">
            <XCircle className="w-4 h-4 text-red-600" />
            <span className="text-xs font-medium text-gray-600">Failed</span>
          </div>
          <div className="text-2xl font-bold text-red-600">{failedGoals.length}</div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="w-4 h-4 text-purple-600" />
            <span className="text-xs font-medium text-gray-600">Avg Progress</span>
          </div>
          <div className="text-2xl font-bold text-purple-600">{Math.round(avgProgress)}%</div>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="flex items-center gap-2 flex-wrap">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'all'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          All Goals ({goals.length})
        </button>
        <button
          onClick={() => setFilter('active')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'active'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Active ({activeGoals.length})
        </button>
        <button
          onClick={() => setFilter('completed')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'completed'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Completed ({completedGoals.length})
        </button>
        <button
          onClick={() => setFilter('failed')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'failed'
              ? 'bg-red-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Failed ({failedGoals.length})
        </button>
      </div>

      {/* Goals Overview Chart */}
      {activeGoals.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Goals Progress</h3>
          <div className="space-y-3">
            {activeGoals
              .sort((a, b) => b.progress_percentage - a.progress_percentage)
              .map((goal) => (
                <div key={goal.id} className="bg-white rounded-lg p-3 border border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-900 flex-1 truncate pr-4">
                      {goal.goal_description}
                    </span>
                    <span className="text-sm font-bold text-gray-700">
                      {Math.round(goal.progress_percentage)}%
                    </span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getProgressColor(goal.progress_percentage)} transition-all`}
                      style={{ width: `${goal.progress_percentage}%` }}
                    />
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Goals List */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Goals</h3>
        {sortedGoals.length === 0 ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No goals in this category</p>
          </div>
        ) : (
          <div className="space-y-4">
            {sortedGoals.map((goal) => (
              <div
                key={goal.id}
                className="bg-white border-2 rounded-lg p-5 hover:border-purple-300 transition-colors"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-start gap-3 flex-1">
                    <div className={`p-2 rounded-lg ${getStatusColor(goal.status)}`}>
                      {getStatusIcon(goal.status)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-gray-900 mb-1">{goal.goal_description}</h4>
                      <div className="flex items-center gap-3 text-xs text-gray-600">
                        <span className={`px-2 py-1 rounded border ${getStatusColor(goal.status)}`}>
                          {getStatusLabel(goal.status)}
                        </span>
                        {goal.target_chapter && (
                          <span className="flex items-center gap-1">
                            <Target className="w-3 h-3" />
                            Target: Ch. {goal.target_chapter}
                          </span>
                        )}
                        {goal.completed_chapter && (
                          <span className="flex items-center gap-1">
                            <Award className="w-3 h-3 text-green-600" />
                            Completed: Ch. {goal.completed_chapter}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Progress Bar */}
                {goal.status === 'active' && (
                  <div className="mb-3">
                    <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                      <span>Progress</span>
                      <span className="font-medium">{Math.round(goal.progress_percentage)}%</span>
                    </div>
                    <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${getProgressColor(goal.progress_percentage)} transition-all`}
                        style={{ width: `${goal.progress_percentage}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Obstacles */}
                {goal.obstacles && (
                  <div className="mb-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="w-4 h-4 text-orange-600 mt-0.5 flex-shrink-0" />
                      <div>
                        <div className="text-xs font-semibold text-orange-900 mb-1">Obstacles</div>
                        <p className="text-sm text-orange-800">{goal.obstacles}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Notes */}
                {goal.notes && (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-sm text-blue-900">{goal.notes}</p>
                  </div>
                )}

                {/* Footer */}
                <div className="mt-3 pt-3 border-t border-gray-200 flex items-center justify-between text-xs text-gray-500">
                  <span>Created: {new Date(goal.created_at).toLocaleDateString()}</span>
                  <span>Updated: {new Date(goal.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Success Rate Card */}
      {completedGoals.length + failedGoals.length > 0 && (
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg p-6 border border-indigo-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Goal Success Rate</h3>
              <p className="text-sm text-gray-600">
                {completedGoals.length} completed out of {completedGoals.length + failedGoals.length} resolved goals
              </p>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold text-indigo-600">
                {Math.round((completedGoals.length / (completedGoals.length + failedGoals.length)) * 100)}%
              </div>
              <div className="text-sm text-gray-600 mt-1">Success Rate</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
