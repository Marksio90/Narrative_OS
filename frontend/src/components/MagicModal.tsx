'use client'

import { useState, useEffect } from 'react'
import { X, Plus, Trash2, Sparkles, Zap, Shield, Users, AlertCircle, Atom } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface MagicSystem {
  id?: number
  project_id: number
  name: string
  description: string
  rule_type?: string  // magic, physics, divine, curse, etc.
  laws: string[]  // Fundamental rules that ALWAYS apply
  costs: string[]  // What using this requires/costs
  limitations: string[]  // What it cannot do
  exceptions: string[]  // Rare cases where rules don't apply
  prohibitions: string[]  // What is strictly forbidden
  mechanics?: string  // How it works in practice
  manifestation: { [key: string]: any }  // How it appears, feels, looks
  tags?: string[]  // Optional tags for categorization
  claims?: { [key: string]: any }  // Canon claims
  unknowns?: string[]  // Things we don't know yet
}

interface MagicModalProps {
  magicSystem: MagicSystem | null
  onClose: () => void
  onSave: () => void
  accessToken: string
  projectId?: number
}

export default function MagicModal({
  magicSystem,
  onClose,
  onSave,
  accessToken,
  projectId = 1
}: MagicModalProps) {
  const [formData, setFormData] = useState<MagicSystem>({
    project_id: projectId,
    name: '',
    description: '',
    rule_type: 'magic',
    laws: [],
    costs: [],
    limitations: [],
    exceptions: [],
    prohibitions: [],
    mechanics: '',
    manifestation: {},
    tags: [],
    claims: {},
    unknowns: []
  })

  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Input states for adding new items to arrays
  const [newLaw, setNewLaw] = useState('')
  const [newCost, setNewCost] = useState('')
  const [newLimitation, setNewLimitation] = useState('')
  const [newException, setNewException] = useState('')
  const [newProhibition, setNewProhibition] = useState('')

  useEffect(() => {
    if (magicSystem) {
      setFormData({
        ...magicSystem,
        laws: magicSystem.laws || [],
        costs: magicSystem.costs || [],
        limitations: magicSystem.limitations || [],
        exceptions: magicSystem.exceptions || [],
        prohibitions: magicSystem.prohibitions || [],
        manifestation: magicSystem.manifestation || {},
        tags: magicSystem.tags || [],
        claims: magicSystem.claims || {},
        unknowns: magicSystem.unknowns || []
      })
    }
  }, [magicSystem])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    setError(null)

    try {
      const url = magicSystem
        ? `${API_URL}/api/canon/magic/${magicSystem.id}`
        : `${API_URL}/api/canon/magic`

      const method = magicSystem ? 'PUT' : 'POST'

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
        throw new Error(errorData.detail || 'Failed to save magic system')
      }

      onSave()
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsSaving(false)
    }
  }

  const addArrayItem = (field: 'laws' | 'costs' | 'limitations' | 'exceptions' | 'prohibitions', value: string, setter: (val: string) => void) => {
    if (!value.trim()) return
    const currentArray = formData[field] || []
    setFormData({
      ...formData,
      [field]: [...currentArray, value.trim()]
    })
    setter('')
  }

  const removeArrayItem = (field: 'laws' | 'costs' | 'limitations' | 'exceptions' | 'prohibitions', index: number) => {
    const currentArray = formData[field] || []
    setFormData({
      ...formData,
      [field]: currentArray.filter((_, i) => i !== index)
    })
  }

  const ruleTypes = [
    {
      value: 'magic',
      label: 'Magic',
      color: 'purple',
      icon: '✨',
      description: 'Arcane spells and mystical forces'
    },
    {
      value: 'physics',
      label: 'Physics',
      color: 'blue',
      icon: '⚛️',
      description: 'Natural laws and physical constraints'
    },
    {
      value: 'divine',
      label: 'Divine',
      color: 'yellow',
      icon: '☀️',
      description: 'Power from gods or cosmic forces'
    },
    {
      value: 'curse',
      label: 'Curse',
      color: 'red',
      icon: '💀',
      description: 'Afflictions and dark powers'
    },
    {
      value: 'technology',
      label: 'Technology',
      color: 'gray',
      icon: '🔧',
      description: 'Advanced tech or science-based systems'
    },
    {
      value: 'psychic',
      label: 'Psychic',
      color: 'indigo',
      icon: '🧠',
      description: 'Mental powers and telepathy'
    },
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full my-8">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {magicSystem ? 'Edit Magic System' : 'New Magic System'}
              </h2>
              <p className="text-sm text-gray-600">
                Define magic rules, costs, and limitations
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
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Basic Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-purple-600" />
              <span>Basic Information</span>
            </h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Magic System Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Elemental Bending, Rune Magic, Divine Power"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description *
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Brief overview of this magic system..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                rows={3}
                required
              />
            </div>
          </div>

          {/* Rule Type */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Atom className="h-5 w-5 text-indigo-600" />
              <span>Rule Type</span>
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {ruleTypes.map((type) => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, rule_type: type.value })}
                  className={`p-4 rounded-lg border-2 transition text-left ${
                    formData.rule_type === type.value
                      ? `border-${type.color}-500 bg-${type.color}-50`
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-2xl">{type.icon}</span>
                    <span className="text-sm font-bold text-gray-900">{type.label}</span>
                  </div>
                  <p className="text-xs text-gray-600">{type.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Power Source */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Zap className="h-5 w-5 text-yellow-600" />
              <span>Power Source</span>
            </h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Where does magic come from?
              </label>
              <input
                type="text"
                value={formData.power_source || ''}
                onChange={(e) => setFormData({ ...formData, power_source: e.target.value })}
                placeholder="e.g., Natural energy, Divine blessing, Ancient artifacts, User's life force"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Costs */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Shield className="h-5 w-5 text-red-600" />
              <span>Costs & Consequences</span>
            </h3>
            <p className="text-sm text-gray-600">
              What does using magic cost? (Energy, time, materials, sacrifice, etc.)
            </p>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newCost}
                onChange={(e) => setNewCost(e.target.value)}
                placeholder="e.g., Drains stamina, Requires rare components, Shortens lifespan"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addArrayItem('costs', newCost, setNewCost))}
              />
              <button
                type="button"
                onClick={() => addArrayItem('costs', newCost, setNewCost)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
            <div className="space-y-2">
              {formData.costs.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4 bg-gray-50 rounded-lg">
                  No costs defined yet
                </p>
              ) : (
                formData.costs.map((cost, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg group hover:bg-red-100 transition"
                  >
                    <span className="text-sm text-gray-900">{cost}</span>
                    <button
                      type="button"
                      onClick={() => removeArrayItem('costs', idx)}
                      className="opacity-0 group-hover:opacity-100 text-red-600 hover:text-red-800 transition"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Limitations */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-amber-600" />
              <span>Limitations & Restrictions</span>
            </h3>
            <p className="text-sm text-gray-600">
              What cannot be done with this magic? Hard limits.
            </p>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newLimitation}
                onChange={(e) => setNewLimitation(e.target.value)}
                placeholder="e.g., Cannot create life, Ineffective against iron, Cannot affect free will"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addArrayItem('limitations', newLimitation, setNewLimitation))}
              />
              <button
                type="button"
                onClick={() => addArrayItem('limitations', newLimitation, setNewLimitation)}
                className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
            <div className="space-y-2">
              {formData.limitations.map((limit, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-amber-50 border border-amber-200 rounded-lg group hover:bg-amber-100 transition"
                >
                  <span className="text-sm text-gray-900">{limit}</span>
                  <button
                    type="button"
                    onClick={() => removeArrayItem('limitations', idx)}
                    className="opacity-0 group-hover:opacity-100 text-amber-600 hover:text-amber-800 transition"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Rules */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-blue-600" />
              <span>Rules & Laws</span>
            </h3>
            <p className="text-sm text-gray-600">
              How does magic work? Fundamental laws and rules.
            </p>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newRule}
                onChange={(e) => setNewRule(e.target.value)}
                placeholder="e.g., Magic follows conservation of energy, Stronger emotions = stronger magic"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addArrayItem('rules', newRule, setNewRule))}
              />
              <button
                type="button"
                onClick={() => addArrayItem('rules', newRule, setNewRule)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
            <div className="space-y-2">
              {formData.rules.map((rule, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-blue-50 border border-blue-200 rounded-lg group hover:bg-blue-100 transition"
                >
                  <span className="text-sm text-gray-900">{rule}</span>
                  <button
                    type="button"
                    onClick={() => removeArrayItem('rules', idx)}
                    className="opacity-0 group-hover:opacity-100 text-blue-600 hover:text-blue-800 transition"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Practitioners */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Users className="h-5 w-5 text-green-600" />
              <span>Practitioners & Access</span>
            </h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Who can use this magic?
              </label>
              <textarea
                value={formData.practitioners || ''}
                onChange={(e) => setFormData({ ...formData, practitioners: e.target.value })}
                placeholder="Requirements, bloodlines, training needed, restrictions on who can learn..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
                rows={2}
              />
            </div>
          </div>

          {/* Manifestation */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-pink-600" />
              <span>Manifestation & Appearance</span>
            </h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                How does magic appear when used?
              </label>
              <textarea
                value={formData.manifestation || ''}
                onChange={(e) => setFormData({ ...formData, manifestation: e.target.value })}
                placeholder="Visual effects, sounds, sensations, signs that magic is being used..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent resize-none"
                rows={2}
              />
            </div>
          </div>

          {/* Cultural Impact */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Users className="h-5 w-5 text-purple-600" />
              <span>Cultural Impact</span>
            </h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                How does society view and use magic?
              </label>
              <textarea
                value={formData.cultural_impact || ''}
                onChange={(e) => setFormData({ ...formData, cultural_impact: e.target.value })}
                placeholder="Social attitudes, legal status, role in daily life, education systems..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                rows={2}
              />
            </div>
          </div>

          {/* Summary Stats */}
          {(formData.costs.length > 0 || formData.limitations.length > 0 || formData.rules.length > 0) && (
            <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-red-600">{formData.costs.length}</p>
                  <p className="text-sm text-gray-600">Costs</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-amber-600">{formData.limitations.length}</p>
                  <p className="text-sm text-gray-600">Limitations</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-blue-600">{formData.rules.length}</p>
                  <p className="text-sm text-gray-600">Rules</p>
                </div>
              </div>
            </div>
          )}
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
              disabled={isSaving || !formData.name || !formData.description}
              className="px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isSaving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <span>Save Magic System</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
