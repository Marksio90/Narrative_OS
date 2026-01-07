'use client'

import { useState } from 'react'
import { BookArc } from '@/types/planner'
import api from '@/lib/api'
import Button from '@/components/Button'
import Input from '@/components/Input'
import Textarea from '@/components/Textarea'
import { X } from 'lucide-react'

interface BookArcFormProps {
  projectId: number
  bookArc?: BookArc
  onClose: () => void
}

export default function BookArcForm({
  projectId,
  bookArc,
  onClose,
}: BookArcFormProps) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    premise: bookArc?.premise || '',
    protagonist_goal: bookArc?.protagonist_goal || '',
    central_conflict: bookArc?.central_conflict || '',
    stakes: bookArc?.stakes || '',
    act1_end: bookArc?.act1_end || 6,
    midpoint: bookArc?.midpoint || 12,
    act2_end: bookArc?.act2_end || 18,
    climax: bookArc?.climax || 23,
    resolution: bookArc?.resolution || '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const payload = {
        project_id: projectId,
        ...formData,
      }

      if (bookArc) {
        await api.put(`/api/planner/book-arc/${bookArc.id}`, payload)
      } else {
        await api.post('/api/planner/book-arc', payload)
      }

      onClose()
    } catch (error) {
      console.error('Failed to save book arc:', error)
      alert('Failed to save book arc. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">
          {bookArc ? 'Edit Book Arc' : 'Create Book Arc'}
        </h2>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Textarea
          label="Premise *"
          placeholder="What is your story about in one sentence?"
          value={formData.premise}
          onChange={(e) => setFormData({ ...formData, premise: e.target.value })}
          rows={2}
          required
        />

        <Textarea
          label="Protagonist Goal *"
          placeholder="What does the protagonist want?"
          value={formData.protagonist_goal}
          onChange={(e) =>
            setFormData({ ...formData, protagonist_goal: e.target.value })
          }
          rows={2}
          required
        />

        <Textarea
          label="Central Conflict *"
          placeholder="What prevents the protagonist from achieving their goal?"
          value={formData.central_conflict}
          onChange={(e) =>
            setFormData({ ...formData, central_conflict: e.target.value })
          }
          rows={2}
          required
        />

        <Textarea
          label="Stakes *"
          placeholder="What happens if the protagonist fails?"
          value={formData.stakes}
          onChange={(e) => setFormData({ ...formData, stakes: e.target.value })}
          rows={2}
          required
        />

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Input
            type="number"
            label="Act 1 End (Chapter) *"
            value={formData.act1_end}
            onChange={(e) =>
              setFormData({ ...formData, act1_end: parseInt(e.target.value) })
            }
            required
          />
          <Input
            type="number"
            label="Midpoint (Chapter) *"
            value={formData.midpoint}
            onChange={(e) =>
              setFormData({ ...formData, midpoint: parseInt(e.target.value) })
            }
            required
          />
          <Input
            type="number"
            label="Act 2 End (Chapter) *"
            value={formData.act2_end}
            onChange={(e) =>
              setFormData({ ...formData, act2_end: parseInt(e.target.value) })
            }
            required
          />
          <Input
            type="number"
            label="Climax (Chapter) *"
            value={formData.climax}
            onChange={(e) =>
              setFormData({ ...formData, climax: parseInt(e.target.value) })
            }
            required
          />
        </div>

        <Textarea
          label="Resolution *"
          placeholder="How does the story end?"
          value={formData.resolution}
          onChange={(e) =>
            setFormData({ ...formData, resolution: e.target.value })
          }
          rows={2}
          required
        />

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? 'Saving...' : bookArc ? 'Update' : 'Create'}
          </Button>
        </div>
      </form>
    </div>
  )
}
