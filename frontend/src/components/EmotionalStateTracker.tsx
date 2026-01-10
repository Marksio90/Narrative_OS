'use client'

import { useState, useEffect } from 'react'
import { Heart, TrendingUp, TrendingDown, Minus, Smile, Frown, Meh, Zap, Cloud } from 'lucide-react'

interface EmotionalState {
  id: number
  arc_id: number
  chapter_number: number
  primary_emotion: string
  intensity: number
  confidence_level?: number
  scene_context?: string
  trigger_event?: string
  internal_state?: Record<string, any>
  created_at: string
}

interface EmotionalStateTrackerProps {
  characterId: number
}

export default function EmotionalStateTracker({ characterId }: EmotionalStateTrackerProps) {
  const [emotionalStates, setEmotionalStates] = useState<EmotionalState[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'positive' | 'negative' | 'neutral'>('all')

  useEffect(() => {
    fetchEmotionalJourney()
  }, [characterId])

  const fetchEmotionalJourney = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/character-arcs/character/${characterId}/emotional-journey`)
      if (response.ok) {
        const data = await response.json()
        setEmotionalStates(data.states || [])
      }
    } catch (error) {
      console.error('Failed to fetch emotional journey:', error)
    } finally {
      setLoading(false)
    }
  }

  const getEmotionColor = (emotion: string) => {
    const emotions: Record<string, string> = {
      joy: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      happiness: 'text-yellow-600 bg-yellow-50 border-yellow-200',
      sadness: 'text-blue-600 bg-blue-50 border-blue-200',
      grief: 'text-blue-700 bg-blue-100 border-blue-300',
      anger: 'text-red-600 bg-red-50 border-red-200',
      rage: 'text-red-700 bg-red-100 border-red-300',
      fear: 'text-purple-600 bg-purple-50 border-purple-200',
      terror: 'text-purple-700 bg-purple-100 border-purple-300',
      anxiety: 'text-indigo-600 bg-indigo-50 border-indigo-200',
      hope: 'text-green-600 bg-green-50 border-green-200',
      despair: 'text-gray-700 bg-gray-100 border-gray-300',
      love: 'text-pink-600 bg-pink-50 border-pink-200',
      disgust: 'text-orange-600 bg-orange-50 border-orange-200',
      surprise: 'text-teal-600 bg-teal-50 border-teal-200',
      confusion: 'text-gray-600 bg-gray-50 border-gray-200',
      determination: 'text-emerald-600 bg-emerald-50 border-emerald-200',
      pride: 'text-amber-600 bg-amber-50 border-amber-200',
      shame: 'text-rose-600 bg-rose-50 border-rose-200',
    }
    return emotions[emotion.toLowerCase()] || 'text-gray-600 bg-gray-50 border-gray-200'
  }

  const getEmotionIcon = (emotion: string) => {
    const positive = ['joy', 'happiness', 'hope', 'love', 'pride', 'determination']
    const negative = ['sadness', 'grief', 'anger', 'rage', 'fear', 'terror', 'despair', 'shame', 'disgust']

    const emotionLower = emotion.toLowerCase()
    if (positive.some(e => emotionLower.includes(e))) {
      return <Smile className="w-4 h-4" />
    } else if (negative.some(e => emotionLower.includes(e))) {
      return <Frown className="w-4 h-4" />
    }
    return <Meh className="w-4 h-4" />
  }

  const getEmotionCategory = (emotion: string): 'positive' | 'negative' | 'neutral' => {
    const positive = ['joy', 'happiness', 'hope', 'love', 'pride', 'determination']
    const negative = ['sadness', 'grief', 'anger', 'rage', 'fear', 'terror', 'despair', 'shame', 'disgust']

    const emotionLower = emotion.toLowerCase()
    if (positive.some(e => emotionLower.includes(e))) return 'positive'
    if (negative.some(e => emotionLower.includes(e))) return 'negative'
    return 'neutral'
  }

  const getTrendIcon = (current: number, previous: number) => {
    if (current > previous + 1) return <TrendingUp className="w-4 h-4 text-green-600" />
    if (current < previous - 1) return <TrendingDown className="w-4 h-4 text-red-600" />
    return <Minus className="w-4 h-4 text-gray-400" />
  }

  const filteredStates = emotionalStates.filter((state) => {
    if (filter === 'all') return true
    return getEmotionCategory(state.primary_emotion) === filter
  })

  const sortedStates = [...filteredStates].sort((a, b) => a.chapter_number - b.chapter_number)

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-600">Loading emotional journey...</div>
      </div>
    )
  }

  if (emotionalStates.length === 0) {
    return (
      <div className="text-center py-12">
        <Heart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No emotional states tracked yet</p>
        <p className="text-sm text-gray-500 mt-2">Track emotional changes as the character develops</p>
      </div>
    )
  }

  // Calculate statistics
  const avgIntensity = emotionalStates.reduce((sum, s) => sum + s.intensity, 0) / emotionalStates.length
  const positiveCount = emotionalStates.filter(s => getEmotionCategory(s.primary_emotion) === 'positive').length
  const negativeCount = emotionalStates.filter(s => getEmotionCategory(s.primary_emotion) === 'negative').length
  const mostCommonEmotion = emotionalStates
    .reduce((acc: Record<string, number>, s) => {
      acc[s.primary_emotion] = (acc[s.primary_emotion] || 0) + 1
      return acc
    }, {})
  const topEmotion = Object.entries(mostCommonEmotion).sort(([, a], [, b]) => b - a)[0]

  return (
    <div className="space-y-6">
      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-200">
          <div className="flex items-center gap-2 mb-1">
            <Heart className="w-4 h-4 text-purple-600" />
            <span className="text-xs font-medium text-gray-600">Total States</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{emotionalStates.length}</div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
          <div className="flex items-center gap-2 mb-1">
            <Smile className="w-4 h-4 text-green-600" />
            <span className="text-xs font-medium text-gray-600">Positive</span>
          </div>
          <div className="text-2xl font-bold text-green-600">{positiveCount}</div>
        </div>

        <div className="bg-gradient-to-br from-red-50 to-rose-50 rounded-lg p-4 border border-red-200">
          <div className="flex items-center gap-2 mb-1">
            <Frown className="w-4 h-4 text-red-600" />
            <span className="text-xs font-medium text-gray-600">Negative</span>
          </div>
          <div className="text-2xl font-bold text-red-600">{negativeCount}</div>
        </div>

        <div className="bg-gradient-to-br from-yellow-50 to-amber-50 rounded-lg p-4 border border-yellow-200">
          <div className="flex items-center gap-2 mb-1">
            <Zap className="w-4 h-4 text-yellow-600" />
            <span className="text-xs font-medium text-gray-600">Avg Intensity</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{avgIntensity.toFixed(1)}</div>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'all'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          All States
        </button>
        <button
          onClick={() => setFilter('positive')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'positive'
              ? 'bg-green-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Positive
        </button>
        <button
          onClick={() => setFilter('negative')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'negative'
              ? 'bg-red-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Negative
        </button>
        <button
          onClick={() => setFilter('neutral')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'neutral'
              ? 'bg-gray-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Neutral
        </button>
      </div>

      {/* Emotional Timeline Chart */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Emotional Intensity Over Time</h3>
        <div className="relative h-48">
          {/* Y-axis labels */}
          <div className="absolute left-0 top-0 bottom-0 flex flex-col justify-between text-xs text-gray-500 pr-2">
            <span>10</span>
            <span>5</span>
            <span>0</span>
          </div>

          {/* Chart area */}
          <div className="ml-8 h-full relative">
            {/* Grid lines */}
            <div className="absolute inset-0 flex flex-col justify-between">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="border-t border-gray-200" />
              ))}
            </div>

            {/* Data points and line */}
            <svg className="absolute inset-0 w-full h-full">
              {sortedStates.map((state, index) => {
                if (index === 0) return null
                const prevState = sortedStates[index - 1]
                const x1 = ((prevState.chapter_number - sortedStates[0].chapter_number) / (sortedStates[sortedStates.length - 1].chapter_number - sortedStates[0].chapter_number)) * 100
                const y1 = 100 - (prevState.intensity / 10) * 100
                const x2 = ((state.chapter_number - sortedStates[0].chapter_number) / (sortedStates[sortedStates.length - 1].chapter_number - sortedStates[0].chapter_number)) * 100
                const y2 = 100 - (state.intensity / 10) * 100

                const category = getEmotionCategory(state.primary_emotion)
                const color = category === 'positive' ? '#10b981' : category === 'negative' ? '#ef4444' : '#6b7280'

                return (
                  <line
                    key={state.id}
                    x1={`${x1}%`}
                    y1={`${y1}%`}
                    x2={`${x2}%`}
                    y2={`${y2}%`}
                    stroke={color}
                    strokeWidth="2"
                  />
                )
              })}

              {sortedStates.map((state) => {
                const x = ((state.chapter_number - sortedStates[0].chapter_number) / (sortedStates[sortedStates.length - 1].chapter_number - sortedStates[0].chapter_number)) * 100
                const y = 100 - (state.intensity / 10) * 100

                const category = getEmotionCategory(state.primary_emotion)
                const color = category === 'positive' ? '#10b981' : category === 'negative' ? '#ef4444' : '#6b7280'

                return (
                  <circle
                    key={state.id}
                    cx={`${x}%`}
                    cy={`${y}%`}
                    r="4"
                    fill={color}
                    className="cursor-pointer hover:r-6 transition-all"
                  >
                    <title>{`Ch. ${state.chapter_number}: ${state.primary_emotion} (${state.intensity})`}</title>
                  </circle>
                )
              })}
            </svg>
          </div>
        </div>

        {/* X-axis */}
        <div className="ml-8 flex justify-between text-xs text-gray-500 mt-2">
          <span>Ch. {sortedStates[0]?.chapter_number || 1}</span>
          <span>Ch. {sortedStates[sortedStates.length - 1]?.chapter_number || 1}</span>
        </div>
      </div>

      {/* States List */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Emotional States</h3>
        <div className="space-y-3">
          {sortedStates.map((state, index) => {
            const prevState = index > 0 ? sortedStates[index - 1] : null
            return (
              <div
                key={state.id}
                className={`border rounded-lg p-4 ${getEmotionColor(state.primary_emotion)}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2">
                      {getEmotionIcon(state.primary_emotion)}
                      <span className="font-semibold capitalize">{state.primary_emotion}</span>
                    </div>
                    <span className="text-sm text-gray-600">Chapter {state.chapter_number}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {prevState && getTrendIcon(state.intensity, prevState.intensity)}
                    <span className="text-sm font-medium">Intensity: {state.intensity}/10</span>
                  </div>
                </div>

                {state.scene_context && (
                  <p className="text-sm text-gray-700 mb-2">{state.scene_context}</p>
                )}

                {state.trigger_event && (
                  <div className="text-xs text-gray-600 bg-white bg-opacity-50 rounded px-2 py-1 inline-block">
                    <strong>Trigger:</strong> {state.trigger_event}
                  </div>
                )}

                {state.confidence_level && (
                  <div className="mt-2 flex items-center gap-2">
                    <Cloud className="w-3 h-3 text-gray-500" />
                    <span className="text-xs text-gray-600">
                      AI Confidence: {Math.round(state.confidence_level * 100)}%
                    </span>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
