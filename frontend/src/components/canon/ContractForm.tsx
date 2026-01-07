'use client'

import { useState } from 'react'
import { CanonContract } from '@/types/canon'
import api from '@/lib/api'
import Button from '@/components/Button'
import Input from '@/components/Input'
import Textarea from '@/components/Textarea'
import { X } from 'lucide-react'

interface ContractFormProps {
  projectId: number
  contract?: CanonContract | null
  onClose: () => void
}

export default function ContractForm({
  projectId,
  contract,
  onClose,
}: ContractFormProps) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: contract?.name || '',
    description: contract?.description || '',
    rule: contract?.rule || '',
    severity: contract?.severity || 'must',
    active: contract?.active !== undefined ? contract.active : true,
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const payload = {
        project_id: projectId,
        ...formData,
      }

      if (contract) {
        await api.put(`/api/contracts/contract/${contract.id}`, payload)
      } else {
        await api.post('/api/contracts/contract', payload)
      }

      onClose()
    } catch (error) {
      console.error('Failed to save contract:', error)
      alert('Failed to save contract. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">
          {contract ? 'Edit Contract' : 'New Canon Contract'}
        </h2>
        <Button variant="ghost" size="sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Name *"
          placeholder="Contract name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />

        <Textarea
          label="Description"
          placeholder="Brief description of what this contract enforces"
          value={formData.description}
          onChange={(e) =>
            setFormData({ ...formData, description: e.target.value })
          }
          rows={2}
        />

        <Textarea
          label="Rule *"
          placeholder="The specific rule that must be followed"
          value={formData.rule}
          onChange={(e) => setFormData({ ...formData, rule: e.target.value })}
          rows={3}
          required
        />

        <div>
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Severity *
          </label>
          <select
            value={formData.severity}
            onChange={(e) =>
              setFormData({
                ...formData,
                severity: e.target.value as 'must' | 'should' | 'prefer',
              })
            }
            className="mt-1 flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            required
          >
            <option value="must">Must (Blocker - generation fails if violated)</option>
            <option value="should">Should (Warning - flag but allow)</option>
            <option value="prefer">Prefer (Suggestion - gentle reminder)</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="active"
            checked={formData.active}
            onChange={(e) =>
              setFormData({ ...formData, active: e.target.checked })
            }
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <label
            htmlFor="active"
            className="text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Active (enforce this contract during generation)
          </label>
        </div>

        <div className="flex justify-end space-x-3">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? 'Saving...' : contract ? 'Update' : 'Create'}
          </Button>
        </div>
      </form>
    </div>
  )
}
