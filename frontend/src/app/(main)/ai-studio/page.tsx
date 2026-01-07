/**
 * AI Writing Studio - The Ultimate Interface
 * Real-time AI prose generation with multi-agent system
 */
'use client'

import { useState, useEffect } from 'react'
import {
  Sparkles,
  Wand2,
  Brain,
  Zap,
  Target,
  Clock,
  DollarSign,
  TrendingUp,
  Copy,
  Download,
  RefreshCw,
  User,
  MapPin,
  BookOpen,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { useSession } from 'next-auth/react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

type GenerationMode = 'scene' | 'beats' | 'continue' | 'refine'
type Preset = 'fast_draft' | 'balanced' | 'premium' | 'creative_burst' | 'canon_strict'

interface GenerationResult {
  text: string
  model_used: string
  tokens_used: number
  cost: number
  quality_score: number
  refinement_iterations: number
  metadata: any
}

interface CanonCharacter {
  id: number
  name: string
  role: string
  goals?: string[]
}

interface CanonLocation {
  id: number
  name: string
  description: string
  atmosphere?: string
}

interface CanonThread {
  id: number
  name: string
  thread_type: string
  status: string
}

export default function AIStudioPage() {
  const { data: session } = useSession()
  const [mode, setMode] = useState<GenerationMode>('scene')
  const [preset, setPreset] = useState<Preset>('balanced')

  // Scene generation state
  const [sceneDescription, setSceneDescription] = useState('')
  const [targetWordCount, setTargetWordCount] = useState(1000)
  const [povCharacterId, setPovCharacterId] = useState<number | null>(null)

  // Generation state
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationProgress, setGenerationProgress] = useState<string>('')
  const [result, setResult] = useState<GenerationResult | null>(null)

  // Stats
  const [totalTokens, setTotalTokens] = useState(0)
  const [totalCost, setTotalCost] = useState(0)

  // Canon data
  const [characters, setCharacters] = useState<CanonCharacter[]>([])
  const [locations, setLocations] = useState<CanonLocation[]>([])
  const [threads, setThreads] = useState<CanonThread[]>([])
  const [isLoadingCanon, setIsLoadingCanon] = useState(false)

  // Selected canon for generation
  const [selectedCharacterIds, setSelectedCharacterIds] = useState<number[]>([])
  const [selectedLocationIds, setSelectedLocationIds] = useState<number[]>([])
  const [selectedThreadIds, setSelectedThreadIds] = useState<number[]>([])

  // Canon selector UI state
  const [showCanonSelector, setShowCanonSelector] = useState(true)

  // Load canon data on mount
  useEffect(() => {
    if (session?.accessToken) {
      loadCanonData()
    }
  }, [session?.accessToken])

  const loadCanonData = async () => {
    setIsLoadingCanon(true)
    try {
      const accessToken = (session?.user as any)?.accessToken
      const headers = {
        'Authorization': `Bearer ${accessToken}`,
      }

      // Load all canon entities in parallel
      const [charsRes, locsRes, threadsRes] = await Promise.all([
        fetch(`${API_URL}/api/canon/character?project_id=1`, { headers }),
        fetch(`${API_URL}/api/canon/location?project_id=1`, { headers }),
        fetch(`${API_URL}/api/canon/thread?project_id=1`, { headers })
      ])

      if (charsRes.ok) {
        const data = await charsRes.json()
        setCharacters(data)
      }
      if (locsRes.ok) {
        const data = await locsRes.json()
        setLocations(data)
      }
      if (threadsRes.ok) {
        const data = await threadsRes.json()
        setThreads(data)
      }
    } catch (error) {
      console.error('Failed to load canon data:', error)
    } finally {
      setIsLoadingCanon(false)
    }
  }

  const toggleCharacter = (id: number) => {
    setSelectedCharacterIds(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    )
  }

  const toggleLocation = (id: number) => {
    setSelectedLocationIds(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    )
  }

  const toggleThread = (id: number) => {
    setSelectedThreadIds(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    )
  }

  const handleGenerate = async () => {
    setIsGenerating(true)
    setGenerationProgress('Planning scene structure...')

    try {
      const accessToken = (session?.user as any)?.accessToken

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/projects/1/ai/generate-scene`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({
            scene_description: sceneDescription,
            target_word_count: targetWordCount,
            pov_character_id: povCharacterId,
            preset: preset,
            canon_context: {
              character_ids: selectedCharacterIds,
              location_ids: selectedLocationIds,
              thread_ids: selectedThreadIds
            }
          }),
        }
      )

      if (!response.ok) {
        throw new Error('Generation failed')
      }

      setGenerationProgress('Writing prose...')

      const data = await response.json()

      setGenerationProgress('Refining and polishing...')

      // Simulate progressive refinement
      setTimeout(() => {
        setResult(data)
        setTotalTokens(prev => prev + data.tokens_used)
        setTotalCost(prev => prev + data.cost)
        setIsGenerating(false)
        setGenerationProgress('')
      }, 1000)

    } catch (error) {
      console.error('Generation error:', error)
      alert('Generation failed. Please try again.')
      setIsGenerating(false)
      setGenerationProgress('')
    }
  }

  const presets = [
    {
      id: 'fast_draft',
      name: 'Fast Draft',
      icon: Zap,
      color: 'yellow',
      description: 'Quick generation (~15s)',
      model: 'GPT-4o Mini',
    },
    {
      id: 'balanced',
      name: 'Balanced',
      icon: Target,
      color: 'blue',
      description: 'Great quality (~30s)',
      model: 'Claude Sonnet',
    },
    {
      id: 'premium',
      name: 'Premium',
      icon: Sparkles,
      color: 'purple',
      description: 'Best quality (~60s)',
      model: 'Claude Opus',
    },
    {
      id: 'creative_burst',
      name: 'Creative',
      icon: Wand2,
      color: 'pink',
      description: 'Experimental ideas',
      model: 'GPT-4o',
    },
    {
      id: 'canon_strict',
      name: 'Canon Strict',
      icon: Brain,
      color: 'green',
      description: 'Maximum consistency',
      model: 'Claude Opus',
    },
  ]

  const selectedPreset = presets.find(p => p.id === preset)

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg">
            <Sparkles className="h-8 w-8 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              AI Writing Studio
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Multi-agent AI prose generation with RAG and iterative refinement
            </p>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center space-x-2 mb-1">
            <Zap className="h-4 w-4 text-yellow-500" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Tokens Used</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {totalTokens.toLocaleString()}
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center space-x-2 mb-1">
            <DollarSign className="h-4 w-4 text-green-500" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Cost (USD)</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            ${totalCost.toFixed(3)}
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center space-x-2 mb-1">
            <TrendingUp className="h-4 w-4 text-blue-500" />
            <span className="text-sm text-gray-600 dark:text-gray-400">Quality</span>
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">
            {result ? `${result.quality_score.toFixed(1)}/10` : '--'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Controls */}
        <div className="lg:col-span-1 space-y-6">
          {/* Preset Selection */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Generation Preset
            </h3>

            <div className="space-y-2">
              {presets.map((p) => {
                const Icon = p.icon
                const isSelected = preset === p.id

                return (
                  <button
                    key={p.id}
                    onClick={() => setPreset(p.id as Preset)}
                    className={`w-full flex items-start p-3 border-2 rounded-lg transition ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <div className={`p-2 rounded-lg mr-3 ${
                      p.color === 'yellow' ? 'bg-yellow-100 dark:bg-yellow-900/30' :
                      p.color === 'blue' ? 'bg-blue-100 dark:bg-blue-900/30' :
                      p.color === 'purple' ? 'bg-purple-100 dark:bg-purple-900/30' :
                      p.color === 'pink' ? 'bg-pink-100 dark:bg-pink-900/30' :
                      'bg-green-100 dark:bg-green-900/30'
                    }`}>
                      <Icon className={`h-5 w-5 ${
                        p.color === 'yellow' ? 'text-yellow-600' :
                        p.color === 'blue' ? 'text-blue-600' :
                        p.color === 'purple' ? 'text-purple-600' :
                        p.color === 'pink' ? 'text-pink-600' :
                        'text-green-600'
                      }`} />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="font-medium text-gray-900 dark:text-white">
                        {p.name}
                      </div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">
                        {p.description}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                        {p.model}
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Canon Selector */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setShowCanonSelector(!showCanonSelector)}
              className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700/50 transition"
            >
              <div className="flex items-center space-x-2">
                <BookOpen className="h-5 w-5 text-indigo-600" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Canon Context
                </h3>
                {(selectedCharacterIds.length + selectedLocationIds.length + selectedThreadIds.length) > 0 && (
                  <span className="px-2 py-0.5 text-xs bg-indigo-100 text-indigo-700 rounded-full">
                    {selectedCharacterIds.length + selectedLocationIds.length + selectedThreadIds.length} selected
                  </span>
                )}
              </div>
              {showCanonSelector ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
            </button>

            {showCanonSelector && (
              <div className="px-6 pb-6 space-y-4">
                {isLoadingCanon ? (
                  <div className="text-center py-4">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
                    <p className="text-sm text-gray-600 mt-2">Loading canon...</p>
                  </div>
                ) : (
                  <>
                    {/* Characters */}
                    {characters.length > 0 && (
                      <div>
                        <div className="flex items-center space-x-2 mb-2">
                          <User className="h-4 w-4 text-purple-600" />
                          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Characters ({selectedCharacterIds.length}/{characters.length})
                          </span>
                        </div>
                        <div className="space-y-1 max-h-40 overflow-y-auto">
                          {characters.map((char) => (
                            <label
                              key={char.id}
                              className="flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded cursor-pointer"
                            >
                              <input
                                type="checkbox"
                                checked={selectedCharacterIds.includes(char.id)}
                                onChange={() => toggleCharacter(char.id)}
                                className="mr-2 rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                              />
                              <div className="flex-1">
                                <p className="text-sm font-medium text-gray-900 dark:text-white">{char.name}</p>
                                {char.role && (
                                  <p className="text-xs text-gray-500">{char.role}</p>
                                )}
                              </div>
                            </label>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Locations */}
                    {locations.length > 0 && (
                      <div>
                        <div className="flex items-center space-x-2 mb-2">
                          <MapPin className="h-4 w-4 text-emerald-600" />
                          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Locations ({selectedLocationIds.length}/{locations.length})
                          </span>
                        </div>
                        <div className="space-y-1 max-h-40 overflow-y-auto">
                          {locations.map((loc) => (
                            <label
                              key={loc.id}
                              className="flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded cursor-pointer"
                            >
                              <input
                                type="checkbox"
                                checked={selectedLocationIds.includes(loc.id)}
                                onChange={() => toggleLocation(loc.id)}
                                className="mr-2 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500"
                              />
                              <div className="flex-1">
                                <p className="text-sm font-medium text-gray-900 dark:text-white">{loc.name}</p>
                                {loc.atmosphere && (
                                  <p className="text-xs text-gray-500">{loc.atmosphere}</p>
                                )}
                              </div>
                            </label>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Plot Threads */}
                    {threads.length > 0 && (
                      <div>
                        <div className="flex items-center space-x-2 mb-2">
                          <Sparkles className="h-4 w-4 text-amber-600" />
                          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Plot Threads ({selectedThreadIds.length}/{threads.length})
                          </span>
                        </div>
                        <div className="space-y-1 max-h-40 overflow-y-auto">
                          {threads.map((thread) => (
                            <label
                              key={thread.id}
                              className="flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded cursor-pointer"
                            >
                              <input
                                type="checkbox"
                                checked={selectedThreadIds.includes(thread.id)}
                                onChange={() => toggleThread(thread.id)}
                                className="mr-2 rounded border-gray-300 text-amber-600 focus:ring-amber-500"
                              />
                              <div className="flex-1">
                                <p className="text-sm font-medium text-gray-900 dark:text-white">{thread.name}</p>
                                <p className="text-xs text-gray-500 capitalize">
                                  {thread.thread_type.replace('_', ' ')} • {thread.status}
                                </p>
                              </div>
                            </label>
                          ))}
                        </div>
                      </div>
                    )}

                    {characters.length === 0 && locations.length === 0 && threads.length === 0 && (
                      <div className="text-center py-4">
                        <BookOpen className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-gray-600">No canon entities found</p>
                        <p className="text-xs text-gray-500 mt-1">
                          Visit Story Bible to add characters, locations, and threads
                        </p>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>

          {/* Scene Parameters */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Scene Parameters
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Target Word Count
                </label>
                <input
                  type="number"
                  value={targetWordCount}
                  onChange={(e) => setTargetWordCount(parseInt(e.target.value))}
                  min="100"
                  max="5000"
                  step="100"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
                <p className="text-xs text-gray-500 mt-1">
                  100-5000 words
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  POV Character
                </label>
                <select
                  value={povCharacterId || ''}
                  onChange={(e) => setPovCharacterId(e.target.value ? parseInt(e.target.value) : null)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="">Auto-detect</option>
                  <option value="1">Sarah Chen</option>
                  <option value="2">Marcus Stone</option>
                  <option value="3">Dr. Elena Rodriguez</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Generation Area */}
        <div className="lg:col-span-2 space-y-6">
          {/* Input Area */}
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Scene Description
            </h3>

            <textarea
              value={sceneDescription}
              onChange={(e) => setSceneDescription(e.target.value)}
              placeholder="Describe what happens in this scene... (e.g., 'Sarah discovers the hidden door behind the bookshelf and ventures into the dark passage')"
              className="w-full h-32 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white resize-none"
            />

            <div className="mt-4 flex items-center justify-between">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {selectedPreset && (
                  <span>
                    Using <span className="font-medium">{selectedPreset.name}</span> preset
                  </span>
                )}
              </div>

              <button
                onClick={handleGenerate}
                disabled={isGenerating || !sceneDescription.trim()}
                className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium shadow-lg"
              >
                {isGenerating ? (
                  <>
                    <RefreshCw className="h-5 w-5 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5" />
                    <span>Generate Scene</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Progress Indicator */}
          {isGenerating && generationProgress && (
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg border border-purple-200 dark:border-purple-800 p-6">
              <div className="flex items-center space-x-3">
                <RefreshCw className="h-5 w-5 text-purple-600 dark:text-purple-400 animate-spin" />
                <div>
                  <p className="font-medium text-purple-900 dark:text-purple-200">
                    {generationProgress}
                  </p>
                  <p className="text-sm text-purple-700 dark:text-purple-300">
                    Multi-agent AI system at work...
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Result Area */}
          {result && (
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
              {/* Result Header */}
              <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-4 text-white">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Sparkles className="h-5 w-5" />
                    <div>
                      <h3 className="font-semibold">Generated Prose</h3>
                      <p className="text-sm text-purple-100">
                        Quality: {result.quality_score.toFixed(1)}/10 •
                        {result.refinement_iterations} refinement{result.refinement_iterations !== 1 ? 's' : ''} •
                        {result.tokens_used.toLocaleString()} tokens
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => navigator.clipboard.writeText(result.text)}
                      className="p-2 hover:bg-white/20 rounded-lg transition"
                      title="Copy to clipboard"
                    >
                      <Copy className="h-5 w-5" />
                    </button>
                    <button
                      className="p-2 hover:bg-white/20 rounded-lg transition"
                      title="Download"
                    >
                      <Download className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Generated Text */}
              <div className="p-6">
                <div className="prose dark:prose-invert max-w-none">
                  {result.text.split('\n\n').map((paragraph, i) => (
                    <p key={i} className="mb-4 text-gray-800 dark:text-gray-200 leading-relaxed">
                      {paragraph}
                    </p>
                  ))}
                </div>
              </div>

              {/* Metadata */}
              <div className="bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 p-4">
                <div className="grid grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Model:</span>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {result.model_used}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Words:</span>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {result.text.split(' ').length}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Cost:</span>
                    <p className="font-medium text-gray-900 dark:text-white">
                      ${result.cost.toFixed(4)}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-600 dark:text-gray-400">Iterations:</span>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {result.refinement_iterations}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
