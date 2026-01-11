'use client'

import { useState, useEffect } from 'react'
import { Calendar, RefreshCw, AlertTriangle, Bookmark, Eye, Filter, Settings } from 'lucide-react'
import { useTranslations } from 'next-intl'
import InteractiveTimeline from '@/components/InteractiveTimeline'
import TimelineControls from '@/components/TimelineControls'
import ConflictPanel from '@/components/ConflictPanel'
import LayerFilterPanel from '@/components/LayerFilterPanel'

interface TimelineStats {
  total_events: number
  events_by_type: Record<string, number>
  events_by_layer: Record<string, number>
  chapter_range: [number, number]
  major_beats_count: number
  total_conflicts: number
  open_conflicts: number
  conflicts_by_severity: Record<string, number>
  pacing_score?: number
}

interface TimelineEvent {
  id: number
  event_type: string
  chapter_number: number
  title: string
  description?: string
  layer: string
  magnitude: number
  is_major_beat: boolean
  color?: string
  icon?: string
  tags: string[]
  related_characters: number[]
  is_custom: boolean
  is_visible: boolean
}

interface Conflict {
  id: number
  conflict_type: string
  severity: string
  chapter_start?: number
  chapter_end?: number
  title: string
  description: string
  status: string
}

export default function TimelinePage() {
  const t = useTranslations('timeline')
  const tCommon = useTranslations('common')

  const [events, setEvents] = useState<TimelineEvent[]>([])
  const [conflicts, setConflicts] = useState<Conflict[]>([])
  const [stats, setStats] = useState<TimelineStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [showConflicts, setShowConflicts] = useState(true)
  const [showFilters, setShowFilters] = useState(false)

  // Get current project ID
  const projectId = 1 // Replace with actual project ID from context

  // Filter state
  const [filters, setFilters] = useState({
    layers: ['plot', 'character', 'theme', 'technical', 'consequence'],
    eventTypes: [] as string[],
    chapterRange: null as [number, number] | null,
    onlyMajorBeats: false,
  })

  useEffect(() => {
    fetchTimeline()
    fetchStatistics()
    fetchConflicts()
  }, [])

  const fetchTimeline = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({
        only_visible: 'true',
        only_major_beats: filters.onlyMajorBeats ? 'true' : 'false',
      })

      if (filters.layers.length > 0) {
        params.append('layers', filters.layers.join(','))
      }

      if (filters.chapterRange) {
        params.append('chapter_start', filters.chapterRange[0].toString())
        params.append('chapter_end', filters.chapterRange[1].toString())
      }

      const response = await fetch(`/api/projects/${projectId}/timeline/events?${params}`)
      if (response.ok) {
        const data = await response.json()
        setEvents(data.events || [])
      }
    } catch (error) {
      console.error('Failed to fetch timeline:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStatistics = async () => {
    try {
      const response = await fetch(`/api/projects/${projectId}/timeline/statistics`)
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to fetch statistics:', error)
    }
  }

  const fetchConflicts = async () => {
    try {
      const response = await fetch(`/api/projects/${projectId}/timeline/conflicts?status=open`)
      if (response.ok) {
        const data = await response.json()
        setConflicts(data.conflicts || [])
      }
    } catch (error) {
      console.error('Failed to fetch conflicts:', error)
    }
  }

  const syncTimeline = async () => {
    setSyncing(true)
    try {
      const response = await fetch(`/api/projects/${projectId}/timeline/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ force_full_sync: false })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Synced:', data)

        // Refresh data
        await Promise.all([
          fetchTimeline(),
          fetchStatistics(),
          fetchConflicts()
        ])
      }
    } catch (error) {
      console.error('Failed to sync timeline:', error)
    } finally {
      setSyncing(false)
    }
  }

  const detectConflicts = async () => {
    try {
      const response = await fetch(`/api/projects/${projectId}/timeline/conflicts/detect`, {
        method: 'POST'
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Conflicts detected:', data)
        await fetchConflicts()
      }
    } catch (error) {
      console.error('Failed to detect conflicts:', error)
    }
  }

  const handleLayerToggle = (layer: string) => {
    setFilters(prev => ({
      ...prev,
      layers: prev.layers.includes(layer)
        ? prev.layers.filter(l => l !== layer)
        : [...prev.layers, layer]
    }))
  }

  useEffect(() => {
    fetchTimeline()
  }, [filters])

  if (loading && events.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">{tCommon('loading')}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <Calendar className="w-6 h-6 text-indigo-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{t('title')}</h1>
                <p className="text-sm text-gray-600">{t('subtitle')}</p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  showFilters
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <Filter className="w-4 h-4" />
                {t('filters')}
              </button>

              <button
                onClick={() => setShowConflicts(!showConflicts)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  showConflicts
                    ? 'bg-orange-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <AlertTriangle className="w-4 h-4" />
                {t('conflicts')} ({conflicts.length})
              </button>

              <button
                onClick={syncTimeline}
                disabled={syncing}
                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
                {syncing ? 'Synchronizacja...' : 'Synchronizuj'}
              </button>
            </div>
          </div>

          {/* Stats Bar */}
          {stats && (
            <div className="mt-4 grid grid-cols-2 md:grid-cols-6 gap-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-600">Łącznie Wydarzeń</div>
                <div className="text-2xl font-bold text-gray-900">{stats.total_events}</div>
              </div>

              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-600">Główne Punkty</div>
                <div className="text-2xl font-bold text-indigo-600">{stats.major_beats_count}</div>
              </div>

              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-600">Rozdziały</div>
                <div className="text-2xl font-bold text-gray-900">
                  {stats.chapter_range[0]}-{stats.chapter_range[1]}
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-600">Otwarte Konflikty</div>
                <div className={`text-2xl font-bold ${
                  stats.open_conflicts > 0 ? 'text-orange-600' : 'text-green-600'
                }`}>
                  {stats.open_conflicts}
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-600">Ocena Tempa</div>
                <div className="text-2xl font-bold text-blue-600">
                  {stats.pacing_score ? (stats.pacing_score * 100).toFixed(0) : 'N/A'}
                  {stats.pacing_score && '%'}
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-600">Aktywne Warstwy</div>
                <div className="text-2xl font-bold text-purple-600">{filters.layers.length}</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-200px)]">
        {/* Sidebar - Filters */}
        {showFilters && (
          <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto">
            <LayerFilterPanel
              filters={filters}
              onFiltersChange={setFilters}
              onLayerToggle={handleLayerToggle}
              stats={stats}
            />
          </div>
        )}

        {/* Timeline Visualization */}
        <div className="flex-1 relative bg-gray-50">
          <InteractiveTimeline
            events={events}
            conflicts={conflicts}
            filters={filters}
            onEventMove={async (eventId, newChapter) => {
              try {
                const response = await fetch(
                  `/api/projects/${projectId}/timeline/events/${eventId}/move`,
                  {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ new_chapter: newChapter })
                  }
                )
                if (response.ok) {
                  await fetchTimeline()
                }
              } catch (error) {
                console.error('Failed to move event:', error)
              }
            }}
            onEventClick={(event) => {
              console.log('Event clicked:', event)
              // Open event details modal
            }}
          />

          {/* Timeline Controls Overlay */}
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 z-10">
            <TimelineControls />
          </div>
        </div>

        {/* Sidebar - Conflicts */}
        {showConflicts && (
          <div className="w-96 bg-white border-l border-gray-200 overflow-y-auto">
            <ConflictPanel
              conflicts={conflicts}
              onResolve={async (conflictId) => {
                try {
                  const response = await fetch(
                    `/api/projects/${projectId}/timeline/conflicts/${conflictId}/resolve`,
                    { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) }
                  )
                  if (response.ok) {
                    await fetchConflicts()
                  }
                } catch (error) {
                  console.error('Failed to resolve conflict:', error)
                }
              }}
              onIgnore={async (conflictId) => {
                try {
                  const response = await fetch(
                    `/api/projects/${projectId}/timeline/conflicts/${conflictId}/ignore`,
                    { method: 'POST' }
                  )
                  if (response.ok) {
                    await fetchConflicts()
                  }
                } catch (error) {
                  console.error('Failed to ignore conflict:', error)
                }
              }}
              onDetectNew={detectConflicts}
            />
          </div>
        )}
      </div>
    </div>
  )
}
