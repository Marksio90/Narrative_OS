'use client'

import { useState } from 'react'
import { Character } from '@/types/canon'
import api from '@/lib/api'
import Button from '@/components/Button'
import Input from '@/components/Input'
import Textarea from '@/components/Textarea'
import { X } from 'lucide-react'

interface CharacterFormProps {
  projectId: number
  character?: Character | null
  onClose: () => void
}

export default function CharacterForm({
  projectId,
  character,
  onClose,
}: CharacterFormProps) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: character?.name || '',
    description: character?.description || '',
    goals: character?.goals?.join('\n') || '',
    behavioral_limits: character?.behavioral_limits?.join('\n') || '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const payload = {
        project_id: projectId,
        name: formData.name,
        description: formData.description,
        goals: formData.goals.split('\n').filter((g) => g.trim()),
        behavioral_limits: formData.behavioral_limits
          .split('\n')
          .filter((l) => l.trim()),
        voice_profile: {},
        claims: {},
        unknowns: [],
      }

      if (character) {
        await api.put(`/api/canon/character/${character.id}`, payload)
      } else {
        await api.post('/api/canon/character', payload)
      }

      onClose()
    } catch (error) {
      console.error('Failed to save character:', error)
      alert('Failed to save character. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">
          {character ? 'Edit Character' : 'New Character'}
        </h2>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Name *"
          placeholder="Character name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />

        <Textarea
          label="Description"
          placeholder="Brief description of the character"
          value={formData.description}
          onChange={(e) =>
            setFormData({ ...formData, description: e.target.value })
          }
          rows={3}
        />

        <Textarea
          label="Goals"
          placeholder="One goal per line"
          value={formData.goals}
          onChange={(e) => setFormData({ ...formData, goals: e.target.value })}
          rows={4}
        />

        <Textarea
          label="Behavioral Limits"
          placeholder="What this character would never do (one per line)"
          value={formData.behavioral_limits}
          onChange={(e) =>
            setFormData({ ...formData, behavioral_limits: e.target.value })
          }
          rows={4}
        />

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? 'Saving...' : character ? 'Update' : 'Create'}
          </Button>
        </div>
      </form>
    </div>
  )
}
