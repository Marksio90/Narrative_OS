'use client'

import { useState, useEffect } from 'react'
import { TrendingUp, Flag, Star, Circle, ChevronRight, Sparkles } from 'lucide-react'

interface CharacterArc {
  id: number
  arc_type: string
  name?: string
  start_chapter?: number
  end_chapter?: number
  current_chapter?: number
  completion_percentage: number
}

interface Milestone {
  id: number
  arc_id: number
  milestone_type: string
  chapter_number: number
  description: string
  significance: number
  notes?: string
  created_at: string
}

interface CharacterArcTimelineProps {
  characterId: number
  arcs: CharacterArc[]
}

export default function CharacterArcTimeline({ characterId, arcs }: CharacterArcTimelineProps) {
  const [selectedArc, setSelectedArc] = useState<CharacterArc | null>(null)
  const [milestones, setMilestones] = useState<Milestone[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (arcs.length > 0 && !selectedArc) {
      setSelectedArc(arcs[0])
    }
  }, [arcs])

  useEffect(() => {
    if (selectedArc) {
      fetchMilestones(selectedArc.id)
    }
  }, [selectedArc])

  const fetchMilestones = async (arcId: number) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/character-arcs/arcs/${arcId}/milestones`)
      if (response.ok) {
        const data = await response.json()
        setMilestones(data)
      }
    } catch (error) {
      console.error('Failed to fetch milestones:', error)
    } finally {
      setLoading(false)
    }
  }

  const getMilestoneIcon = (type: string) => {
    const icons: Record<string, any> = {
      inciting_incident: Flag,
      turning_point: TrendingUp,
      crisis: Star,
      climax: Star,
      resolution: Circle,
      revelation: Sparkles,
      setback: Flag,
      triumph: Star,
    }
    const Icon = icons[type] || Circle
    return <Icon className="w-4 h-4" />
  }

  const getMilestoneColor = (type: string) => {
    const colors: Record<string, string> = {
      inciting_incident: 'bg-blue-500',
      turning_point: 'bg-purple-500',
      crisis: 'bg-orange-500',
      climax: 'bg-red-500',
      resolution: 'bg-green-500',
      revelation: 'bg-yellow-500',
      setback: 'bg-gray-500',
      triumph: 'bg-emerald-500',
    }
    return colors[type] || 'bg-gray-400'
  }

  const getMilestoneLabel = (type: string) => {
    const labels: Record<string, string> = {
      inciting_incident: 'Inciting Incident',
      turning_point: 'Turning Point',
      crisis: 'Crisis',
      climax: 'Climax',
      resolution: 'Resolution',
      revelation: 'Revelation',
      setback: 'Setback',
      triumph: 'Triumph',
    }
    return labels[type] || type
  }

  if (arcs.length === 0) {
    return (
      <div className="text-center py-12">
        <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No character arcs found</p>
        <p className="text-sm text-gray-500 mt-2">Create an arc to start tracking milestones</p>
      </div>
    )
  }

  const sortedMilestones = [...milestones].sort((a, b) => a.chapter_number - b.chapter_number)
  const minChapter = selectedArc?.start_chapter || 1
  const maxChapter = selectedArc?.end_chapter || 30
  const currentChapter = selectedArc?.current_chapter || minChapter

  return (
    <div className="space-y-6">
      {/* Arc Selector */}
      {arcs.length > 1 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Select Arc</label>
          <select
            value={selectedArc?.id || ''}
            onChange={(e) => {
              const arc = arcs.find((a) => a.id === parseInt(e.target.value))
              setSelectedArc(arc || null)
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            {arcs.map((arc) => (
              <option key={arc.id} value={arc.id}>
                {arc.name || `${arc.arc_type} Arc`}
              </option>
            ))}
          </select>
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="text-gray-600">Loading timeline...</div>
        </div>
      ) : (
        <>
          {/* Timeline Visualization */}
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Arc Timeline</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Chapter {minChapter} - {maxChapter}
                </p>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600">Current Position</div>
                <div className="text-2xl font-bold text-purple-600">Chapter {currentChapter}</div>
              </div>
            </div>

            {/* Progress Bar with Milestones */}
            <div className="relative">
              {/* Progress Track */}
              <div className="h-3 bg-gray-300 rounded-full overflow-hidden">
                <div
                  className="h-full bg-purple-600 transition-all"
                  style={{ width: `${selectedArc?.completion_percentage || 0}%` }}
                />
              </div>

              {/* Current Position Indicator */}
              <div
                className="absolute top-1/2 -translate-y-1/2 w-6 h-6 bg-purple-600 border-4 border-white rounded-full shadow-lg"
                style={{
                  left: `${((currentChapter - minChapter) / (maxChapter - minChapter)) * 100}%`,
                  transform: 'translate(-50%, -50%)',
                }}
              />

              {/* Milestone Markers */}
              {sortedMilestones.map((milestone) => {
                const position = ((milestone.chapter_number - minChapter) / (maxChapter - minChapter)) * 100
                return (
                  <div
                    key={milestone.id}
                    className="absolute"
                    style={{
                      left: `${position}%`,
                      top: '-24px',
                      transform: 'translateX(-50%)',
                    }}
                  >
                    <div
                      className={`w-8 h-8 ${getMilestoneColor(
                        milestone.milestone_type
                      )} rounded-full flex items-center justify-center text-white shadow-lg cursor-pointer hover:scale-110 transition-transform`}
                      title={milestone.description}
                    >
                      {getMilestoneIcon(milestone.milestone_type)}
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Chapter Labels */}
            <div className="flex justify-between mt-8 text-xs text-gray-600">
              <span>Ch. {minChapter}</span>
              <span>Ch. {Math.round((minChapter + maxChapter) / 2)}</span>
              <span>Ch. {maxChapter}</span>
            </div>
          </div>

          {/* Milestones List */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Milestones</h3>
              <button className="text-sm text-purple-600 hover:text-purple-700 font-medium">
                + Add Milestone
              </button>
            </div>

            {sortedMilestones.length === 0 ? (
              <div className="text-center py-12 bg-gray-50 rounded-lg">
                <Flag className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No milestones recorded yet</p>
                <p className="text-sm text-gray-500 mt-2">Track key moments in the character's journey</p>
              </div>
            ) : (
              <div className="space-y-3">
                {sortedMilestones.map((milestone, index) => (
                  <div
                    key={milestone.id}
                    className="bg-white border border-gray-200 rounded-lg p-4 hover:border-purple-300 transition-colors"
                  >
                    <div className="flex items-start gap-4">
                      {/* Timeline Connector */}
                      <div className="flex flex-col items-center">
                        <div
                          className={`w-10 h-10 ${getMilestoneColor(
                            milestone.milestone_type
                          )} rounded-full flex items-center justify-center text-white flex-shrink-0`}
                        >
                          {getMilestoneIcon(milestone.milestone_type)}
                        </div>
                        {index < sortedMilestones.length - 1 && (
                          <div className="w-0.5 h-full bg-gray-200 mt-2" style={{ minHeight: '20px' }} />
                        )}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4 mb-2">
                          <div>
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-semibold text-gray-900">
                                {getMilestoneLabel(milestone.milestone_type)}
                              </span>
                              <span className="text-sm text-gray-500">Chapter {milestone.chapter_number}</span>
                            </div>
                            <p className="text-gray-700">{milestone.description}</p>
                          </div>
                          <div className="flex items-center gap-1 text-yellow-500 flex-shrink-0">
                            {Array.from({ length: 5 }).map((_, i) => (
                              <Star
                                key={i}
                                className={`w-3 h-3 ${
                                  i < milestone.significance ? 'fill-current' : 'stroke-current fill-transparent'
                                }`}
                              />
                            ))}
                          </div>
                        </div>
                        {milestone.notes && (
                          <p className="text-sm text-gray-600 mt-2 italic">{milestone.notes}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* AI Analysis Section */}
          <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-6 border border-purple-200">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Arc Analysis</h3>
                <p className="text-sm text-gray-600">
                  Get AI-powered insights on arc pacing, consistency, and emotional depth
                </p>
              </div>
              <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                <Sparkles className="w-4 h-4" />
                Analyze Arc
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
