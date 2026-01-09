'use client'

import { useState, useEffect } from 'react'
import { Mic, TrendingUp, MessageSquare, BarChart3, AlertCircle, CheckCircle, Loader2, RefreshCw } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface VoiceFingerprint {
  id: number
  character_id: number
  vocabulary_profile: {
    avg_word_length: number
    unique_word_ratio: number
    rarity_score: number
    top_words: string[]
  }
  syntax_profile: {
    avg_sentence_length: number
    complexity_score: number
    question_frequency: number
    exclamation_frequency: number
  }
  linguistic_markers: {
    catchphrases: string[]
    filler_words: string[]
    contractions_ratio: number
  }
  emotional_baseline: {
    dominant_emotion: string
    joy: number
    anger: number
    sadness: number
    fear: number
    neutral: number
  }
  formality_score: number
  confidence_score: number
  sample_count: number
  total_words: number
  last_analyzed_at: string
}

interface ConsistencyScore {
  scene_id: number | null
  overall_score: number
  timestamp: string
  issues_count: number
}

interface VoiceFingerprintPanelProps {
  characterId: number
  characterName: string
  accessToken: string
}

export default function VoiceFingerprintPanel({
  characterId,
  characterName,
  accessToken
}: VoiceFingerprintPanelProps) {
  const [fingerprint, setFingerprint] = useState<VoiceFingerprint | null>(null)
  const [consistencyHistory, setConsistencyHistory] = useState<ConsistencyScore[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  useEffect(() => {
    loadFingerprint()
    loadConsistencyHistory()
  }, [characterId])

  const loadFingerprint = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(
        `${API_URL}/api/voice/character/${characterId}/voice-fingerprint`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setFingerprint(data)
      } else if (response.status === 404) {
        // No fingerprint yet - that's ok
        setFingerprint(null)
      } else {
        throw new Error('Failed to load fingerprint')
      }
    } catch (err: any) {
      console.error('Error loading fingerprint:', err)
      // Don't show error for missing fingerprint
    } finally {
      setIsLoading(false)
    }
  }

  const loadConsistencyHistory = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/voice/character/${characterId}/consistency-history?limit=10`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setConsistencyHistory(data.scores || [])
      }
    } catch (err) {
      console.error('Error loading consistency history:', err)
    }
  }

  const analyzeVoice = async () => {
    setIsAnalyzing(true)
    setError(null)
    setSuccessMessage(null)

    try {
      const response = await fetch(
        `${API_URL}/api/voice/character/${characterId}/analyze-voice`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        }
      )

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Analysis failed')
      }

      const data = await response.json()
      setFingerprint(data)
      setSuccessMessage(`Voice analyzed! Found ${data.sample_count} dialogue samples (${data.total_words} words)`)

      // Reload consistency history
      loadConsistencyHistory()
    } catch (err: any) {
      setError(err.message || 'Failed to analyze voice')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50'
    if (score >= 0.5) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getConsistencyColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-500'
    if (score >= 0.6) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg">
            <Mic className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Voice Fingerprint</h3>
            <p className="text-sm text-gray-600">Dialogue consistency analysis for {characterName}</p>
          </div>
        </div>

        <button
          onClick={analyzeVoice}
          disabled={isAnalyzing}
          className="px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg hover:from-purple-600 hover:to-pink-700 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4" />
              {fingerprint ? 'Re-analyze' : 'Analyze Voice'}
            </>
          )}
        </button>
      </div>

      {/* Messages */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-red-900">Error</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}

      {successMessage && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-green-900">Success</p>
            <p className="text-sm text-green-700 mt-1">{successMessage}</p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
        </div>
      )}

      {/* No Fingerprint State */}
      {!isLoading && !fingerprint && (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <Mic className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h4 className="text-lg font-medium text-gray-900 mb-2">No Voice Fingerprint Yet</h4>
          <p className="text-sm text-gray-600 mb-4 max-w-md mx-auto">
            Click "Analyze Voice" to extract dialogue patterns from existing scenes.
            The system will analyze vocabulary, syntax, and linguistic quirks.
          </p>
          <p className="text-xs text-gray-500">
            Tip: Add dialogue for this character in your scenes first for best results.
          </p>
        </div>
      )}

      {/* Fingerprint Display */}
      {!isLoading && fingerprint && (
        <div className="space-y-4">
          {/* Confidence Score */}
          <div className={`p-4 rounded-lg ${getConfidenceColor(fingerprint.confidence_score)}`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Confidence Score</span>
              <span className="text-2xl font-bold">{(fingerprint.confidence_score * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-white bg-opacity-50 rounded-full h-2">
              <div
                className="h-2 rounded-full bg-current"
                style={{ width: `${fingerprint.confidence_score * 100}%` }}
              />
            </div>
            <p className="text-xs mt-2">
              Based on {fingerprint.sample_count} dialogue samples ({fingerprint.total_words} words)
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 gap-4">
            {/* Formality */}
            <div className="p-4 bg-indigo-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <MessageSquare className="w-4 h-4 text-indigo-600" />
                <span className="text-sm font-medium text-indigo-900">Formality</span>
              </div>
              <p className="text-2xl font-bold text-indigo-600">
                {(fingerprint.formality_score * 100).toFixed(0)}%
              </p>
              <p className="text-xs text-indigo-700 mt-1">
                {fingerprint.formality_score > 0.7 ? 'Formal' : fingerprint.formality_score > 0.4 ? 'Balanced' : 'Casual'}
              </p>
            </div>

            {/* Complexity */}
            <div className="p-4 bg-purple-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium text-purple-900">Complexity</span>
              </div>
              <p className="text-2xl font-bold text-purple-600">
                {(fingerprint.syntax_profile.complexity_score * 100).toFixed(0)}%
              </p>
              <p className="text-xs text-purple-700 mt-1">
                Avg {fingerprint.syntax_profile.avg_sentence_length.toFixed(1)} words/sentence
              </p>
            </div>

            {/* Vocabulary */}
            <div className="p-4 bg-pink-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-pink-600" />
                <span className="text-sm font-medium text-pink-900">Vocabulary</span>
              </div>
              <p className="text-2xl font-bold text-pink-600">
                {fingerprint.vocabulary_profile.avg_word_length.toFixed(1)}
              </p>
              <p className="text-xs text-pink-700 mt-1">
                Avg word length • {(fingerprint.vocabulary_profile.unique_word_ratio * 100).toFixed(0)}% unique
              </p>
            </div>

            {/* Emotion */}
            <div className="p-4 bg-amber-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <MessageSquare className="w-4 h-4 text-amber-600" />
                <span className="text-sm font-medium text-amber-900">Dominant Emotion</span>
              </div>
              <p className="text-lg font-bold text-amber-600 capitalize">
                {fingerprint.emotional_baseline.dominant_emotion}
              </p>
              <p className="text-xs text-amber-700 mt-1">
                Emotional baseline
              </p>
            </div>
          </div>

          {/* Linguistic Markers */}
          {fingerprint.linguistic_markers.catchphrases.length > 0 && (
            <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg border border-purple-200">
              <h4 className="text-sm font-semibold text-purple-900 mb-3 flex items-center gap-2">
                <Mic className="w-4 h-4" />
                Signature Phrases
              </h4>
              <div className="flex flex-wrap gap-2">
                {fingerprint.linguistic_markers.catchphrases.map((phrase, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-white text-purple-700 rounded-full text-xs font-medium border border-purple-200"
                  >
                    "{phrase}"
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Top Words */}
          {fingerprint.vocabulary_profile.top_words.length > 0 && (
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <h4 className="text-sm font-semibold text-gray-900 mb-3">Most Used Words</h4>
              <div className="flex flex-wrap gap-2">
                {fingerprint.vocabulary_profile.top_words.slice(0, 10).map((word, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-white text-gray-700 rounded-lg text-xs font-medium border border-gray-300"
                  >
                    {word}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Consistency History */}
          {consistencyHistory.length > 0 && (
            <div className="p-4 bg-white rounded-lg border border-gray-200">
              <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Consistency History
              </h4>
              <div className="space-y-2">
                {consistencyHistory.slice(0, 5).map((score, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs text-gray-600">
                          {score.scene_id ? `Scene #${score.scene_id}` : 'Scene'}
                        </span>
                        <span className="text-xs font-medium text-gray-900">
                          {(score.overall_score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-1.5">
                        <div
                          className={`h-1.5 rounded-full ${getConsistencyColor(score.overall_score)}`}
                          style={{ width: `${score.overall_score * 100}%` }}
                        />
                      </div>
                    </div>
                    {score.issues_count > 0 && (
                      <span className="text-xs text-red-600 font-medium">
                        {score.issues_count} issue{score.issues_count !== 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Last Analyzed */}
          <div className="text-center text-xs text-gray-500">
            Last analyzed: {new Date(fingerprint.last_analyzed_at).toLocaleDateString()} at{' '}
            {new Date(fingerprint.last_analyzed_at).toLocaleTimeString()}
          </div>
        </div>
      )}
    </div>
  )
}
