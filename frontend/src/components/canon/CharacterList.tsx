'use client'

import { useState, useEffect } from 'react'
import { Character } from '@/types/canon'
import api from '@/lib/api'
import Button from '@/components/Button'
import { Plus, Edit2, Trash2 } from 'lucide-react'
import { formatDateTime } from '@/lib/utils'
import CharacterForm from './CharacterForm'

interface CharacterListProps {
  projectId: number
}

export default function CharacterList({ projectId }: CharacterListProps) {
  const [characters, setCharacters] = useState<Character[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(null)

  const fetchCharacters = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/api/canon/character`, {
        params: { project_id: projectId },
      })
      setCharacters(response.data)
    } catch (error) {
      console.error('Failed to fetch characters:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCharacters()
  }, [projectId])

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this character?')) return

    try {
      await api.delete(`/api/canon/character/${id}`)
      fetchCharacters()
    } catch (error) {
      console.error('Failed to delete character:', error)
    }
  }

  const handleEdit = (character: Character) => {
    setEditingCharacter(character)
    setShowForm(true)
  }

  const handleFormClose = () => {
    setShowForm(false)
    setEditingCharacter(null)
    fetchCharacters()
  }

  if (showForm) {
    return (
      <CharacterForm
        projectId={projectId}
        character={editingCharacter}
        onClose={handleFormClose}
      />
    )
  }

  if (loading) {
    return <div className="text-center py-12">Loading characters...</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Characters ({characters.length})</h2>
        <Button onClick={() => setShowForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Character
        </Button>
      </div>

      {characters.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No characters yet. Create your first character to get started.
        </div>
      ) : (
        <div className="grid gap-4">
          {characters.map((character) => (
            <div
              key={character.id}
              className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-blue-300 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {character.name}
                  </h3>
                  {character.description && (
                    <p className="text-gray-600 dark:text-gray-400 mt-1">
                      {character.description}
                    </p>
                  )}
                  {character.goals && character.goals.length > 0 && (
                    <div className="mt-2">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Goals:
                      </span>
                      <ul className="list-disc list-inside text-sm text-gray-600 dark:text-gray-400">
                        {character.goals.map((goal, idx) => (
                          <li key={idx}>{goal}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <p className="text-xs text-gray-500 mt-2">
                    Updated {formatDateTime(character.updated_at)}
                  </p>
                </div>
                <div className="flex space-x-2 ml-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleEdit(character)}
                  >
                    <Edit2 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(character.id)}
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
