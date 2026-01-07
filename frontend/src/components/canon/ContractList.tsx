'use client'

import { useState, useEffect } from 'react'
import { CanonContract } from '@/types/canon'
import api from '@/lib/api'
import Button from '@/components/Button'
import { Plus, Edit2, Trash2, AlertTriangle, AlertCircle, Info } from 'lucide-react'
import { formatDateTime } from '@/lib/utils'
import ContractForm from './ContractForm'

interface ContractListProps {
  projectId: number
}

export default function ContractList({ projectId }: ContractListProps) {
  const [contracts, setContracts] = useState<CanonContract[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingContract, setEditingContract] = useState<CanonContract | null>(null)

  const fetchContracts = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/api/contracts/contract`, {
        params: { project_id: projectId },
      })
      setContracts(response.data)
    } catch (error) {
      console.error('Failed to fetch contracts:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchContracts()
  }, [projectId])

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this contract?')) return

    try {
      await api.delete(`/api/contracts/contract/${id}`)
      fetchContracts()
    } catch (error) {
      console.error('Failed to delete contract:', error)
    }
  }

  const handleEdit = (contract: CanonContract) => {
    setEditingContract(contract)
    setShowForm(true)
  }

  const handleFormClose = () => {
    setShowForm(false)
    setEditingContract(null)
    fetchContracts()
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'must':
        return <AlertTriangle className="h-5 w-5 text-red-600" />
      case 'should':
        return <AlertCircle className="h-5 w-5 text-orange-600" />
      case 'prefer':
        return <Info className="h-5 w-5 text-blue-600" />
      default:
        return null
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'must':
        return 'border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950'
      case 'should':
        return 'border-orange-300 bg-orange-50 dark:border-orange-800 dark:bg-orange-950'
      case 'prefer':
        return 'border-blue-300 bg-blue-50 dark:border-blue-800 dark:bg-blue-950'
      default:
        return ''
    }
  }

  if (showForm) {
    return (
      <ContractForm
        projectId={projectId}
        contract={editingContract}
        onClose={handleFormClose}
      />
    )
  }

  if (loading) {
    return <div className="text-center py-12">Loading contracts...</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold">Canon Contracts ({contracts.length})</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Hard rules that AI generation must respect
          </p>
        </div>
        <Button onClick={() => setShowForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Contract
        </Button>
      </div>

      {contracts.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No contracts yet. Create your first contract to enforce consistency rules.
        </div>
      ) : (
        <div className="grid gap-4">
          {contracts.map((contract) => (
            <div
              key={contract.id}
              className={`border rounded-lg p-4 ${getSeverityColor(contract.severity)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    {getSeverityIcon(contract.severity)}
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {contract.name}
                    </h3>
                    <span className="text-xs px-2 py-1 rounded-full bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 uppercase font-medium">
                      {contract.severity}
                    </span>
                    {!contract.active && (
                      <span className="text-xs px-2 py-1 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400">
                        Inactive
                      </span>
                    )}
                  </div>
                  {contract.description && (
                    <p className="text-gray-600 dark:text-gray-400 mt-2">
                      {contract.description}
                    </p>
                  )}
                  <div className="mt-3 p-3 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                    <p className="text-sm font-mono text-gray-800 dark:text-gray-200">
                      {contract.rule}
                    </p>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Updated {formatDateTime(contract.updated_at)}
                  </p>
                </div>
                <div className="flex space-x-2 ml-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEdit(contract)}
                  >
                    <Edit2 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(contract.id)}
                  >
                    <Trash2 className="h-4 w-4 text-red-600" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
