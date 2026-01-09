'use client'

import { useState } from 'react'
import { AlertTriangle, CheckCircle, Lightbulb, Loader2, User, TrendingDown } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ConsistencyIssue {
  type: string
  severity: string
  description: string
  line_number: number
  problematic_text: string
}

interface ConsistencySuggestion {
  issue_index: number
  original_text: string
  suggested_text: string
  reason: string
}

interface ConsistencyResult {
  overall_score: number
  vocabulary_score: number
  syntax_score: number
  formality_score: number
  emotional_score: number
  issues: ConsistencyIssue[]
  suggestions: ConsistencySuggestion[]
}

interface DialogueConsistencyCheckerProps {
  generatedText: string
  accessToken: string
  onClose?: () => void
}

export default function DialogueConsistencyChecker({
  generatedText,
  accessToken,
  onClose
}: DialogueConsistencyCheckerProps) {
  const [isChecking, setIsChecking] = useState(false)
  const [selectedCharacterId, setSelectedCharacterId] = useState<number | null>(null)
  const [consistencyResults, setConsistencyResults] = useState<Map<number, ConsistencyResult>>(new Map())
  const [characters, setCharacters] = useState<Array<{id: number, name: string}>>([])
  const [error, setError] = useState<string | null>(null)

  // Extract dialogue from generated text (simple approach)
  const extractDialogue = (text: string): Array<{dialogue: string, context: string}> => {
    const dialoguePattern = /"([^"]+)"/g
    const matches = []
    let match

    while ((match = dialoguePattern.exec(text)) !== null) {
      const dialogue = match[1]
      const start = Math.max(0, match.index - 50)
      const end = Math.min(text.length, match.index + match[0].length + 50)
      const context = text.substring(start, end)

      matches.push({ dialogue, context })
    }

    return matches
  }

  const checkDialogueConsistency = async (characterId: number, dialogue: string) => {
    setIsChecking(true)
    setError(null)

    try {
      const response = await fetch(
        `${API_URL}/api/voice/ai/check-dialogue-consistency`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            character_id: characterId,
            dialogue_text: dialogue,
          }),
        }
      )

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Consistency check failed')
      }

      const result = await response.json()
      setConsistencyResults(prev => new Map(prev).set(characterId, result))

      return result
    } catch (err: any) {
      setError(err.message)
      return null
    } finally {
      setIsChecking(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50'
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getSeverityColor = (severity: string) => {
    if (severity === 'high') return 'bg-red-100 text-red-800 border-red-300'
    if (severity === 'medium') return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    return 'bg-blue-100 text-blue-800 border-blue-300'
  }

  const dialogues = extractDialogue(generatedText)

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg">
            <User className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Dialogue Consistency Check</h3>
            <p className="text-sm text-gray-600">
              {dialogues.length} dialogue line{dialogues.length !== 1 ? 's' : ''} detected
            </p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition"
          >
            ×
          </button>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-900">Error</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* No Dialogue */}
      {dialogues.length === 0 && (
        <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-sm text-gray-600">No dialogue found in generated text.</p>
        </div>
      )}

      {/* Dialogue List */}
      {dialogues.length > 0 && (
        <div className="space-y-3">
          {dialogues.map((item, idx) => {
            const result = selectedCharacterId ? consistencyResults.get(selectedCharacterId) : null

            return (
              <div
                key={idx}
                className="p-4 bg-white rounded-lg border border-gray-200 hover:border-purple-300 transition"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 mb-2">
                      "{item.dialogue}"
                    </p>
                    <p className="text-xs text-gray-500 line-clamp-1">
                      ...{item.context}...
                    </p>
                  </div>
                </div>

                {/* Check Button (placeholder - would need character attribution) */}
                <div className="flex items-center gap-2 mt-3">
                  <button
                    onClick={() => selectedCharacterId && checkDialogueConsistency(selectedCharacterId, item.dialogue)}
                    disabled={!selectedCharacterId || isChecking}
                    className="px-3 py-1.5 bg-purple-600 text-white text-xs rounded-lg hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    {isChecking ? (
                      <>
                        <Loader2 className="w-3 h-3 animate-spin" />
                        Checking...
                      </>
                    ) : (
                      'Check Consistency'
                    )}
                  </button>
                  <span className="text-xs text-gray-500">
                    {!selectedCharacterId && '(Select character first)'}
                  </span>
                </div>

                {/* Consistency Results */}
                {result && (
                  <div className="mt-4 space-y-3 pt-4 border-t border-gray-200">
                    {/* Overall Score */}
                    <div className={`p-3 rounded-lg ${getScoreColor(result.overall_score)}`}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium">Overall Consistency</span>
                        <span className="text-xl font-bold">
                          {(result.overall_score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="w-full bg-white bg-opacity-50 rounded-full h-2">
                        <div
                          className="h-2 rounded-full bg-current"
                          style={{ width: `${result.overall_score * 100}%` }}
                        />
                      </div>
                    </div>

                    {/* Score Breakdown */}
                    <div className="grid grid-cols-2 gap-2">
                      <div className="p-2 bg-gray-50 rounded">
                        <p className="text-xs text-gray-600">Vocabulary</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {(result.vocabulary_score * 100).toFixed(0)}%
                        </p>
                      </div>
                      <div className="p-2 bg-gray-50 rounded">
                        <p className="text-xs text-gray-600">Syntax</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {(result.syntax_score * 100).toFixed(0)}%
                        </p>
                      </div>
                      <div className="p-2 bg-gray-50 rounded">
                        <p className="text-xs text-gray-600">Formality</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {(result.formality_score * 100).toFixed(0)}%
                        </p>
                      </div>
                      <div className="p-2 bg-gray-50 rounded">
                        <p className="text-xs text-gray-600">Emotion</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {(result.emotional_score * 100).toFixed(0)}%
                        </p>
                      </div>
                    </div>

                    {/* Issues */}
                    {result.issues.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="text-xs font-semibold text-gray-900 flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4 text-yellow-600" />
                          Issues Detected
                        </h4>
                        {result.issues.map((issue, issueIdx) => (
                          <div
                            key={issueIdx}
                            className={`p-2 rounded border text-xs ${getSeverityColor(issue.severity)}`}
                          >
                            <p className="font-medium">{issue.type.toUpperCase()}</p>
                            <p className="mt-1">{issue.description}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Suggestions */}
                    {result.suggestions.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="text-xs font-semibold text-gray-900 flex items-center gap-2">
                          <Lightbulb className="w-4 h-4 text-green-600" />
                          Suggestions
                        </h4>
                        {result.suggestions.map((suggestion, sugIdx) => (
                          <div
                            key={sugIdx}
                            className="p-2 bg-green-50 border border-green-200 rounded text-xs"
                          >
                            <p className="text-gray-600 mb-1">Original:</p>
                            <p className="text-gray-900 mb-2">{suggestion.original_text}</p>
                            <p className="text-gray-600 mb-1">Suggested:</p>
                            <p className="text-green-700 font-medium mb-2">{suggestion.suggested_text}</p>
                            <p className="text-gray-500 text-xs">{suggestion.reason}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Success Message */}
                    {result.issues.length === 0 && (
                      <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-600" />
                        <p className="text-sm text-green-800">
                          Dialogue is consistent with character voice!
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
