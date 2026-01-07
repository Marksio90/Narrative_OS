'use client'

import { useState, useEffect } from 'react'
import { Location } from '@/types/canon'
import api from '@/lib/api'
import Button from '@/components/Button'
import { Plus, Edit2, Trash2 } from 'lucide-react'
import { formatDateTime } from '@/lib/utils'
import LocationForm from './LocationForm'

interface LocationListProps {
  projectId: number
}

export default function LocationList({ projectId }: LocationListProps) {
  const [locations, setLocations] = useState<Location[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingLocation, setEditingLocation] = useState<Location | null>(null)

  const fetchLocations = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/api/canon/location`, {
        params: { project_id: projectId },
      })
      setLocations(response.data)
    } catch (error) {
      console.error('Failed to fetch locations:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLocations()
  }, [projectId])

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this location?')) return

    try {
      await api.delete(`/api/canon/location/${id}`)
      fetchLocations()
    } catch (error) {
      console.error('Failed to delete location:', error)
    }
  }

  const handleEdit = (location: Location) => {
    setEditingLocation(location)
    setShowForm(true)
  }

  const handleFormClose = () => {
    setShowForm(false)
    setEditingLocation(null)
    fetchLocations()
  }

  if (showForm) {
    return (
      <LocationForm
        projectId={projectId}
        location={editingLocation}
        onClose={handleFormClose}
      />
    )
  }

  if (loading) {
    return <div className="text-center py-12">Loading locations...</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Locations ({locations.length})</h2>
        <Button onClick={() => setShowForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Location
        </Button>
      </div>

      {locations.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No locations yet. Create your first location to get started.
        </div>
      ) : (
        <div className="grid gap-4">
          {locations.map((location) => (
            <div
              key={location.id}
              className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-blue-300 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {location.name}
                  </h3>
                  {location.description && (
                    <p className="text-gray-600 dark:text-gray-400 mt-1">
                      {location.description}
                    </p>
                  )}
                  {location.atmosphere && (
                    <div className="mt-2">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Atmosphere:
                      </span>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {location.atmosphere}
                      </p>
                    </div>
                  )}
                  <p className="text-xs text-gray-500 mt-2">
                    Updated {formatDateTime(location.updated_at)}
                  </p>
                </div>
                <div className="flex space-x-2 ml-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEdit(location)}
                  >
                    <Edit2 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(location.id)}
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
