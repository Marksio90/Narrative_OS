'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import {
  User, MapPin, Sparkles, Book, Clock, Wand2,
  Plus, Search, Filter, ArrowUpDown, Edit2, Trash2,
  Eye, Heart, Shield, Zap, Target, MessageSquare
} from 'lucide-react'
import CharacterModal from '@/components/CharacterModal'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Character {
  id: number
  project_id: number
  name: string
  role: string
  goals: string[]
  values: string[]
  fears: string[]
  secrets: string[]
  behavioral_limits: string[]
  voice_profile?: {
    vocabulary_level: string
    sentence_structure: string
    emotional_expression: string
    quirks: string[]
  }
  arc?: {
    starting_state: string
    goal_state: string
    key_transformations: string[]
  }
  created_at: string
  updated_at: string
}

interface Location {
  id: number
  project_id: number
  name: string
  description: string
  geography?: string
  climate?: string
  culture?: string
  social_rules?: string[]
  restrictions?: string[]
  atmosphere?: string
  created_at: string
  updated_at: string
}

interface PlotThread {
  id: number
  project_id: number
  name: string
  description: string
  thread_type: 'main' | 'subplot' | 'character_arc' | 'mystery' | 'romance' | 'theme'
  status: 'active' | 'resolved' | 'abandoned'
  start_chapter?: number
  end_chapter?: number
  key_moments: string[]
  related_characters: number[]
  created_at: string
  updated_at: string
}

type Tab = 'characters' | 'locations' | 'threads' | 'magic' | 'timeline'

export default function StoryBiblePage() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<Tab>('characters')
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  // Data states
  const [characters, setCharacters] = useState<Character[]>([])
  const [locations, setLocations] = useState<Location[]>([])
  const [threads, setThreads] = useState<PlotThread[]>([])

  // Modal states
  const [showCharacterModal, setShowCharacterModal] = useState(false)
  const [showLocationModal, setShowLocationModal] = useState(false)
  const [showThreadModal, setShowThreadModal] = useState(false)
  const [editingItem, setEditingItem] = useState<any>(null)

  // Redirect if not authenticated
  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/login')
    }
  }, [status, router])

  // Load data
  useEffect(() => {
    if (session?.accessToken) {
      loadAllData()
    }
  }, [session?.accessToken])

  const loadAllData = async () => {
    setIsLoading(true)
    try {
      // For now, using project_id = 1 (would come from project selector)
      await Promise.all([
        loadCharacters(),
        loadLocations(),
        loadThreads()
      ])
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadCharacters = async () => {
    try {
      const response = await fetch(`${API_URL}/api/canon/character?project_id=1`, {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setCharacters(data)
      }
    } catch (error) {
      console.error('Error loading characters:', error)
    }
  }

  const loadLocations = async () => {
    try {
      const response = await fetch(`${API_URL}/api/canon/location?project_id=1`, {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setLocations(data)
      }
    } catch (error) {
      console.error('Error loading locations:', error)
    }
  }

  const loadThreads = async () => {
    try {
      const response = await fetch(`${API_URL}/api/canon/thread?project_id=1`, {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setThreads(data)
      }
    } catch (error) {
      console.error('Error loading threads:', error)
    }
  }

  if (status === 'loading' || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading Story Bible...</p>
        </div>
      </div>
    )
  }

  const tabs = [
    { id: 'characters' as Tab, name: 'Characters', icon: User, count: characters.length },
    { id: 'locations' as Tab, name: 'Locations', icon: MapPin, count: locations.length },
    { id: 'threads' as Tab, name: 'Plot Threads', icon: Sparkles, count: threads.length },
    { id: 'magic' as Tab, name: 'Magic & Rules', icon: Wand2, count: 0 },
    { id: 'timeline' as Tab, name: 'Timeline', icon: Clock, count: 0 },
  ]

  const handleAddNew = () => {
    setEditingItem(null)
    if (activeTab === 'characters') setShowCharacterModal(true)
    if (activeTab === 'locations') setShowLocationModal(true)
    if (activeTab === 'threads') setShowThreadModal(true)
  }

  const handleEdit = (item: any) => {
    setEditingItem(item)
    if (activeTab === 'characters') setShowCharacterModal(true)
    if (activeTab === 'locations') setShowLocationModal(true)
    if (activeTab === 'threads') setShowThreadModal(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this item?')) return

    try {
      let endpoint = ''
      if (activeTab === 'characters') endpoint = `/api/canon/character/${id}`
      if (activeTab === 'locations') endpoint = `/api/canon/location/${id}`
      if (activeTab === 'threads') endpoint = `/api/canon/thread/${id}`

      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })

      if (response.ok) {
        loadAllData()
      }
    } catch (error) {
      console.error('Error deleting item:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
                <Book className="h-8 w-8 text-indigo-600" />
                <span>Story Bible</span>
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Your canon, characters, world, and narrative threads
              </p>
            </div>
            <button
              onClick={handleAddNew}
              className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition shadow-sm"
            >
              <Plus className="h-5 w-5" />
              <span>Add New</span>
            </button>
          </div>

          {/* Tabs */}
          <div className="mt-6 flex space-x-1 border-b border-gray-200">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 py-3 font-medium text-sm transition ${
                    isActive
                      ? 'text-indigo-600 border-b-2 border-indigo-600'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.name}</span>
                  <span className={`px-2 py-0.5 text-xs rounded-full ${
                    isActive ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {tab.count}
                  </span>
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder={`Search ${activeTab}...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            <Filter className="h-5 w-5 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Filter</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
            <ArrowUpDown className="h-5 w-5 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Sort</span>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        {activeTab === 'characters' && (
          <CharactersTab
            characters={characters}
            searchQuery={searchQuery}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        )}
        {activeTab === 'locations' && (
          <LocationsTab
            locations={locations}
            searchQuery={searchQuery}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        )}
        {activeTab === 'threads' && (
          <ThreadsTab
            threads={threads}
            searchQuery={searchQuery}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        )}
        {(activeTab === 'magic' || activeTab === 'timeline') && (
          <div className="text-center py-12">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
              <Wand2 className="h-8 w-8 text-gray-400" />
            </div>
            <p className="text-gray-600">Coming soon...</p>
          </div>
        )}
      </div>

      {/* Modals */}
      {showCharacterModal && (
        <CharacterModal
          character={editingItem}
          onClose={() => {
            setShowCharacterModal(false)
            setEditingItem(null)
          }}
          onSave={() => {
            loadCharacters()
            setShowCharacterModal(false)
            setEditingItem(null)
          }}
          accessToken={session?.accessToken || ''}
        />
      )}
      {showLocationModal && (
        <LocationModal
          location={editingItem}
          onClose={() => {
            setShowLocationModal(false)
            setEditingItem(null)
          }}
          onSave={() => {
            loadLocations()
            setShowLocationModal(false)
            setEditingItem(null)
          }}
          accessToken={session?.accessToken || ''}
        />
      )}
      {showThreadModal && (
        <ThreadModal
          thread={editingItem}
          onClose={() => {
            setShowThreadModal(false)
            setEditingItem(null)
          }}
          onSave={() => {
            loadThreads()
            setShowThreadModal(false)
            setEditingItem(null)
          }}
          accessToken={session?.accessToken || ''}
        />
      )}
    </div>
  )
}

// Characters Tab Component
function CharactersTab({
  characters,
  searchQuery,
  onEdit,
  onDelete
}: {
  characters: Character[]
  searchQuery: string
  onEdit: (item: any) => void
  onDelete: (id: number) => void
}) {
  const filtered = characters.filter(c =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.role?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (filtered.length === 0) {
    return (
      <div className="text-center py-12">
        <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No characters found</p>
        <p className="text-sm text-gray-500 mt-1">Create your first character to get started</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {filtered.map((character) => (
        <CharacterCard
          key={character.id}
          character={character}
          onEdit={() => onEdit(character)}
          onDelete={() => onDelete(character.id)}
        />
      ))}
    </div>
  )
}

// Character Card Component
function CharacterCard({
  character,
  onEdit,
  onDelete
}: {
  character: Character
  onEdit: () => void
  onDelete: () => void
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition overflow-hidden">
      {/* Header with gradient */}
      <div className="h-24 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 relative">
        <div className="absolute -bottom-8 left-6">
          <div className="w-16 h-16 rounded-full bg-white border-4 border-white shadow-lg flex items-center justify-center">
            <User className="h-8 w-8 text-indigo-600" />
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="pt-10 px-6 pb-6">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h3 className="text-lg font-bold text-gray-900">{character.name}</h3>
            {character.role && (
              <p className="text-sm text-gray-600">{character.role}</p>
            )}
          </div>
          <div className="flex space-x-1">
            <button
              onClick={onEdit}
              className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded transition"
            >
              <Edit2 className="h-4 w-4" />
            </button>
            <button
              onClick={onDelete}
              className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-100">
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Target className="h-4 w-4 text-green-600" />
            </div>
            <p className="text-xs text-gray-600">Goals</p>
            <p className="text-sm font-semibold text-gray-900">{character.goals?.length || 0}</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Shield className="h-4 w-4 text-blue-600" />
            </div>
            <p className="text-xs text-gray-600">Values</p>
            <p className="text-sm font-semibold text-gray-900">{character.values?.length || 0}</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Zap className="h-4 w-4 text-amber-600" />
            </div>
            <p className="text-xs text-gray-600">Secrets</p>
            <p className="text-sm font-semibold text-gray-900">{character.secrets?.length || 0}</p>
          </div>
        </div>

        {/* Tags */}
        {character.goals && character.goals.length > 0 && (
          <div className="mt-4">
            <div className="flex flex-wrap gap-1">
              {character.goals.slice(0, 2).map((goal, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 text-xs bg-green-50 text-green-700 rounded"
                >
                  {goal.length > 20 ? goal.substring(0, 20) + '...' : goal}
                </span>
              ))}
              {character.goals.length > 2 && (
                <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                  +{character.goals.length - 2} more
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Locations Tab Component
function LocationsTab({
  locations,
  searchQuery,
  onEdit,
  onDelete
}: {
  locations: Location[]
  searchQuery: string
  onEdit: (item: any) => void
  onDelete: (id: number) => void
}) {
  const filtered = locations.filter(l =>
    l.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    l.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (filtered.length === 0) {
    return (
      <div className="text-center py-12">
        <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No locations found</p>
        <p className="text-sm text-gray-500 mt-1">Create your first location to build your world</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {filtered.map((location) => (
        <LocationCard
          key={location.id}
          location={location}
          onEdit={() => onEdit(location)}
          onDelete={() => onDelete(location.id)}
        />
      ))}
    </div>
  )
}

// Location Card Component
function LocationCard({
  location,
  onEdit,
  onDelete
}: {
  location: Location
  onEdit: () => void
  onDelete: () => void
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start space-x-3">
          <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center flex-shrink-0">
            <MapPin className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">{location.name}</h3>
            {location.description && (
              <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                {location.description}
              </p>
            )}
          </div>
        </div>
        <div className="flex space-x-1">
          <button
            onClick={onEdit}
            className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded transition"
          >
            <Edit2 className="h-4 w-4" />
          </button>
          <button
            onClick={onDelete}
            className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Details */}
      <div className="space-y-2 text-sm">
        {location.climate && (
          <div className="flex items-start space-x-2">
            <span className="text-gray-500 font-medium w-20">Climate:</span>
            <span className="text-gray-900">{location.climate}</span>
          </div>
        )}
        {location.atmosphere && (
          <div className="flex items-start space-x-2">
            <span className="text-gray-500 font-medium w-20">Mood:</span>
            <span className="text-gray-900">{location.atmosphere}</span>
          </div>
        )}
        {location.social_rules && location.social_rules.length > 0 && (
          <div className="flex items-start space-x-2">
            <span className="text-gray-500 font-medium w-20">Rules:</span>
            <span className="text-gray-900">{location.social_rules.length} rules</span>
          </div>
        )}
      </div>
    </div>
  )
}

// Threads Tab Component
function ThreadsTab({
  threads,
  searchQuery,
  onEdit,
  onDelete
}: {
  threads: PlotThread[]
  searchQuery: string
  onEdit: (item: any) => void
  onDelete: (id: number) => void
}) {
  const filtered = threads.filter(t =>
    t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (filtered.length === 0) {
    return (
      <div className="text-center py-12">
        <Sparkles className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No plot threads found</p>
        <p className="text-sm text-gray-500 mt-1">Create your first plot thread to track story arcs</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {filtered.map((thread) => (
        <ThreadCard
          key={thread.id}
          thread={thread}
          onEdit={() => onEdit(thread)}
          onDelete={() => onDelete(thread.id)}
        />
      ))}
    </div>
  )
}

// Thread Card Component
function ThreadCard({
  thread,
  onEdit,
  onDelete
}: {
  thread: PlotThread
  onEdit: () => void
  onDelete: () => void
}) {
  const typeColors = {
    main: 'from-purple-500 to-indigo-600',
    subplot: 'from-blue-500 to-cyan-600',
    character_arc: 'from-green-500 to-emerald-600',
    mystery: 'from-amber-500 to-orange-600',
    romance: 'from-pink-500 to-rose-600',
    theme: 'from-violet-500 to-purple-600',
  }

  const statusColors = {
    active: 'bg-green-100 text-green-700',
    resolved: 'bg-gray-100 text-gray-700',
    abandoned: 'bg-red-100 text-red-700',
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start space-x-4 flex-1">
          <div className={`w-1 h-full min-h-[80px] rounded-full bg-gradient-to-b ${typeColors[thread.thread_type]}`} />
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="text-lg font-bold text-gray-900">{thread.name}</h3>
              <span className={`px-2 py-1 text-xs font-medium rounded ${statusColors[thread.status]}`}>
                {thread.status}
              </span>
              <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded capitalize">
                {thread.thread_type.replace('_', ' ')}
              </span>
            </div>
            {thread.description && (
              <p className="text-sm text-gray-600 mb-3">{thread.description}</p>
            )}
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              {thread.start_chapter && (
                <span>Start: Ch. {thread.start_chapter}</span>
              )}
              {thread.end_chapter && (
                <span>End: Ch. {thread.end_chapter}</span>
              )}
              {thread.key_moments && thread.key_moments.length > 0 && (
                <span>{thread.key_moments.length} key moments</span>
              )}
            </div>
          </div>
        </div>
        <div className="flex space-x-1">
          <button
            onClick={onEdit}
            className="p-1.5 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded transition"
          >
            <Edit2 className="h-4 w-4" />
          </button>
          <button
            onClick={onDelete}
            className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

// Placeholder modals for Location and Thread (to be implemented)
function LocationModal({ location, onClose, onSave, accessToken }: any) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full p-6">
        <h2 className="text-2xl font-bold mb-4">
          {location ? 'Edit Location' : 'New Location'}
        </h2>
        <p className="text-gray-600 mb-4">Location editor coming in next iteration...</p>
        <div className="flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={onSave}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  )
}

function ThreadModal({ thread, onClose, onSave, accessToken }: any) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full p-6">
        <h2 className="text-2xl font-bold mb-4">
          {thread ? 'Edit Plot Thread' : 'New Plot Thread'}
        </h2>
        <p className="text-gray-600 mb-4">Thread editor coming in next iteration...</p>
        <div className="flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={onSave}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  )
}
