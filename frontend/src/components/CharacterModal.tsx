'use client'

import { useState, useEffect } from 'react'
import { X, Plus, Trash2, User, Target, Heart, Shield, Zap, MessageSquare, TrendingUp } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Character {
  id?: number
  project_id: number
  name: string
  role: string
  goals: string[]
  values: string[]
  fears: string[]
  secrets: string[]
  behavioral_limits: string[]
  voice_profile?: {
    vocabulary_level: string
    sentence_structure: string
    emotional_expression: string
    quirks: string[]
  }
  arc?: {
    starting_state: string
    goal_state: string
    key_transformations: string[]
  }
}

interface CharacterModalProps {
  character: Character | null
  onClose: () => void
  onSave: () => void
  accessToken: string
  projectId?: number
}

export default function CharacterModal({
  character,
  onClose,
  onSave,
  accessToken,
  projectId = 1
}: CharacterModalProps) {
  const [formData, setFormData] = useState<Character>({
    project_id: projectId,
    name: '',
    role: '',
    goals: [],
    values: [],
    fears: [],
    secrets: [],
    behavioral_limits: [],
    voice_profile: {
      vocabulary_level: '',
      sentence_structure: '',
      emotional_expression: '',
      quirks: []
    },
    arc: {
      starting_state: '',
      goal_state: '',
      key_transformations: []
    }
  })

  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Input states for adding new items to arrays
  const [newGoal, setNewGoal] = useState('')
  const [newValue, setNewValue] = useState('')
  const [newFear, setNewFear] = useState('')
  const [newSecret, setNewSecret] = useState('')
  const [newLimit, setNewLimit] = useState('')
  const [newQuirk, setNewQuirk] = useState('')
  const [newTransformation, setNewTransformation] = useState('')

  useEffect(() => {
    if (character) {
      setFormData({
        ...character,
        voice_profile: character.voice_profile || {
          vocabulary_level: '',
          sentence_structure: '',
          emotional_expression: '',
          quirks: []
        },
        arc: character.arc || {
          starting_state: '',
          goal_state: '',
          key_transformations: []
        }
      })
    }
  }, [character])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    setError(null)

    try {
      const url = character
        ? `${API_URL}/api/canon/character/${character.id}`
        : `${API_URL}/api/canon/character`

      const method = character ? 'PUT' : 'POST'

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to save character')
      }

      onSave()
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsSaving(false)
    }
  }

  const addArrayItem = (field: keyof Character, value: string, setter: (val: string) => void) => {
    if (!value.trim()) return
    const currentArray = (formData[field] as string[]) || []
    setFormData({
      ...formData,
      [field]: [...currentArray, value.trim()]
    })
    setter('')
  }

  const removeArrayItem = (field: keyof Character, index: number) => {
    const currentArray = (formData[field] as string[]) || []
    setFormData({
      ...formData,
      [field]: currentArray.filter((_, i) => i !== index)
    })
  }

  const addQuirk = () => {
    if (!newQuirk.trim()) return
    setFormData({
      ...formData,
      voice_profile: {
        ...formData.voice_profile!,
        quirks: [...(formData.voice_profile?.quirks || []), newQuirk.trim()]
      }
    })
    setNewQuirk('')
  }

  const removeQuirk = (index: number) => {
    setFormData({
      ...formData,
      voice_profile: {
        ...formData.voice_profile!,
        quirks: (formData.voice_profile?.quirks || []).filter((_, i) => i !== index)
      }
    })
  }

  const addTransformation = () => {
    if (!newTransformation.trim()) return
    setFormData({
      ...formData,
      arc: {
        ...formData.arc!,
        key_transformations: [...(formData.arc?.key_transformations || []), newTransformation.trim()]
      }
    })
    setNewTransformation('')
  }

  const removeTransformation = (index: number) => {
    setFormData({
      ...formData,
      arc: {
        ...formData.arc!,
        key_transformations: (formData.arc?.key_transformations || []).filter((_, i) => i !== index)
      }
    })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full my-8">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <User className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {character ? 'Edit Character' : 'New Character'}
              </h2>
              <p className="text-sm text-gray-600">
                Define your character's core traits and development
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {/* Basic Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <User className="h-5 w-5 text-indigo-600" />
              <span>Basic Information</span>
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role
                </label>
                <input
                  type="text"
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  placeholder="e.g., Protagonist, Mentor, Antagonist"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Goals */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Target className="h-5 w-5 text-green-600" />
              <span>Goals & Motivations</span>
            </h3>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newGoal}
                onChange={(e) => setNewGoal(e.target.value)}
                placeholder="What does this character want?"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addArrayItem('goals', newGoal, setNewGoal))}
              />
              <button
                type="button"
                onClick={() => addArrayItem('goals', newGoal, setNewGoal)}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.goals.map((goal, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center space-x-2 px-3 py-1.5 bg-green-50 text-green-700 rounded-lg text-sm"
                >
                  <span>{goal}</span>
                  <button
                    type="button"
                    onClick={() => removeArrayItem('goals', idx)}
                    className="text-green-600 hover:text-green-800"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Values */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Heart className="h-5 w-5 text-red-600" />
              <span>Core Values</span>
            </h3>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newValue}
                onChange={(e) => setNewValue(e.target.value)}
                placeholder="What does this character believe in?"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addArrayItem('values', newValue, setNewValue))}
              />
              <button
                type="button"
                onClick={() => addArrayItem('values', newValue, setNewValue)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.values.map((value, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center space-x-2 px-3 py-1.5 bg-red-50 text-red-700 rounded-lg text-sm"
                >
                  <span>{value}</span>
                  <button
                    type="button"
                    onClick={() => removeArrayItem('values', idx)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Fears */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Shield className="h-5 w-5 text-amber-600" />
              <span>Fears & Vulnerabilities</span>
            </h3>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newFear}
                onChange={(e) => setNewFear(e.target.value)}
                placeholder="What is this character afraid of?"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addArrayItem('fears', newFear, setNewFear))}
              />
              <button
                type="button"
                onClick={() => addArrayItem('fears', newFear, setNewFear)}
                className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.fears.map((fear, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center space-x-2 px-3 py-1.5 bg-amber-50 text-amber-700 rounded-lg text-sm"
                >
                  <span>{fear}</span>
                  <button
                    type="button"
                    onClick={() => removeArrayItem('fears', idx)}
                    className="text-amber-600 hover:text-amber-800"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Secrets */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Zap className="h-5 w-5 text-purple-600" />
              <span>Secrets & Hidden Depths</span>
            </h3>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newSecret}
                onChange={(e) => setNewSecret(e.target.value)}
                placeholder="What is this character hiding?"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addArrayItem('secrets', newSecret, setNewSecret))}
              />
              <button
                type="button"
                onClick={() => addArrayItem('secrets', newSecret, setNewSecret)}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.secrets.map((secret, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center space-x-2 px-3 py-1.5 bg-purple-50 text-purple-700 rounded-lg text-sm"
                >
                  <span>{secret}</span>
                  <button
                    type="button"
                    onClick={() => removeArrayItem('secrets', idx)}
                    className="text-purple-600 hover:text-purple-800"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Behavioral Limits */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Shield className="h-5 w-5 text-blue-600" />
              <span>Behavioral Limits</span>
            </h3>
            <p className="text-sm text-gray-600">What this character would NEVER do</p>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newLimit}
                onChange={(e) => setNewLimit(e.target.value)}
                placeholder="e.g., Would never betray a friend"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addArrayItem('behavioral_limits', newLimit, setNewLimit))}
              />
              <button
                type="button"
                onClick={() => addArrayItem('behavioral_limits', newLimit, setNewLimit)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.behavioral_limits.map((limit, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center space-x-2 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-lg text-sm"
                >
                  <span>{limit}</span>
                  <button
                    type="button"
                    onClick={() => removeArrayItem('behavioral_limits', idx)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    <Trash2 className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Voice Profile */}
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <MessageSquare className="h-5 w-5 text-indigo-600" />
              <span>Voice Profile (for AI generation)</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Vocabulary Level
                </label>
                <select
                  value={formData.voice_profile?.vocabulary_level || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    voice_profile: { ...formData.voice_profile!, vocabulary_level: e.target.value }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Select...</option>
                  <option value="simple">Simple (everyday words)</option>
                  <option value="moderate">Moderate (educated)</option>
                  <option value="sophisticated">Sophisticated (literary)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sentence Structure
                </label>
                <select
                  value={formData.voice_profile?.sentence_structure || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    voice_profile: { ...formData.voice_profile!, sentence_structure: e.target.value }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Select...</option>
                  <option value="short">Short & punchy</option>
                  <option value="varied">Varied (natural)</option>
                  <option value="complex">Complex & flowing</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Emotional Expression
                </label>
                <select
                  value={formData.voice_profile?.emotional_expression || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    voice_profile: { ...formData.voice_profile!, emotional_expression: e.target.value }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Select...</option>
                  <option value="reserved">Reserved (stoic)</option>
                  <option value="balanced">Balanced</option>
                  <option value="expressive">Expressive (passionate)</option>
                </select>
              </div>
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Speech Quirks</label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newQuirk}
                  onChange={(e) => setNewQuirk(e.target.value)}
                  placeholder="e.g., Uses nautical metaphors, Repeats 'you know'"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addQuirk())}
                />
                <button
                  type="button"
                  onClick={addQuirk}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                >
                  <Plus className="h-5 w-5" />
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.voice_profile?.quirks?.map((quirk, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center space-x-2 px-3 py-1.5 bg-indigo-50 text-indigo-700 rounded-lg text-sm"
                  >
                    <span>{quirk}</span>
                    <button
                      type="button"
                      onClick={() => removeQuirk(idx)}
                      className="text-indigo-600 hover:text-indigo-800"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Character Arc */}
          <div className="space-y-4 p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-purple-600" />
              <span>Character Arc</span>
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Starting State
                </label>
                <textarea
                  value={formData.arc?.starting_state || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    arc: { ...formData.arc!, starting_state: e.target.value }
                  })}
                  placeholder="Who is this character at the beginning?"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 resize-none"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Goal State
                </label>
                <textarea
                  value={formData.arc?.goal_state || ''}
                  onChange={(e) => setFormData({
                    ...formData,
                    arc: { ...formData.arc!, goal_state: e.target.value }
                  })}
                  placeholder="Who will they become by the end?"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 resize-none"
                  rows={3}
                />
              </div>
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Key Transformations</label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={newTransformation}
                  onChange={(e) => setNewTransformation(e.target.value)}
                  placeholder="Major moment of change or growth"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTransformation())}
                />
                <button
                  type="button"
                  onClick={addTransformation}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
                >
                  <Plus className="h-5 w-5" />
                </button>
              </div>
              <div className="space-y-2">
                {formData.arc?.key_transformations?.map((transformation, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-white rounded-lg border border-purple-200"
                  >
                    <span className="text-sm text-gray-900">{transformation}</span>
                    <button
                      type="button"
                      onClick={() => removeTransformation(idx)}
                      className="text-purple-600 hover:text-purple-800"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </form>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <p className="text-sm text-gray-600">
            * Required fields
          </p>
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition"
              disabled={isSaving}
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={isSaving || !formData.name}
              className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isSaving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <span>Save Character</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
