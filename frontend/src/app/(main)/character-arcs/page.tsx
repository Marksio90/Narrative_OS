'use client'

import { useState, useEffect } from 'react'
import { TrendingUp, User, Target, Heart, BarChart3, Sparkles, Plus } from 'lucide-react'
import CharacterArcTimeline from '@/components/CharacterArcTimeline'
import EmotionalStateTracker from '@/components/EmotionalStateTracker'
import GoalProgressVisualization from '@/components/GoalProgressVisualization'

interface Character {
  id: number
  name: string
  role?: string
}

interface CharacterArc {
  id: number
  character_id: number
  character_name?: string
  arc_type: string
  name?: string
  description?: string
  completion_percentage: number
  is_on_track: boolean
  pacing_score?: number
  consistency_score?: number
  start_chapter?: number
  end_chapter?: number
  current_chapter?: number
}

interface ArcSummary {
  character_id: number
  character_name: string
  arc_count: number
  avg_completion: number
  on_track_count: number
  off_track_count: number
}

export default function CharacterArcsPage() {
  const [characters, setCharacters] = useState<Character[]>([])
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null)
  const [arcs, setArcs] = useState<CharacterArc[]>([])
  const [arcSummaries, setArcSummaries] = useState<ArcSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'timeline' | 'emotional' | 'goals'>('timeline')
  const [showCreateModal, setShowCreateModal] = useState(false)

  // Get current project ID (you'll need to adapt this to your auth/context)
  const projectId = 1 // Replace with actual project ID from context

  useEffect(() => {
    fetchCharacters()
    fetchArcSummaries()
  }, [])

  useEffect(() => {
    if (selectedCharacter) {
      fetchCharacterArcs(selectedCharacter.id)
    }
  }, [selectedCharacter])

  const fetchCharacters = async () => {
    try {
      const response = await fetch(`/api/canon/characters?project_id=${projectId}`)
      if (response.ok) {
        const data = await response.json()
        setCharacters(data)
        if (data.length > 0 && !selectedCharacter) {
          setSelectedCharacter(data[0])
        }
      }
    } catch (error) {
      console.error('Failed to fetch characters:', error)
    }
  }

  const fetchArcSummaries = async () => {
    try {
      const response = await fetch(`/api/character-arcs/summaries?project_id=${projectId}`)
      if (response.ok) {
        const data = await response.json()
        setArcSummaries(data)
      }
    } catch (error) {
      console.error('Failed to fetch arc summaries:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchCharacterArcs = async (characterId: number) => {
    try {
      const response = await fetch(`/api/character-arcs/character/${characterId}/arcs`)
      if (response.ok) {
        const data = await response.json()
        setArcs(data)
      }
    } catch (error) {
      console.error('Failed to fetch character arcs:', error)
    }
  }

  const getArcTypeLabel = (arcType: string) => {
    const labels: Record<string, string> = {
      positive_change: 'Positive Change',
      negative_change: 'Negative Change',
      flat_arc: 'Flat Arc',
      transformation: 'Transformation',
      redemption: 'Redemption',
      corruption: 'Corruption',
      disillusionment: 'Disillusionment',
      coming_of_age: 'Coming of Age',
      tragic: 'Tragic Arc',
    }
    return labels[arcType] || arcType
  }

  const getArcTypeColor = (arcType: string) => {
    const colors: Record<string, string> = {
      positive_change: 'text-green-600 bg-green-50',
      negative_change: 'text-red-600 bg-red-50',
      flat_arc: 'text-blue-600 bg-blue-50',
      transformation: 'text-purple-600 bg-purple-50',
      redemption: 'text-emerald-600 bg-emerald-50',
      corruption: 'text-orange-600 bg-orange-50',
      disillusionment: 'text-gray-600 bg-gray-50',
      coming_of_age: 'text-indigo-600 bg-indigo-50',
      tragic: 'text-rose-600 bg-rose-50',
    }
    return colors[arcType] || 'text-gray-600 bg-gray-50'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading character arcs...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Character Arc Tracker</h1>
                <p className="text-sm text-gray-600">Track character development and emotional journeys</p>
              </div>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Arc
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center gap-3 mb-2">
              <User className="w-5 h-5 text-blue-600" />
              <span className="text-sm font-medium text-gray-600">Characters</span>
            </div>
            <div className="text-3xl font-bold text-gray-900">{characters.length}</div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="w-5 h-5 text-purple-600" />
              <span className="text-sm font-medium text-gray-600">Total Arcs</span>
            </div>
            <div className="text-3xl font-bold text-gray-900">
              {arcSummaries.reduce((sum, s) => sum + s.arc_count, 0)}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center gap-3 mb-2">
              <Target className="w-5 h-5 text-green-600" />
              <span className="text-sm font-medium text-gray-600">On Track</span>
            </div>
            <div className="text-3xl font-bold text-green-600">
              {arcSummaries.reduce((sum, s) => sum + s.on_track_count, 0)}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center gap-3 mb-2">
              <BarChart3 className="w-5 h-5 text-orange-600" />
              <span className="text-sm font-medium text-gray-600">Avg Progress</span>
            </div>
            <div className="text-3xl font-bold text-gray-900">
              {arcSummaries.length > 0
                ? Math.round(
                    arcSummaries.reduce((sum, s) => sum + s.avg_completion, 0) / arcSummaries.length
                  )
                : 0}
              %
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Character Selector */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                <h3 className="text-sm font-semibold text-gray-900">Characters</h3>
              </div>
              <div className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
                {characters.map((character) => {
                  const summary = arcSummaries.find((s) => s.character_id === character.id)
                  return (
                    <button
                      key={character.id}
                      onClick={() => setSelectedCharacter(character)}
                      className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors ${
                        selectedCharacter?.id === character.id ? 'bg-purple-50 border-l-4 border-purple-600' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">{character.name}</div>
                          {character.role && (
                            <div className="text-xs text-gray-500 mt-1">{character.role}</div>
                          )}
                        </div>
                        {summary && summary.arc_count > 0 && (
                          <div className="text-right">
                            <div className="text-xs font-medium text-purple-600">
                              {summary.arc_count} {summary.arc_count === 1 ? 'arc' : 'arcs'}
                            </div>
                            <div className="text-xs text-gray-500">{Math.round(summary.avg_completion)}%</div>
                          </div>
                        )}
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-3">
            {selectedCharacter ? (
              <div className="space-y-6">
                {/* Character Header */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h2 className="text-xl font-bold text-gray-900">{selectedCharacter.name}</h2>
                      <p className="text-sm text-gray-600 mt-1">
                        {arcs.length} {arcs.length === 1 ? 'arc' : 'arcs'} tracked
                      </p>
                    </div>
                    <button
                      className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm"
                    >
                      <Sparkles className="w-4 h-4" />
                      AI Analysis
                    </button>
                  </div>

                  {/* Arc Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {arcs.map((arc) => (
                      <div
                        key={arc.id}
                        className="border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition-colors"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-1">
                            <div className={`inline-block px-2 py-1 rounded text-xs font-medium ${getArcTypeColor(arc.arc_type)}`}>
                              {getArcTypeLabel(arc.arc_type)}
                            </div>
                            {arc.name && (
                              <h4 className="font-semibold text-gray-900 mt-2">{arc.name}</h4>
                            )}
                          </div>
                          <div
                            className={`px-2 py-1 rounded text-xs font-medium ${
                              arc.is_on_track ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'
                            }`}
                          >
                            {arc.is_on_track ? '✓ On Track' : '⚠ Off Track'}
                          </div>
                        </div>

                        {arc.description && (
                          <p className="text-sm text-gray-600 mb-3 line-clamp-2">{arc.description}</p>
                        )}

                        {/* Progress Bar */}
                        <div className="mb-3">
                          <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
                            <span>Progress</span>
                            <span className="font-medium">{Math.round(arc.completion_percentage)}%</span>
                          </div>
                          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-purple-600 transition-all"
                              style={{ width: `${arc.completion_percentage}%` }}
                            />
                          </div>
                        </div>

                        {/* Scores */}
                        <div className="flex items-center gap-4 text-xs">
                          {arc.pacing_score !== null && arc.pacing_score !== undefined && (
                            <div className="flex items-center gap-1">
                              <BarChart3 className="w-3 h-3 text-gray-400" />
                              <span className="text-gray-600">Pacing: {arc.pacing_score.toFixed(1)}</span>
                            </div>
                          )}
                          {arc.consistency_score !== null && arc.consistency_score !== undefined && (
                            <div className="flex items-center gap-1">
                              <Target className="w-3 h-3 text-gray-400" />
                              <span className="text-gray-600">Consistency: {arc.consistency_score.toFixed(1)}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Tabs */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                  <div className="border-b border-gray-200">
                    <div className="flex gap-6 px-6">
                      <button
                        onClick={() => setActiveTab('timeline')}
                        className={`py-4 border-b-2 font-medium text-sm transition-colors ${
                          activeTab === 'timeline'
                            ? 'border-purple-600 text-purple-600'
                            : 'border-transparent text-gray-600 hover:text-gray-900'
                        }`}
                      >
                        Arc Timeline
                      </button>
                      <button
                        onClick={() => setActiveTab('emotional')}
                        className={`py-4 border-b-2 font-medium text-sm transition-colors ${
                          activeTab === 'emotional'
                            ? 'border-purple-600 text-purple-600'
                            : 'border-transparent text-gray-600 hover:text-gray-900'
                        }`}
                      >
                        Emotional Journey
                      </button>
                      <button
                        onClick={() => setActiveTab('goals')}
                        className={`py-4 border-b-2 font-medium text-sm transition-colors ${
                          activeTab === 'goals'
                            ? 'border-purple-600 text-purple-600'
                            : 'border-transparent text-gray-600 hover:text-gray-900'
                        }`}
                      >
                        Goals & Milestones
                      </button>
                    </div>
                  </div>

                  <div className="p-6">
                    {activeTab === 'timeline' && (
                      <CharacterArcTimeline characterId={selectedCharacter.id} arcs={arcs} />
                    )}
                    {activeTab === 'emotional' && (
                      <EmotionalStateTracker characterId={selectedCharacter.id} />
                    )}
                    {activeTab === 'goals' && (
                      <GoalProgressVisualization characterId={selectedCharacter.id} />
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <User className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Select a character to view their arc development</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
