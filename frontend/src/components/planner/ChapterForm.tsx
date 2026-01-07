'use client'

import { useState } from 'react'
import api from '@/lib/api'
import Button from '@/components/Button'
import Input from '@/components/Input'
import Textarea from '@/components/Textarea'
import { X } from 'lucide-react'

interface ChapterFormProps {
  projectId: number
  nextChapterNumber: number
  onClose: () => void
}

export default function ChapterForm({
  projectId,
  nextChapterNumber,
  onClose,
}: ChapterFormProps) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    chapter_number: nextChapterNumber,
    title: '',
    summary: '',
    pov_character: '',
    location: '',
    goals: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const payload = {
        project_id: projectId,
        chapter_number: formData.chapter_number,
        title: formData.title || undefined,
        summary: formData.summary,
        pov_character: formData.pov_character || undefined,
        location: formData.location || undefined,
        goals: formData.goals.split('\n').filter((g) => g.trim()),
      }

      await api.post('/api/planner/chapter', payload)
      onClose()
    } catch (error) {
      console.error('Failed to create chapter:', error)
      alert('Failed to create chapter. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">New Chapter</h3>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Input
            type="number"
            label="Chapter Number *"
            value={formData.chapter_number}
            onChange={(e) =>
              setFormData({
                ...formData,
                chapter_number: parseInt(e.target.value),
              })
            }
            required
          />
          <Input
            label="Title (Optional)"
            placeholder="Chapter title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          />
        </div>

        <Textarea
          label="Summary *"
          placeholder="What happens in this chapter?"
          value={formData.summary}
          onChange={(e) => setFormData({ ...formData, summary: e.target.value })}
          rows={3}
          required
        />

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="POV Character"
            placeholder="Whose perspective?"
            value={formData.pov_character}
            onChange={(e) =>
              setFormData({ ...formData, pov_character: e.target.value })
            }
          />
          <Input
            label="Location"
            placeholder="Where does it take place?"
            value={formData.location}
            onChange={(e) =>
              setFormData({ ...formData, location: e.target.value })
            }
          />
        </div>

        <Textarea
          label="Goals"
          placeholder="Chapter goals (one per line)"
          value={formData.goals}
          onChange={(e) => setFormData({ ...formData, goals: e.target.value })}
          rows={2}
        />

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Chapter'}
          </Button>
        </div>
      </form>
    </div>
  )
}
