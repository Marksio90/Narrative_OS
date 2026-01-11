'use client'

import { Circle, Star, User, Sparkles, BookOpen, GitBranch } from 'lucide-react'

interface TimelineStats {
  events_by_layer?: Record<string, number>
  events_by_type?: Record<string, number>
  chapter_range?: [number, number]
}

interface Filters {
  layers: string[]
  eventTypes: string[]
  chapterRange: [number, number] | null
  onlyMajorBeats: boolean
}

interface LayerFilterPanelProps {
  filters: Filters
  onFiltersChange: (filters: Filters) => void
  onLayerToggle: (layer: string) => void
  stats: TimelineStats | null
}

const LAYER_CONFIG = {
  plot: {
    label: 'Fabuła',
    color: '#3B82F6',
    icon: Star,
    description: 'Główne wydarzenia fabularne i punkty opowieści'
  },
  character: {
    label: 'Postać',
    color: '#8B5CF6',
    icon: User,
    description: 'Kamienie milowe łuku postaci'
  },
  theme: {
    label: 'Temat',
    color: '#EC4899',
    icon: Sparkles,
    description: 'Momenty tematyczne i symbolika'
  },
  technical: {
    label: 'Techniczny',
    color: '#6B7280',
    icon: BookOpen,
    description: 'Struktura rozdziałów'
  },
  consequence: {
    label: 'Konsekwencja',
    color: '#F59E0B',
    icon: GitBranch,
    description: 'Konsekwencje i efekty falowania'
  }
}

export default function LayerFilterPanel({
  filters,
  onFiltersChange,
  onLayerToggle,
  stats
}: LayerFilterPanelProps) {
  const handleChapterRangeChange = (type: 'start' | 'end', value: string) => {
    const num = parseInt(value)
    if (isNaN(num)) return

    const newRange = filters.chapterRange || [1, 30]
    if (type === 'start') {
      newRange[0] = num
    } else {
      newRange[1] = num
    }

    onFiltersChange({
      ...filters,
      chapterRange: newRange
    })
  }

  const clearChapterRange = () => {
    onFiltersChange({
      ...filters,
      chapterRange: null
    })
  }

  return (
    <div className="p-4 space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-1">Filtry</h3>
        <p className="text-sm text-gray-600">Dostosuj widok osi czasu</p>
      </div>

      {/* Timeline Layers */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-semibold text-gray-900">Warstwy Osi Czasu</h4>
          <button
            onClick={() => {
              const allLayers = Object.keys(LAYER_CONFIG)
              const allEnabled = allLayers.every(l => filters.layers.includes(l))

              onFiltersChange({
                ...filters,
                layers: allEnabled ? [] : allLayers
              })
            }}
            className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
          >
            {filters.layers.length === Object.keys(LAYER_CONFIG).length ? 'Wyczyść Wszystko' : 'Zaznacz Wszystko'}
          </button>
        </div>

        <div className="space-y-2">
          {Object.entries(LAYER_CONFIG).map(([key, config]) => {
            const Icon = config.icon
            const count = stats?.events_by_layer?.[key] || 0
            const isActive = filters.layers.includes(key)

            return (
              <button
                key={key}
                onClick={() => onLayerToggle(key)}
                className={`w-full flex items-center gap-3 p-3 rounded-lg border-2 transition-all ${
                  isActive
                    ? 'border-indigo-200 bg-indigo-50'
                    : 'border-gray-200 bg-white hover:bg-gray-50'
                }`}
              >
                <div
                  className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    isActive ? 'opacity-100' : 'opacity-40'
                  }`}
                  style={{ backgroundColor: config.color + '20' }}
                >
                  <Icon className="w-5 h-5" style={{ color: config.color }} />
                </div>

                <div className="flex-1 text-left">
                  <div className="flex items-center justify-between">
                    <span className={`font-medium ${isActive ? 'text-gray-900' : 'text-gray-600'}`}>
                      {config.label}
                    </span>
                    <span className="text-sm text-gray-500">{count}</span>
                  </div>
                  <div className="text-xs text-gray-500 mt-0.5">{config.description}</div>
                </div>

                {/* Checkbox */}
                <div
                  className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                    isActive
                      ? 'bg-indigo-600 border-indigo-600'
                      : 'border-gray-300'
                  }`}
                >
                  {isActive && (
                    <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Chapter Range */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-semibold text-gray-900">Zakres Rozdziałów</h4>
          {filters.chapterRange && (
            <button
              onClick={clearChapterRange}
              className="text-xs text-gray-600 hover:text-gray-900"
            >
              Wyczyść
            </button>
          )}
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-xs text-gray-600 mb-1">Początkowy Rozdział</label>
            <input
              type="number"
              min={stats?.chapter_range?.[0] || 1}
              max={stats?.chapter_range?.[1] || 30}
              value={filters.chapterRange?.[0] || ''}
              onChange={(e) => handleChapterRangeChange('start', e.target.value)}
              placeholder={`${stats?.chapter_range?.[0] || 1}`}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
            />
          </div>

          <div>
            <label className="block text-xs text-gray-600 mb-1">Końcowy Rozdział</label>
            <input
              type="number"
              min={stats?.chapter_range?.[0] || 1}
              max={stats?.chapter_range?.[1] || 30}
              value={filters.chapterRange?.[1] || ''}
              onChange={(e) => handleChapterRangeChange('end', e.target.value)}
              placeholder={`${stats?.chapter_range?.[1] || 30}`}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
            />
          </div>
        </div>

        {stats?.chapter_range && (
          <div className="mt-2 text-xs text-gray-500">
            Historia obejmuje rozdziały {stats.chapter_range[0]} - {stats.chapter_range[1]}
          </div>
        )}
      </div>

      {/* Display Options */}
      <div>
        <h4 className="text-sm font-semibold text-gray-900 mb-3">Opcje Wyświetlania</h4>

        <div className="space-y-2">
          <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
            <input
              type="checkbox"
              checked={filters.onlyMajorBeats}
              onChange={(e) => onFiltersChange({
                ...filters,
                onlyMajorBeats: e.target.checked
              })}
              className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
            />
            <div>
              <div className="text-sm font-medium text-gray-900">Tylko Główne Punkty</div>
              <div className="text-xs text-gray-500">Pokaż tylko znaczące wydarzenia historii</div>
            </div>
          </label>
        </div>
      </div>

      {/* Event Type Filters */}
      <div>
        <h4 className="text-sm font-semibold text-gray-900 mb-3">Typy Wydarzeń</h4>

        <div className="space-y-2">
          {stats?.events_by_type && Object.entries(stats.events_by_type).map(([type, count]) => (
            <div
              key={type}
              className="flex items-center justify-between p-2 bg-gray-50 rounded"
            >
              <span className="text-sm text-gray-700 capitalize">
                {type.replace('_', ' ')}
              </span>
              <span className="text-xs font-medium text-gray-500">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="pt-4 border-t border-gray-200">
        <button
          onClick={() => onFiltersChange({
            layers: Object.keys(LAYER_CONFIG),
            eventTypes: [],
            chapterRange: null,
            onlyMajorBeats: false
          })}
          className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
        >
          Resetuj Wszystkie Filtry
        </button>
      </div>
    </div>
  )
}
