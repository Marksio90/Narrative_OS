'use client'

import { useState, useEffect } from 'react'
import { X, Plus, Trash2, MapPin, Mountain, Cloud, Users, ShieldAlert, Sparkles } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Location {
  id?: number
  project_id: number
  name: string
  description: string
  geography?: string
  climate?: string
  culture?: string
  social_rules?: string[]
  restrictions?: string[]
  atmosphere?: string
}

interface LocationModalProps {
  location: Location | null
  onClose: () => void
  onSave: () => void
  accessToken: string
  projectId?: number
}

export default function LocationModal({
  location,
  onClose,
  onSave,
  accessToken,
  projectId = 1
}: LocationModalProps) {
  const [formData, setFormData] = useState<Location>({
    project_id: projectId,
    name: '',
    description: '',
    geography: '',
    climate: '',
    culture: '',
    social_rules: [],
    restrictions: [],
    atmosphere: ''
  })

  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Input states for adding new items to arrays
  const [newRule, setNewRule] = useState('')
  const [newRestriction, setNewRestriction] = useState('')

  useEffect(() => {
    if (location) {
      setFormData({
        ...location,
        social_rules: location.social_rules || [],
        restrictions: location.restrictions || []
      })
    }
  }, [location])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    setError(null)

    try {
      const url = location
        ? `${API_URL}/api/canon/location/${location.id}`
        : `${API_URL}/api/canon/location`

      const method = location ? 'PUT' : 'POST'

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
        throw new Error(errorData.detail || 'Failed to save location')
      }

      onSave()
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsSaving(false)
    }
  }

  const addArrayItem = (field: 'social_rules' | 'restrictions', value: string, setter: (val: string) => void) => {
    if (!value.trim()) return
    const currentArray = formData[field] || []
    setFormData({
      ...formData,
      [field]: [...currentArray, value.trim()]
    })
    setter('')
  }

  const removeArrayItem = (field: 'social_rules' | 'restrictions', index: number) => {
    const currentArray = formData[field] || []
    setFormData({
      ...formData,
      [field]: currentArray.filter((_, i) => i !== index)
    })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full my-8">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
              <MapPin className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {location ? 'Edit Location' : 'New Location'}
              </h2>
              <p className="text-sm text-gray-600">
                Define a place in your story world
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
              <MapPin className="h-5 w-5 text-emerald-600" />
              <span>Basic Information</span>
            </h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., The Whispering Woods, King's Landing, Baker Street"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
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
                placeholder="Brief overview of this location..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent resize-none"
                rows={3}
                required
              />
            </div>
          </div>

          {/* Geography */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Mountain className="h-5 w-5 text-blue-600" />
              <span>Geography & Layout</span>
            </h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Geography
              </label>
              <textarea
                value={formData.geography || ''}
                onChange={(e) => setFormData({ ...formData, geography: e.target.value })}
                placeholder="Physical features: mountains, rivers, forests, urban layout, etc."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={3}
              />
            </div>
          </div>

          {/* Climate & Atmosphere */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Cloud className="h-5 w-5 text-sky-600" />
              <span>Climate & Atmosphere</span>
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Climate
                </label>
                <input
                  type="text"
                  value={formData.climate || ''}
                  onChange={(e) => setFormData({ ...formData, climate: e.target.value })}
                  placeholder="e.g., Temperate, Arctic, Tropical"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Atmosphere
                </label>
                <input
                  type="text"
                  value={formData.atmosphere || ''}
                  onChange={(e) => setFormData({ ...formData, atmosphere: e.target.value })}
                  placeholder="e.g., Eerie, Bustling, Serene"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Culture */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Users className="h-5 w-5 text-purple-600" />
              <span>Culture & Society</span>
            </h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Culture
              </label>
              <textarea
                value={formData.culture || ''}
                onChange={(e) => setFormData({ ...formData, culture: e.target.value })}
                placeholder="Cultural aspects: traditions, social norms, way of life..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                rows={3}
              />
            </div>
          </div>

          {/* Social Rules */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <ShieldAlert className="h-5 w-5 text-amber-600" />
              <span>Social Rules & Customs</span>
            </h3>
            <p className="text-sm text-gray-600">
              Behavioral expectations, customs, and social norms
            </p>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newRule}
                onChange={(e) => setNewRule(e.target.value)}
                placeholder="e.g., Remove shoes indoors, Bow to elders, No eye contact with royalty"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addArrayItem('social_rules', newRule, setNewRule))}
              />
              <button
                type="button"
                onClick={() => addArrayItem('social_rules', newRule, setNewRule)}
                className="px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
            <div className="space-y-2">
              {formData.social_rules?.map((rule, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-amber-50 border border-amber-200 rounded-lg"
                >
                  <span className="text-sm text-gray-900">{rule}</span>
                  <button
                    type="button"
                    onClick={() => removeArrayItem('social_rules', idx)}
                    className="text-amber-600 hover:text-amber-800"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Restrictions */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-red-600" />
              <span>Restrictions & Limitations</span>
            </h3>
            <p className="text-sm text-gray-600">
              What cannot be done here, forbidden areas, access limitations
            </p>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newRestriction}
                onChange={(e) => setNewRestriction(e.target.value)}
                placeholder="e.g., Outsiders forbidden after dark, Magic banned, Weapons not allowed"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addArrayItem('restrictions', newRestriction, setNewRestriction))}
              />
              <button
                type="button"
                onClick={() => addArrayItem('restrictions', newRestriction, setNewRestriction)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
            <div className="space-y-2">
              {formData.restrictions?.map((restriction, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg"
                >
                  <span className="text-sm text-gray-900">{restriction}</span>
                  <button
                    type="button"
                    onClick={() => removeArrayItem('restrictions', idx)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
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
              disabled={isSaving || !formData.name || !formData.description}
              className="px-6 py-2 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg hover:from-emerald-700 hover:to-teal-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isSaving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <span>Save Location</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
