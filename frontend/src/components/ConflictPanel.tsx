'use client'

import { useState } from 'react'
import { AlertTriangle, AlertCircle, Info, XCircle, CheckCircle, X, RefreshCw } from 'lucide-react'

interface Conflict {
  id: number
  conflict_type: string
  severity: string
  chapter_start?: number
  chapter_end?: number
  title: string
  description: string
  status: string
  suggestions?: Array<{
    action: string
    details: string
  }>
}

interface ConflictPanelProps {
  conflicts: Conflict[]
  onResolve: (conflictId: number) => void
  onIgnore: (conflictId: number) => void
  onDetectNew: () => void
}

const SEVERITY_CONFIG = {
  critical: {
    icon: XCircle,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    label: 'Krytyczny'
  },
  error: {
    icon: AlertCircle,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
    label: 'Błąd'
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    label: 'Ostrzeżenie'
  },
  info: {
    icon: Info,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    label: 'Info'
  }
}

const CONFLICT_TYPE_LABELS: Record<string, string> = {
  overlap: 'Nakładanie Wydarzeń',
  character_conflict: 'Konflikt Postaci',
  pacing_issue: 'Problem Tempa',
  continuity_error: 'Błąd Ciągłości',
  inconsistency: 'Niespójność'
}

export default function ConflictPanel({
  conflicts,
  onResolve,
  onIgnore,
  onDetectNew
}: ConflictPanelProps) {
  const groupedConflicts = {
    critical: conflicts.filter(c => c.severity === 'critical'),
    error: conflicts.filter(c => c.severity === 'error'),
    warning: conflicts.filter(c => c.severity === 'warning'),
    info: conflicts.filter(c => c.severity === 'info')
  }

  const totalConflicts = conflicts.length

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">Konflikty</h3>
          <button
            onClick={onDetectNew}
            className="flex items-center gap-2 px-3 py-1.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm"
          >
            <RefreshCw className="w-4 h-4" />
            Wykryj
          </button>
        </div>

        {/* Summary */}
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-gray-50 rounded-lg p-2">
            <div className="text-xs text-gray-600">Łącznie</div>
            <div className="text-xl font-bold text-gray-900">{totalConflicts}</div>
          </div>

          <div className="bg-red-50 rounded-lg p-2">
            <div className="text-xs text-red-600">Krytyczne + Błędy</div>
            <div className="text-xl font-bold text-red-600">
              {groupedConflicts.critical.length + groupedConflicts.error.length}
            </div>
          </div>
        </div>
      </div>

      {/* Conflicts List */}
      <div className="flex-1 overflow-y-auto">
        {totalConflicts === 0 ? (
          <div className="flex flex-col items-center justify-center h-full p-8 text-center">
            <CheckCircle className="w-16 h-16 text-green-500 mb-4" />
            <h4 className="text-lg font-semibold text-gray-900 mb-2">Nie Znaleziono Konfliktów</h4>
            <p className="text-sm text-gray-600">Twoja oś czasu wygląda dobrze!</p>
            <button
              onClick={onDetectNew}
              className="mt-4 px-4 py-2 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-colors text-sm font-medium"
            >
              Uruchom Wykrywanie
            </button>
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {/* Critical */}
            {groupedConflicts.critical.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <XCircle className="w-4 h-4 text-red-600" />
                  <span className="text-sm font-semibold text-gray-900">
                    Krytyczne ({groupedConflicts.critical.length})
                  </span>
                </div>
                <div className="space-y-2">
                  {groupedConflicts.critical.map(conflict => (
                    <ConflictCard
                      key={conflict.id}
                      conflict={conflict}
                      onResolve={onResolve}
                      onIgnore={onIgnore}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Errors */}
            {groupedConflicts.error.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="w-4 h-4 text-orange-600" />
                  <span className="text-sm font-semibold text-gray-900">
                    Błędy ({groupedConflicts.error.length})
                  </span>
                </div>
                <div className="space-y-2">
                  {groupedConflicts.error.map(conflict => (
                    <ConflictCard
                      key={conflict.id}
                      conflict={conflict}
                      onResolve={onResolve}
                      onIgnore={onIgnore}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Warnings */}
            {groupedConflicts.warning.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-4 h-4 text-yellow-600" />
                  <span className="text-sm font-semibold text-gray-900">
                    Ostrzeżenia ({groupedConflicts.warning.length})
                  </span>
                </div>
                <div className="space-y-2">
                  {groupedConflicts.warning.map(conflict => (
                    <ConflictCard
                      key={conflict.id}
                      conflict={conflict}
                      onResolve={onResolve}
                      onIgnore={onIgnore}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Info */}
            {groupedConflicts.info.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Info className="w-4 h-4 text-blue-600" />
                  <span className="text-sm font-semibold text-gray-900">
                    Info ({groupedConflicts.info.length})
                  </span>
                </div>
                <div className="space-y-2">
                  {groupedConflicts.info.map(conflict => (
                    <ConflictCard
                      key={conflict.id}
                      conflict={conflict}
                      onResolve={onResolve}
                      onIgnore={onIgnore}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function ConflictCard({
  conflict,
  onResolve,
  onIgnore
}: {
  conflict: Conflict
  onResolve: (id: number) => void
  onIgnore: (id: number) => void
}) {
  const [expanded, setExpanded] = useState(false)
  const config = SEVERITY_CONFIG[conflict.severity as keyof typeof SEVERITY_CONFIG] || SEVERITY_CONFIG.info
  const Icon = config.icon

  return (
    <div
      className={`border-2 rounded-lg overflow-hidden ${config.borderColor} ${config.bgColor}`}
    >
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-3 text-left hover:bg-black hover:bg-opacity-5 transition-colors"
      >
        <div className="flex items-start gap-3">
          <Icon className={`w-5 h-5 mt-0.5 flex-shrink-0 ${config.color}`} />

          <div className="flex-1 min-w-0">
            <div className="font-semibold text-gray-900 text-sm mb-1">
              {conflict.title}
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <span className={`text-xs px-2 py-0.5 rounded ${config.color} bg-white border ${config.borderColor}`}>
                {config.label}
              </span>

              <span className="text-xs text-gray-600">
                {CONFLICT_TYPE_LABELS[conflict.conflict_type] || conflict.conflict_type}
              </span>

              {conflict.chapter_start !== undefined && (
                <span className="text-xs text-gray-600">
                  {conflict.chapter_end && conflict.chapter_end !== conflict.chapter_start
                    ? `Rozdz. ${conflict.chapter_start}-${conflict.chapter_end}`
                    : `Rozdz. ${conflict.chapter_start}`
                  }
                </span>
              )}
            </div>
          </div>

          {/* Expand Icon */}
          <svg
            className={`w-5 h-5 text-gray-400 transition-transform flex-shrink-0 ${
              expanded ? 'rotate-180' : ''
            }`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Expanded Content */}
      {expanded && (
        <div className="px-3 pb-3 space-y-3 border-t border-gray-200">
          {/* Description */}
          <div className="pt-3">
            <div className="text-sm text-gray-700 whitespace-pre-wrap">
              {conflict.description}
            </div>
          </div>

          {/* Suggestions */}
          {conflict.suggestions && conflict.suggestions.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-gray-900 mb-2">Sugestie:</div>
              <ul className="space-y-1">
                {conflict.suggestions.map((suggestion, index) => (
                  <li key={index} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-indigo-600 mt-0.5">•</span>
                    <span>{suggestion.details}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-2 pt-2">
            <button
              onClick={() => onResolve(conflict.id)}
              className="flex-1 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
            >
              <CheckCircle className="w-4 h-4 inline mr-1" />
              Rozwiąż
            </button>

            <button
              onClick={() => onIgnore(conflict.id)}
              className="flex-1 px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors text-sm font-medium"
            >
              <X className="w-4 h-4 inline mr-1" />
              Ignoruj
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
