'use client'

import { useState } from 'react'
import { Sparkles, AlertTriangle, CheckCircle, Lightbulb, X, Loader } from 'lucide-react'

interface AIToolsProps {
  projectId: number
  accessToken: string
  onClose: () => void
}

interface ConsistencyIssue {
  type: string
  severity: string
  description: string
  text_excerpt?: string
  canon_reference?: string
  suggestion?: string
  line_number?: number
}

interface Suggestion {
  category: string
  priority: string
  suggestion: string
  example?: string
  rationale?: string
}

export default function AITools({ projectId, accessToken, onClose }: AIToolsProps) {
  const [activeTab, setActiveTab] = useState<'consistency' | 'suggestions'>('consistency')
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)

  // Consistency check state
  const [consistencyResult, setConsistencyResult] = useState<{
    issues: ConsistencyIssue[]
    summary: string
    overall_score: number
    critical_count: number
    warning_count: number
    suggestion_count: number
  } | null>(null)

  // Suggestions state
  const [suggestionsResult, setSuggestionsResult] = useState<{
    suggestions: Suggestion[]
    summary: string
    strengths: string[]
    opportunities: string[]
  } | null>(null)

  const handleCheckConsistency = async () => {
    if (!text.trim()) {
      alert('Wpisz tekst do sprawdzenia')
      return
    }

    setLoading(true)
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/projects/${projectId}/ai/check-consistency`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text,
            check_character_voice: true,
            check_worldbuilding: true,
            check_plot_continuity: true,
          }),
        }
      )

      if (response.ok) {
        const result = await response.json()
        setConsistencyResult(result)
      } else {
        alert('Błąd podczas sprawdzania spójności')
      }
    } catch (error) {
      console.error('Error checking consistency:', error)
      alert('Błąd podczas sprawdzania spójności')
    } finally {
      setLoading(false)
    }
  }

  const handleGetSuggestions = async () => {
    if (!text.trim()) {
      alert('Wpisz tekst do analizy')
      return
    }

    setLoading(true)
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/projects/${projectId}/ai/suggest`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            text,
            focus_areas: ['pacing', 'dialogue', 'description', 'emotion'],
          }),
        }
      )

      if (response.ok) {
        const result = await response.json()
        setSuggestionsResult(result)
      } else {
        alert('Błąd podczas generowania sugestii')
      }
    } catch (error) {
      console.error('Error getting suggestions:', error)
      alert('Błąd podczas generowania sugestii')
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600 bg-red-50 border-red-200'
      case 'warning':
        return 'text-amber-600 bg-amber-50 border-amber-200'
      case 'suggestion':
        return 'text-blue-600 bg-blue-50 border-blue-200'
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-600 bg-red-50'
      case 'medium':
        return 'text-amber-600 bg-amber-50'
      case 'low':
        return 'text-blue-600 bg-blue-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-6xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">AI Narzędzia</h2>
              <p className="text-sm text-gray-600">Sprawdź spójność i otrzymaj sugestie</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 px-6">
          <button
            onClick={() => setActiveTab('consistency')}
            className={`flex items-center space-x-2 px-4 py-3 font-medium text-sm transition ${
              activeTab === 'consistency'
                ? 'text-indigo-600 border-b-2 border-indigo-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <AlertTriangle className="h-4 w-4" />
            <span>Sprawdzanie Spójności</span>
          </button>
          <button
            onClick={() => setActiveTab('suggestions')}
            className={`flex items-center space-x-2 px-4 py-3 font-medium text-sm transition ${
              activeTab === 'suggestions'
                ? 'text-indigo-600 border-b-2 border-indigo-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Lightbulb className="h-4 w-4" />
            <span>Sugestie AI</span>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-2 gap-6 h-full">
            {/* Left: Input */}
            <div className="flex flex-col space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tekst do analizy
                </label>
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Wklej fragment tekstu do sprawdzenia..."
                  className="w-full h-96 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none font-mono text-sm"
                />
              </div>

              <button
                onClick={activeTab === 'consistency' ? handleCheckConsistency : handleGetSuggestions}
                disabled={loading || !text.trim()}
                className={`w-full py-3 rounded-lg font-medium transition ${
                  loading || !text.trim()
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700'
                }`}
              >
                {loading ? (
                  <span className="flex items-center justify-center space-x-2">
                    <Loader className="h-5 w-5 animate-spin" />
                    <span>Analizowanie...</span>
                  </span>
                ) : activeTab === 'consistency' ? (
                  'Sprawdź Spójność'
                ) : (
                  'Wygeneruj Sugestie'
                )}
              </button>
            </div>

            {/* Right: Results */}
            <div className="flex flex-col space-y-4">
              <h3 className="text-lg font-bold text-gray-900">Wyniki</h3>

              {/* Consistency Results */}
              {activeTab === 'consistency' && consistencyResult && (
                <div className="space-y-4">
                  {/* Score */}
                  <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg p-4 border border-indigo-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Wynik Spójności</span>
                      <span className="text-2xl font-bold text-indigo-600">
                        {consistencyResult.overall_score}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-indigo-600 to-purple-600 h-2 rounded-full transition-all"
                        style={{ width: `${consistencyResult.overall_score}%` }}
                      />
                    </div>
                  </div>

                  {/* Summary */}
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-blue-900">{consistencyResult.summary}</p>
                  </div>

                  {/* Issue Counts */}
                  <div className="grid grid-cols-3 gap-3">
                    <div className="bg-red-50 rounded-lg p-3 text-center">
                      <p className="text-2xl font-bold text-red-600">{consistencyResult.critical_count}</p>
                      <p className="text-xs text-red-700">Krytyczne</p>
                    </div>
                    <div className="bg-amber-50 rounded-lg p-3 text-center">
                      <p className="text-2xl font-bold text-amber-600">{consistencyResult.warning_count}</p>
                      <p className="text-xs text-amber-700">Ostrzeżenia</p>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-3 text-center">
                      <p className="text-2xl font-bold text-blue-600">{consistencyResult.suggestion_count}</p>
                      <p className="text-xs text-blue-700">Sugestie</p>
                    </div>
                  </div>

                  {/* Issues List */}
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {consistencyResult.issues.map((issue, idx) => (
                      <div key={idx} className={`border rounded-lg p-4 ${getSeverityColor(issue.severity)}`}>
                        <div className="flex items-start justify-between mb-2">
                          <span className="text-xs font-semibold uppercase">{issue.type}</span>
                          <span className="text-xs font-semibold uppercase">{issue.severity}</span>
                        </div>
                        <p className="text-sm font-medium mb-2">{issue.description}</p>
                        {issue.text_excerpt && (
                          <div className="bg-white bg-opacity-50 rounded p-2 mb-2 text-xs italic">
                            "{issue.text_excerpt}"
                          </div>
                        )}
                        {issue.canon_reference && (
                          <p className="text-xs mb-2">
                            <strong>Canon:</strong> {issue.canon_reference}
                          </p>
                        )}
                        {issue.suggestion && (
                          <p className="text-xs">
                            <strong>Sugestia:</strong> {issue.suggestion}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Suggestions Results */}
              {activeTab === 'suggestions' && suggestionsResult && (
                <div className="space-y-4">
                  {/* Summary */}
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <p className="text-sm text-purple-900">{suggestionsResult.summary}</p>
                  </div>

                  {/* Strengths */}
                  {suggestionsResult.strengths.length > 0 && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div className="flex items-center space-x-2 mb-2">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <span className="text-sm font-semibold text-green-900">Mocne Strony</span>
                      </div>
                      <ul className="space-y-1">
                        {suggestionsResult.strengths.map((strength, idx) => (
                          <li key={idx} className="text-sm text-green-800">• {strength}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Suggestions List */}
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {suggestionsResult.suggestions.map((suggestion, idx) => (
                      <div key={idx} className={`border rounded-lg p-4 ${getPriorityColor(suggestion.priority)}`}>
                        <div className="flex items-start justify-between mb-2">
                          <span className="text-xs font-semibold uppercase">{suggestion.category}</span>
                          <span className="text-xs font-semibold uppercase">{suggestion.priority}</span>
                        </div>
                        <p className="text-sm font-medium mb-2">{suggestion.suggestion}</p>
                        {suggestion.rationale && (
                          <p className="text-xs mb-2 italic">{suggestion.rationale}</p>
                        )}
                        {suggestion.example && (
                          <div className="bg-white bg-opacity-50 rounded p-2 text-xs">
                            <strong>Przykład:</strong> {suggestion.example}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Empty State */}
              {((activeTab === 'consistency' && !consistencyResult) ||
                (activeTab === 'suggestions' && !suggestionsResult)) && (
                <div className="flex-1 flex items-center justify-center text-gray-400">
                  <div className="text-center">
                    <Sparkles className="h-16 w-16 mx-auto mb-4" />
                    <p className="text-sm">
                      {activeTab === 'consistency'
                        ? 'Wklej tekst i kliknij "Sprawdź Spójność"'
                        : 'Wklej tekst i kliknij "Wygeneruj Sugestie"'}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
