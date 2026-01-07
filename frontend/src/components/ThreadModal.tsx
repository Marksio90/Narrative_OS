'use client'

import { useState, useEffect } from 'react'
import { X, Plus, Trash2, Sparkles, TrendingUp, Check, AlertCircle } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface PlotThread {
  id?: number
  project_id: number
  name: string
  description: string
  thread_type: 'main' | 'subplot' | 'character_arc' | 'mystery' | 'romance' | 'theme'
  status: 'active' | 'resolved' | 'abandoned'
  start_chapter?: number
  end_chapter?: number
  key_moments: string[]
  related_characters: number[]
}

interface ThreadModalProps {
  thread: PlotThread | null
  onClose: () => void
  onSave: () => void
  accessToken: string
  projectId?: number
}

export default function ThreadModal({
  thread,
  onClose,
  onSave,
  accessToken,
  projectId = 1
}: ThreadModalProps) {
  const [formData, setFormData] = useState<PlotThread>({
    project_id: projectId,
    name: '',
    description: '',
    thread_type: 'subplot',
    status: 'active',
    start_chapter: undefined,
    end_chapter: undefined,
    key_moments: [],
    related_characters: []
  })

  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Input state for adding new key moments
  const [newMoment, setNewMoment] = useState('')

  useEffect(() => {
    if (thread) {
      setFormData({
        ...thread,
        key_moments: thread.key_moments || [],
        related_characters: thread.related_characters || []
      })
    }
  }, [thread])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSaving(true)
    setError(null)

    try {
      const url = thread
        ? `${API_URL}/api/canon/thread/${thread.id}`
        : `${API_URL}/api/canon/thread`

      const method = thread ? 'PUT' : 'POST'

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
        throw new Error(errorData.detail || 'Failed to save plot thread')
      }

      onSave()
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsSaving(false)
    }
  }

  const addMoment = () => {
    if (!newMoment.trim()) return
    setFormData({
      ...formData,
      key_moments: [...formData.key_moments, newMoment.trim()]
    })
    setNewMoment('')
  }

  const removeMoment = (index: number) => {
    setFormData({
      ...formData,
      key_moments: formData.key_moments.filter((_, i) => i !== index)
    })
  }

  const threadTypes = [
    { value: 'main', label: 'Main Plot', color: 'purple', icon: '⭐' },
    { value: 'subplot', label: 'Subplot', color: 'blue', icon: '📖' },
    { value: 'character_arc', label: 'Character Arc', color: 'green', icon: '🎭' },
    { value: 'mystery', label: 'Mystery', color: 'amber', icon: '🔍' },
    { value: 'romance', label: 'Romance', color: 'pink', icon: '💕' },
    { value: 'theme', label: 'Theme', color: 'violet', icon: '💡' },
  ]

  const statusOptions = [
    { value: 'active', label: 'Active', color: 'green', icon: '🟢' },
    { value: 'resolved', label: 'Resolved', color: 'gray', icon: '✅' },
    { value: 'abandoned', label: 'Abandoned', color: 'red', icon: '❌' },
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full my-8">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                {thread ? 'Edit Plot Thread' : 'New Plot Thread'}
              </h2>
              <p className="text-sm text-gray-600">
                Track story arcs, mysteries, and narrative threads
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
                Thread Name *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., The Quest for the Crystal, Mystery of the Missing Heir"
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
                placeholder="Brief summary of this narrative thread..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                rows={3}
                required
              />
            </div>
          </div>

          {/* Type and Status */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-indigo-600" />
              <span>Type & Status</span>
            </h3>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Thread Type
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {threadTypes.map((type) => (
                  <button
                    key={type.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, thread_type: type.value as any })}
                    className={`p-3 rounded-lg border-2 transition text-left ${
                      formData.thread_type === type.value
                        ? `border-${type.color}-500 bg-${type.color}-50`
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <span className="text-xl">{type.icon}</span>
                      <span className="text-sm font-medium text-gray-900">{type.label}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <div className="grid grid-cols-3 gap-3">
                {statusOptions.map((status) => (
                  <button
                    key={status.value}
                    type="button"
                    onClick={() => setFormData({ ...formData, status: status.value as any })}
                    className={`p-3 rounded-lg border-2 transition ${
                      formData.status === status.value
                        ? `border-${status.color}-500 bg-${status.color}-50`
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center justify-center space-x-2">
                      <span>{status.icon}</span>
                      <span className="text-sm font-medium text-gray-900">{status.label}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Chapter Range */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Check className="h-5 w-5 text-green-600" />
              <span>Chapter Range</span>
            </h3>
            <p className="text-sm text-gray-600">
              When does this thread start and end?
            </p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Chapter
                </label>
                <input
                  type="number"
                  value={formData.start_chapter || ''}
                  onChange={(e) => setFormData({ ...formData, start_chapter: e.target.value ? parseInt(e.target.value) : undefined })}
                  placeholder="e.g., 1"
                  min="1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Chapter
                </label>
                <input
                  type="number"
                  value={formData.end_chapter || ''}
                  onChange={(e) => setFormData({ ...formData, end_chapter: e.target.value ? parseInt(e.target.value) : undefined })}
                  placeholder="e.g., 25"
                  min="1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>
            {formData.start_chapter && formData.end_chapter && formData.end_chapter < formData.start_chapter && (
              <p className="text-sm text-red-600 flex items-center space-x-1">
                <AlertCircle className="h-4 w-4" />
                <span>End chapter should be after start chapter</span>
              </p>
            )}
          </div>

          {/* Key Moments */}
          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-yellow-600" />
              <span>Key Moments</span>
            </h3>
            <p className="text-sm text-gray-600">
              Important beats, revelations, or turning points in this thread
            </p>
            <div className="flex space-x-2">
              <input
                type="text"
                value={newMoment}
                onChange={(e) => setNewMoment(e.target.value)}
                placeholder="e.g., Hero learns the truth about their past"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addMoment())}
              />
              <button
                type="button"
                onClick={addMoment}
                className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition"
              >
                <Plus className="h-5 w-5" />
              </button>
            </div>
            <div className="space-y-2">
              {formData.key_moments.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4 bg-gray-50 rounded-lg">
                  No key moments added yet
                </p>
              ) : (
                formData.key_moments.map((moment, idx) => (
                  <div
                    key={idx}
                    className="flex items-start space-x-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg group hover:bg-yellow-100 transition"
                  >
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-yellow-500 text-white flex items-center justify-center text-xs font-bold">
                      {idx + 1}
                    </div>
                    <span className="flex-1 text-sm text-gray-900">{moment}</span>
                    <button
                      type="button"
                      onClick={() => removeMoment(idx)}
                      className="opacity-0 group-hover:opacity-100 text-yellow-600 hover:text-yellow-800 transition"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Summary Stats */}
          {formData.key_moments.length > 0 && (
            <div className="p-4 bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg">
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-purple-600">{formData.key_moments.length}</p>
                  <p className="text-sm text-gray-600">Key Moments</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-indigo-600">
                    {formData.start_chapter && formData.end_chapter
                      ? formData.end_chapter - formData.start_chapter + 1
                      : '?'}
                  </p>
                  <p className="text-sm text-gray-600">Chapters</p>
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
              className="px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isSaving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <span>Save Plot Thread</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
