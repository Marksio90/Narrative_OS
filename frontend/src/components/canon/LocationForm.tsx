'use client'

import { useState } from 'react'
import { Location } from '@/types/canon'
import api from '@/lib/api'
import Button from '@/components/Button'
import Input from '@/components/Input'
import Textarea from '@/components/Textarea'
import { X } from 'lucide-react'

interface LocationFormProps {
  projectId: number
  location?: Location | null
  onClose: () => void
}

export default function LocationForm({
  projectId,
  location,
  onClose,
}: LocationFormProps) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: location?.name || '',
    description: location?.description || '',
    atmosphere: location?.atmosphere || '',
    accessibility: location?.accessibility?.join('\n') || '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const payload = {
        project_id: projectId,
        name: formData.name,
        description: formData.description,
        atmosphere: formData.atmosphere,
        accessibility: formData.accessibility
          .split('\n')
          .filter((a) => a.trim()),
        geography: {},
        claims: {},
        unknowns: [],
      }

      if (location) {
        await api.put(`/api/canon/location/${location.id}`, payload)
      } else {
        await api.post('/api/canon/location', payload)
      }

      onClose()
    } catch (error) {
      console.error('Failed to save location:', error)
      alert('Failed to save location. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">
          {location ? 'Edit Location' : 'New Location'}
        </h2>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Name *"
          placeholder="Location name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />

        <Textarea
          label="Description"
          placeholder="Brief description of the location"
          value={formData.description}
          onChange={(e) =>
            setFormData({ ...formData, description: e.target.value })
          }
          rows={3}
        />

        <Textarea
          label="Atmosphere"
          placeholder="The mood and feeling of this place"
          value={formData.atmosphere}
          onChange={(e) =>
            setFormData({ ...formData, atmosphere: e.target.value })
          }
          rows={2}
        />

        <Textarea
          label="Accessibility"
          placeholder="How to reach this location (one method per line)"
          value={formData.accessibility}
          onChange={(e) =>
            setFormData({ ...formData, accessibility: e.target.value })
          }
          rows={3}
        />

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? 'Saving...' : location ? 'Update' : 'Create'}
          </Button>
        </div>
      </form>
    </div>
  )
}
