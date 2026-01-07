'use client'

import { useState, useEffect } from 'react'
import { X, Plus, Trash2, Clock, MapPin, Users, Zap, AlertCircle, Calendar } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface TimelineEvent {
  id?: number
  project_id: number
  name: string
  description: string
  event_type: 'plot' | 'backstory' | 'world' | 'character'
  date_in_story?: string  // e.g., "1850", "Year 3 of the War", "Spring"
  chapter_number?: number
  location?: string
  participants: string[]  // Character names involved
  consequences: string[]  // What resulted from this event
  related_events?: number[]  // IDs of causally connected events
}

interface TimelineModalProps {
  event: TimelineEvent | null
  onClose: () => void
  onSave: () => void
  accessToken: string
  projectId?: number
}

export default function TimelineModal({
  event,
  onClose,
  onSave,
  accessToken,
  projectId = 1
}: TimelineModalProps) {
  const [formData, setFormData] = useState<TimelineEvent>({
    project_id: projectId,
    name: '',
    description: '',
    event_type: 'plot',
    date_in_story: '',
    chapter_number: undefined,
    location: '',
    participants: [],
    consequences: [],
    related_events: []
  })

  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Input states for adding new items to arrays
  const [newParticipant, setNewParticipant] = useState('')
  const [newConsequence, setNewConsequence] = useState('')

  useEffect(() => {
    if (event) {
      setFormData({
        ...event,
        participants: event.participants || [],
        consequences: event.consequences || [],
        related_events: event.related_events || []
      })
    }
  }, [event])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    setError(null)

    try {
      const url = event
        ? `${API_URL}/api/canon/event/${event.id}`
        : `${API_URL}/api/canon/event`

      const method = event ? 'PUT' : 'POST'

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
        throw new Error(errorData.detail || 'Failed to save timeline event')
      }

      onSave()
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsSaving(false)
    }
  }

  const addArrayItem = (field: 'participants' | 'consequences', value: string, setter: (val: string) => void) => {
    if (!value.trim()) return
    const currentArray = formData[field] || []
    setFormData({
      ...formData,
      [field]: [...currentArray, value.trim()]
    })
    setter('')
  }

  const removeArrayItem = (field: 'participants' | 'consequences', index: number) => {
    const currentArray = formData[field] || []
    setFormData({
      ...formData,
      [field]: currentArray.filter((_, i) => i !== index)
    })
  }

  const eventTypes = [
    {
      value: 'plot',
      label: 'Wydarzenie Fabularne',
      color: 'purple',
      icon: '📖',
      description: 'Główne wydarzenie fabularne'
    },
    {
      value: 'backstory',
      label: 'Przeszłość',
      color: 'gray',
      icon: '⏪',
      description: 'Wydarzenie z przeszłości'
    },
    {
      value: 'world',
      label: 'Wydarzenie Światowe',
      color: 'blue',
      icon: '🌍',
      description: 'Historyczne/tworzenie świata'
    },
    {
      value: 'character',
      label: 'Moment Postaci',
      color: 'green',
      icon: '👤',
      description: 'Osobiste wydarzenie postaci'
    },
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full my-8">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-cyan-600 flex items-center justify-center">
              <Clock className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {event ? 'Edytuj Wydarzenie na Osi Czasu' : 'Nowe Wydarzenie na Osi Czasu'}
              </h2>
              <p className="text-sm text-gray-600">
                Śledź chronologiczne wydarzenia w swojej historii
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
              <Calendar className="h-5 w-5 text-indigo-600" />
              <span>Podstawowe Informacje</span>
            </h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nazwa Wydarzenia *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="np. Bitwa o Winterfell, Przebudzenie Sary, Wielki Kataklizm"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Opis *
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Co się dzieje w tym wydarzeniu..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                rows={3}
                required
              />
            </div>
          </div>

          {/* Event Type */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Zap className="h-5 w-5 text-amber-600" />
              <span>Typ Wydarzenia</span>
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {eventTypes.map((type) => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, event_type: type.value as any })}
                  className={`p-3 rounded-lg border-2 transition text-left ${
                    formData.event_type === type.value
                      ? `border-${type.color}-500 bg-${type.color}-50`
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex flex-col items-center text-center space-y-1">
                    <span className="text-2xl">{type.icon}</span>
                    <span className="text-xs font-bold text-gray-900">{type.label}</span>
                    <span className="text-xs text-gray-600">{type.description}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Timing */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Clock className="h-5 w-5 text-blue-600" />
              <span>Kiedy</span>
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Data/Czas w Historii
                </label>
                <input
                  type="text"
                  value={formData.date_in_story || ''}
                  onChange={(e) => setFormData({ ...formData, date_in_story: e.target.value })}
                  placeholder="np. Rok 1850, Wiosna, Dzień 3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Numer Rozdziału
                </label>
                <input
                  type="number"
                  value={formData.chapter_number || ''}
                  onChange={(e) => setFormData({ ...formData, chapter_number: e.target.value ? parseInt(e.target.value) : undefined })}
                  placeholder="np. 15"
                  min="1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Location */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <MapPin className="h-5 w-5 text-green-600" />
              <span>Gdzie</span>
            </h3>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Lokalizacja
              </label>
              <input
                type="text"
                value={formData.location || ''}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                placeholder="np. Królewska Przystań, Mroczny Las, Mieszkanie Sary"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Participants */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Users className="h-5 w-5 text-purple-600" />
              <span>Kto Bierze Udział</span>
            </h3>
            <p className="text-sm text-gray-600">
              Postacie biorące udział w tym wydarzeniu
            </p>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newParticipant}
                onChange={(e) => setNewParticipant(e.target.value)}
                placeholder="np. Jon Snow, Sara Chen"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addArrayItem('participants', newParticipant, setNewParticipant))}
              />
              <button
                type="button"
                onClick={() => addArrayItem('participants', newParticipant, setNewParticipant)}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
            <div className="space-y-2">
              {formData.participants.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4 bg-gray-50 rounded-lg">
                  Nie dodano jeszcze uczestników
                </p>
              ) : (
                formData.participants.map((participant, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-purple-50 border border-purple-200 rounded-lg group hover:bg-purple-100 transition"
                  >
                    <span className="text-sm text-gray-900">{participant}</span>
                    <button
                      type="button"
                      onClick={() => removeArrayItem('participants', idx)}
                      className="opacity-0 group-hover:opacity-100 text-purple-600 hover:text-purple-800 transition"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Consequences */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Zap className="h-5 w-5 text-orange-600" />
              <span>Konsekwencje i Rezultaty</span>
            </h3>
            <p className="text-sm text-gray-600">
              Co wynikło z tego wydarzenia? Jak to zmieniło sytuację?
            </p>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newConsequence}
                onChange={(e) => setNewConsequence(e.target.value)}
                placeholder="np. Królestwo popadło w chaos, Sara odkryła swoje moce"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addArrayItem('consequences', newConsequence, setNewConsequence))}
              />
              <button
                type="button"
                onClick={() => addArrayItem('consequences', newConsequence, setNewConsequence)}
                className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
            <div className="space-y-2">
              {formData.consequences.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4 bg-gray-50 rounded-lg">
                  Nie dodano jeszcze konsekwencji
                </p>
              ) : (
                formData.consequences.map((consequence, idx) => (
                  <div
                    key={idx}
                    className="flex items-start space-x-3 p-3 bg-orange-50 border border-orange-200 rounded-lg group hover:bg-orange-100 transition"
                  >
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-orange-500 text-white flex items-center justify-center text-xs font-bold mt-0.5">
                      {idx + 1}
                    </div>
                    <span className="flex-1 text-sm text-gray-900">{consequence}</span>
                    <button
                      type="button"
                      onClick={() => removeArrayItem('consequences', idx)}
                      className="opacity-0 group-hover:opacity-100 text-orange-600 hover:text-orange-800 transition flex-shrink-0"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Summary Stats */}
          {(formData.participants.length > 0 || formData.consequences.length > 0) && (
            <div className="p-4 bg-gradient-to-br from-indigo-50 to-cyan-50 rounded-lg">
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-purple-600">{formData.participants.length}</p>
                  <p className="text-sm text-gray-600">Uczestnicy</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-orange-600">{formData.consequences.length}</p>
                  <p className="text-sm text-gray-600">Konsekwencje</p>
                </div>
              </div>
            </div>
          )}
        </form>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <p className="text-sm text-gray-600">
            * Pola wymagane
          </p>
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition"
              disabled={isSaving}
            >
              Anuluj
            </button>
            <button
              onClick={handleSubmit}
              disabled={isSaving || !formData.name || !formData.description}
              className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-cyan-600 text-white rounded-lg hover:from-indigo-700 hover:to-cyan-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isSaving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Zapisywanie...</span>
                </>
              ) : (
                <span>Zapisz Wydarzenie</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
