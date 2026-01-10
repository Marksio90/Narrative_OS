'use client'

import { useState, useEffect } from 'react'
import { AlertTriangle, Clock, Zap, TrendingUp, ChevronDown, ChevronUp, Eye, EyeOff } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

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
  ai_prediction?: {
    reasoning?: string
    suggested_chapter?: number
  }
}

interface ActiveConsequencesResponse {
  consequences: Consequence[]
  total_count: number
  high_probability_count: number
  high_severity_count: number
}

interface ActiveConsequencesPanelProps {
  projectId: number
  currentChapter?: number
  className?: string
}

export default function ActiveConsequencesPanel({
  projectId,
  currentChapter,
  className = ''
}: ActiveConsequencesPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true)
  const [filterTimeframe, setFilterTimeframe] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<'probability' | 'severity'>('probability')

  // Fetch active consequences
  const { data, isLoading, error } = useQuery<ActiveConsequencesResponse>({
    queryKey: ['active-consequences', projectId, currentChapter],
    queryFn: async () => {
      const params = new URLSearchParams({
        project_id: projectId.toString(),
      })
      if (currentChapter) {
        params.append('chapter_number', currentChapter.toString())
      }

      const res = await axios.get(`/api/consequences/active?${params}`)
      return res.data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
    enabled: !!projectId,
  })

  const consequences = data?.consequences || []

  // Filter and sort consequences
  const filteredConsequences = consequences
    .filter(c => !filterTimeframe || c.timeframe === filterTimeframe)
    .sort((a, b) => {
      if (sortBy === 'probability') {
        return b.probability - a.probability
      }
      return b.severity - a.severity
    })

  const getTimeframeIcon = (timeframe: string) => {
    switch (timeframe) {
      case 'immediate':
        return <Zap className="h-3 w-3" />
      case 'short_term':
        return <Clock className="h-3 w-3" />
      case 'medium_term':
        return <TrendingUp className="h-3 w-3" />
      case 'long_term':
        return <TrendingUp className="h-3 w-3" />
      default:
        return <Clock className="h-3 w-3" />
    }
  }

  const getTimeframeLabel = (timeframe: string) => {
    const labels: { [key: string]: string } = {
      immediate: 'Natychmiastowe',
      short_term: 'Krótkoterm.',
      medium_term: 'Średnioterm.',
      long_term: 'Długoterm.',
    }
    return labels[timeframe] || timeframe
  }

  const getTimeframeColor = (timeframe: string) => {
    const colors: { [key: string]: string } = {
      immediate: 'bg-red-100 text-red-700',
      short_term: 'bg-amber-100 text-amber-700',
      medium_term: 'bg-blue-100 text-blue-700',
      long_term: 'bg-purple-100 text-purple-700',
    }
    return colors[timeframe] || 'bg-gray-100 text-gray-700'
  }

  const getSeverityColor = (severity: number) => {
    if (severity >= 0.8) return 'text-red-600'
    if (severity >= 0.5) return 'text-amber-600'
    return 'text-blue-600'
  }

  const getProbabilityColor = (probability: number) => {
    if (probability >= 0.8) return 'bg-green-500'
    if (probability >= 0.5) return 'bg-amber-500'
    return 'bg-blue-500'
  }

  if (!isExpanded) {
    return (
      <div className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className}`}>
        <button
          onClick={() => setIsExpanded(true)}
          className="w-full p-3 flex items-center justify-between hover:bg-gray-50 transition"
        >
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-4 w-4 text-purple-600" />
            <span className="text-sm font-medium text-gray-900">Aktywne Konsekwencje</span>
            {data && (
              <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-bold rounded-full">
                {data.total_count}
              </span>
            )}
          </div>
          <ChevronDown className="h-4 w-4 text-gray-400" />
        </button>
      </div>
    )
  }

  return (
    <div className={`bg-white border border-gray-200 rounded-lg shadow-sm ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5 text-purple-600" />
            <h3 className="text-sm font-bold text-gray-900">Aktywne Konsekwencje</h3>
            {data && (
              <span className="px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-bold rounded-full">
                {data.total_count}
              </span>
            )}
          </div>
          <button
            onClick={() => setIsExpanded(false)}
            className="p-1 text-gray-400 hover:text-gray-600 transition"
          >
            <ChevronUp className="h-4 w-4" />
          </button>
        </div>

        {data && (
          <div className="flex items-center space-x-4 text-xs">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-purple-500 rounded-full" />
              <span className="text-gray-600">
                Wysokie prawdopodobieństwo: <span className="font-bold">{data.high_probability_count}</span>
              </span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-red-500 rounded-full" />
              <span className="text-gray-600">
                Wysoka dotkliwość: <span className="font-bold">{data.high_severity_count}</span>
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="p-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-600">Sortuj:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'probability' | 'severity')}
            className="text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="probability">Prawdopodobieństwo</option>
            <option value="severity">Dotkliwość</option>
          </select>
        </div>

        <div className="flex items-center space-x-1">
          <button
            onClick={() => setFilterTimeframe(null)}
            className={`px-2 py-1 text-xs rounded transition ${
              filterTimeframe === null
                ? 'bg-purple-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            Wszystkie
          </button>
          <button
            onClick={() => setFilterTimeframe('immediate')}
            className={`px-2 py-1 text-xs rounded transition ${
              filterTimeframe === 'immediate'
                ? 'bg-red-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
            title="Natychmiastowe"
          >
            <Zap className="h-3 w-3" />
          </button>
          <button
            onClick={() => setFilterTimeframe('short_term')}
            className={`px-2 py-1 text-xs rounded transition ${
              filterTimeframe === 'short_term'
                ? 'bg-amber-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
            title="Krótkoterminowe"
          >
            <Clock className="h-3 w-3" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-h-96 overflow-y-auto">
        {isLoading && (
          <div className="p-8 text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-purple-600 border-r-transparent"></div>
            <p className="text-sm text-gray-600 mt-2">Ładowanie konsekwencji...</p>
          </div>
        )}

        {error && (
          <div className="p-4 text-center">
            <AlertTriangle className="h-8 w-8 mx-auto text-red-500 mb-2" />
            <p className="text-sm text-red-600">Błąd ładowania konsekwencji</p>
          </div>
        )}

        {!isLoading && !error && filteredConsequences.length === 0 && (
          <div className="p-8 text-center">
            <Eye className="h-12 w-12 mx-auto text-gray-300 mb-2" />
            <p className="text-sm text-gray-500">Brak aktywnych konsekwencji</p>
            <p className="text-xs text-gray-400 mt-1">
              Przeanalizuj sceny aby wykryć wydarzenia i ich konsekwencje
            </p>
          </div>
        )}

        {!isLoading && !error && filteredConsequences.length > 0 && (
          <div className="divide-y divide-gray-100">
            {filteredConsequences.map((consequence) => (
              <ConsequenceCard
                key={consequence.id}
                consequence={consequence}
                getTimeframeIcon={getTimeframeIcon}
                getTimeframeLabel={getTimeframeLabel}
                getTimeframeColor={getTimeframeColor}
                getSeverityColor={getSeverityColor}
                getProbabilityColor={getProbabilityColor}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

interface ConsequenceCardProps {
  consequence: Consequence
  getTimeframeIcon: (timeframe: string) => JSX.Element
  getTimeframeLabel: (timeframe: string) => string
  getTimeframeColor: (timeframe: string) => string
  getSeverityColor: (severity: number) => string
  getProbabilityColor: (probability: number) => string
}

function ConsequenceCard({
  consequence,
  getTimeframeIcon,
  getTimeframeLabel,
  getTimeframeColor,
  getSeverityColor,
  getProbabilityColor,
}: ConsequenceCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="p-3 hover:bg-purple-50 transition">
      <div className="flex items-start space-x-3">
        {/* Probability indicator */}
        <div className="flex-shrink-0 mt-1">
          <div className="relative w-8 h-8">
            <svg className="transform -rotate-90 w-8 h-8">
              <circle
                cx="16"
                cy="16"
                r="14"
                stroke="currentColor"
                strokeWidth="3"
                fill="none"
                className="text-gray-200"
              />
              <circle
                cx="16"
                cy="16"
                r="14"
                stroke="currentColor"
                strokeWidth="3"
                fill="none"
                strokeDasharray={`${consequence.probability * 88} 88`}
                className={getProbabilityColor(consequence.probability)}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-[8px] font-bold text-gray-700">
                {Math.round(consequence.probability * 100)}
              </span>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-1">
            <p className="text-sm text-gray-900 font-medium leading-snug">
              {consequence.description}
            </p>
          </div>

          <div className="flex items-center space-x-2 mb-2">
            {/* Timeframe badge */}
            <span
              className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-medium ${getTimeframeColor(
                consequence.timeframe
              )}`}
            >
              {getTimeframeIcon(consequence.timeframe)}
              <span>{getTimeframeLabel(consequence.timeframe)}</span>
            </span>

            {/* Severity */}
            <div className="flex items-center space-x-1">
              <AlertTriangle className={`h-3 w-3 ${getSeverityColor(consequence.severity)}`} />
              <span className={`text-xs font-medium ${getSeverityColor(consequence.severity)}`}>
                {Math.round(consequence.severity * 100)}%
              </span>
            </div>

            {/* Status badge */}
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                consequence.status === 'active'
                  ? 'bg-amber-100 text-amber-700'
                  : 'bg-purple-100 text-purple-700'
              }`}
            >
              {consequence.status === 'active' ? 'Aktywne' : 'Potencjalne'}
            </span>
          </div>

          {/* Plot impact preview */}
          {consequence.plot_impact && !isExpanded && (
            <p className="text-xs text-gray-600 italic line-clamp-1">
              {consequence.plot_impact}
            </p>
          )}

          {/* Expanded details */}
          {isExpanded && (
            <div className="mt-2 p-2 bg-white rounded border border-gray-200">
              {consequence.plot_impact && (
                <div className="mb-2">
                  <p className="text-xs font-medium text-gray-700 mb-1">Wpływ na fabułę:</p>
                  <p className="text-xs text-gray-600 italic">{consequence.plot_impact}</p>
                </div>
              )}

              {consequence.ai_prediction?.reasoning && (
                <div className="mb-2">
                  <p className="text-xs font-medium text-gray-700 mb-1">Uzasadnienie AI:</p>
                  <p className="text-xs text-gray-600">{consequence.ai_prediction.reasoning}</p>
                </div>
              )}

              {consequence.ai_prediction?.suggested_chapter && (
                <div>
                  <p className="text-xs font-medium text-gray-700">
                    Sugerowany rozdział realizacji:{' '}
                    <span className="text-purple-600">{consequence.ai_prediction.suggested_chapter}</span>
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Expand toggle */}
          {(consequence.plot_impact || consequence.ai_prediction) && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="mt-1 text-xs text-purple-600 hover:text-purple-700 font-medium flex items-center space-x-1"
            >
              {isExpanded ? (
                <>
                  <EyeOff className="h-3 w-3" />
                  <span>Zwiń</span>
                </>
              ) : (
                <>
                  <Eye className="h-3 w-3" />
                  <span>Zobacz szczegóły</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
