'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSession } from 'next-auth/react'
import { useTranslations } from 'next-intl'
import axios from 'axios'
import {
  GitBranch,
  Plus,
  Filter,
  AlertTriangle,
  TrendingUp,
  Clock,
  Zap,
  Eye,
  CheckCircle,
  XCircle,
  BarChart3,
  FileText,
  Search
} from 'lucide-react'
import ConsequenceGraph from '@/components/ConsequenceGraph'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface StoryEvent {
  id: number
  project_id: number
  scene_id?: number
  chapter_number?: number
  title: string
  description: string
  event_type: string
  magnitude: number
  emotional_impact?: number
  causes: number[]
  effects: number[]
  ai_analysis?: any
  extracted_at?: string
  created_at: string
  updated_at: string
}

interface Consequence {
  id: number
  source_event_id: number
  target_event_id?: number
  description: string
  probability: number
  severity: number
  timeframe: string
  status: string
  plot_impact?: string
  affected_entities: {
    characters?: number[]
    locations?: number[]
    threads?: number[]
  }
  ai_prediction?: any
  predicted_at?: string
  realized_at?: string
  invalidated_at?: string
  invalidation_reason?: string
  created_at: string
  updated_at: string
}

interface ConsequenceStats {
  total_events: number
  total_consequences: number
  potential_consequences: number
  active_consequences: number
  realized_consequences: number
  invalidated_consequences: number
  avg_consequences_per_event: number
  events_by_type: { [key: string]: number }
  consequences_by_timeframe: { [key: string]: number }
}

export default function ConsequencesPage() {
  const t = useTranslations('consequences')
  const tCommon = useTranslations('common')
  const { data: session } = useSession()
  const queryClient = useQueryClient()
  const [projectId] = useState(1) // TODO: Get from context
  const [selectedChapter, setSelectedChapter] = useState<number | null>(null)
  const [filterStatus, setFilterStatus] = useState<string[]>(['potential', 'active'])
  const [filterTimeframe, setFilterTimeframe] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [showGraph, setShowGraph] = useState(false)

  // Fetch events
  const { data: eventsData, isLoading: eventsLoading } = useQuery<StoryEvent[]>({
    queryKey: ['events', projectId, selectedChapter],
    queryFn: async () => {
      const params = new URLSearchParams({ project_id: projectId.toString() })
      if (selectedChapter) params.append('chapter_number', selectedChapter.toString())

      const res = await axios.get(`${API_URL}/api/consequences/events?${params}`)
      return res.data
    },
    enabled: !!projectId,
  })

  // Fetch statistics
  const { data: stats, isLoading: statsLoading } = useQuery<ConsequenceStats>({
    queryKey: ['consequence-stats', projectId],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/consequences/stats?project_id=${projectId}`)
      return res.data
    },
    enabled: !!projectId,
  })

  // Fetch active consequences
  const { data: activeConsequences } = useQuery<Consequence[]>({
    queryKey: ['active-consequences', projectId, selectedChapter],
    queryFn: async () => {
      const params = new URLSearchParams({ project_id: projectId.toString() })
      if (selectedChapter) params.append('chapter_number', selectedChapter.toString())

      const res = await axios.get(`${API_URL}/api/consequences/active?${params}`)
      return res.data.consequences
    },
    enabled: !!projectId,
  })

  // Fetch graph data
  const { data: graphData } = useQuery({
    queryKey: ['consequence-graph', projectId, selectedChapter],
    queryFn: async () => {
      const params = new URLSearchParams({ project_id: projectId.toString() })
      if (selectedChapter) {
        params.append('start_chapter', selectedChapter.toString())
        params.append('end_chapter', selectedChapter.toString())
      }

      const res = await axios.get(`${API_URL}/api/consequences/graph?${params}`)
      return res.data
    },
    enabled: !!projectId && showGraph,
  })

  const events = eventsData || []
  const consequences = activeConsequences || []

  // Filter consequences
  const filteredConsequences = consequences
    .filter(c => filterStatus.length === 0 || filterStatus.includes(c.status))
    .filter(c => !filterTimeframe || c.timeframe === filterTimeframe)
    .filter(c =>
      !searchQuery ||
      c.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.plot_impact?.toLowerCase().includes(searchQuery.toLowerCase())
    )

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'potential':
        return <Eye className="h-4 w-4 text-purple-600" />
      case 'active':
        return <AlertTriangle className="h-4 w-4 text-amber-600" />
      case 'realized':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'invalidated':
        return <XCircle className="h-4 w-4 text-gray-600" />
      default:
        return null
    }
  }

  const getTimeframeIcon = (timeframe: string) => {
    switch (timeframe) {
      case 'immediate':
        return <Zap className="h-4 w-4 text-red-600" />
      case 'short_term':
        return <Clock className="h-4 w-4 text-amber-600" />
      case 'medium_term':
        return <TrendingUp className="h-4 w-4 text-blue-600" />
      case 'long_term':
        return <TrendingUp className="h-4 w-4 text-purple-600" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg">
              <GitBranch className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                {t('title')}
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                {t('subtitle')}
              </p>
            </div>
          </div>

          <button
            onClick={() => setShowGraph(!showGraph)}
            className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
          >
            <GitBranch className="h-5 w-5" />
            <span>{showGraph ? 'Ukryj Graf' : 'Pokaż Graf'}</span>
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center space-x-2 mb-1">
              <FileText className="h-4 w-4 text-blue-500" />
              <span className="text-sm text-gray-600 dark:text-gray-400">Wydarzenia</span>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {stats.total_events}
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center space-x-2 mb-1">
              <GitBranch className="h-4 w-4 text-purple-500" />
              <span className="text-sm text-gray-600 dark:text-gray-400">Konsekwencje</span>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {stats.total_consequences}
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center space-x-2 mb-1">
              <AlertTriangle className="h-4 w-4 text-amber-500" />
              <span className="text-sm text-gray-600 dark:text-gray-400">Aktywne</span>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {stats.active_consequences}
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center space-x-2 mb-1">
              <BarChart3 className="h-4 w-4 text-green-500" />
              <span className="text-sm text-gray-600 dark:text-gray-400">Średnia/Wydarzenie</span>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {stats.avg_consequences_per_event.toFixed(1)}
            </p>
          </div>
        </div>
      )}

      {/* Graph Visualization */}
      {showGraph && graphData && (
        <ConsequenceGraph
          events={graphData.events}
          consequences={graphData.consequences}
          onClose={() => setShowGraph(false)}
        />
      )}

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="h-5 w-5 text-gray-600" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filtry:</span>
            </div>

            {/* Status filters */}
            <div className="flex items-center space-x-2">
              {['potential', 'active', 'realized', 'invalidated'].map(status => (
                <button
                  key={status}
                  onClick={() =>
                    setFilterStatus(prev =>
                      prev.includes(status)
                        ? prev.filter(s => s !== status)
                        : [...prev, status]
                    )
                  }
                  className={`px-3 py-1 rounded-full text-xs font-medium transition ${
                    filterStatus.includes(status)
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {getStatusIcon(status)}
                  <span className="ml-1 capitalize">{status}</span>
                </button>
              ))}
            </div>

            {/* Timeframe filter */}
            <select
              value={filterTimeframe || ''}
              onChange={(e) => setFilterTimeframe(e.target.value || null)}
              className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="">Wszystkie Timeframy</option>
              <option value="immediate">Natychmiastowe</option>
              <option value="short_term">Krótkoterminowe</option>
              <option value="medium_term">Średnioterminowe</option>
              <option value="long_term">Długoterminowe</option>
            </select>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Szukaj konsekwencji..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
        </div>
      </div>

      {/* Consequences List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Konsekwencje ({filteredConsequences.length})
          </h2>
        </div>

        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {filteredConsequences.map((consequence) => {
            const sourceEvent = events.find(e => e.id === consequence.source_event_id)

            return (
              <div
                key={consequence.id}
                className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* Source event */}
                    {sourceEvent && (
                      <div className="mb-2">
                        <span className="text-xs text-gray-500">Źródło:</span>
                        <span className="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                          {sourceEvent.title}
                        </span>
                      </div>
                    )}

                    {/* Consequence description */}
                    <p className="text-base font-medium text-gray-900 dark:text-white mb-2">
                      {consequence.description}
                    </p>

                    {/* Plot impact */}
                    {consequence.plot_impact && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 italic mb-3">
                        {consequence.plot_impact}
                      </p>
                    )}

                    {/* Metrics */}
                    <div className="flex items-center space-x-4">
                      {/* Status */}
                      <div className="flex items-center space-x-1">
                        {getStatusIcon(consequence.status)}
                        <span className="text-xs text-gray-600 capitalize">{consequence.status}</span>
                      </div>

                      {/* Timeframe */}
                      <div className="flex items-center space-x-1">
                        {getTimeframeIcon(consequence.timeframe)}
                        <span className="text-xs text-gray-600 capitalize">
                          {consequence.timeframe.replace('_', ' ')}
                        </span>
                      </div>

                      {/* Probability */}
                      <div className="flex items-center space-x-1">
                        <span className="text-xs text-gray-600">Prawdopodobieństwo:</span>
                        <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-purple-600"
                            style={{ width: `${consequence.probability * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-medium text-gray-900">
                          {Math.round(consequence.probability * 100)}%
                        </span>
                      </div>

                      {/* Severity */}
                      <div className="flex items-center space-x-1">
                        <span className="text-xs text-gray-600">Dotkliwość:</span>
                        <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-red-600"
                            style={{ width: `${consequence.severity * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-medium text-gray-900">
                          {Math.round(consequence.severity * 100)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )
          })}

          {filteredConsequences.length === 0 && (
            <div className="p-12 text-center">
              <GitBranch className="h-12 w-12 mx-auto text-gray-300 mb-4" />
              <p className="text-gray-500">{t('noEvents')}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
