'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import {
  User, MapPin, Sparkles, Book, Clock, Wand2,
  Plus, Search, Filter, ArrowUpDown, Edit2, Trash2,
  Eye, Heart, Shield, Zap, Target, MessageSquare,
  Download, Upload, AlertCircle, Users, X, FileJson
} from 'lucide-react'
import CharacterModal from '@/components/CharacterModal'
import LocationModal from '@/components/LocationModal'
import ThreadModal from '@/components/ThreadModal'
import MagicModal from '@/components/MagicModal'
import TimelineModal from '@/components/TimelineModal'

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

interface MagicSystem {
  id: number
  project_id: number
  name: string
  description: string
  magic_type: 'hard' | 'soft' | 'hybrid'
  power_source?: string
  costs: string[]
  limitations: string[]
  rules: string[]
  practitioners?: string
  manifestation?: string
  cultural_impact?: string
  created_at: string
  updated_at: string
}

interface TimelineEvent {
  id: number
  project_id: number
  name: string
  description: string
  event_type: 'plot' | 'backstory' | 'world' | 'character'
  date_in_story?: string
  chapter_number?: number
  location?: string
  participants: string[]
  consequences: string[]
  related_events?: number[]
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
  const [magicSystems, setMagicSystems] = useState<MagicSystem[]>([])
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([])

  // Modal states
  const [showCharacterModal, setShowCharacterModal] = useState(false)
  const [showLocationModal, setShowLocationModal] = useState(false)
  const [showThreadModal, setShowThreadModal] = useState(false)
  const [showMagicModal, setShowMagicModal] = useState(false)
  const [showTimelineModal, setShowTimelineModal] = useState(false)
  const [showImportModal, setShowImportModal] = useState(false)
  const [editingItem, setEditingItem] = useState<any>(null)

  // Export/Import states
  const [importFile, setImportFile] = useState<File | null>(null)
  const [importOverwrite, setImportOverwrite] = useState(false)
  const [importing, setImporting] = useState(false)
  const [importResult, setImportResult] = useState<any>(null)

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
        loadThreads(),
        loadMagicSystems(),
        loadTimelineEvents()
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

  const loadMagicSystems = async () => {
    try {
      const response = await fetch(`${API_URL}/api/canon/magic?project_id=1`, {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setMagicSystems(data)
      }
    } catch (error) {
      console.error('Error loading magic systems:', error)
    }
  }

  const loadTimelineEvents = async () => {
    try {
      const response = await fetch(`${API_URL}/api/canon/event?project_id=1`, {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })
      if (response.ok) {
        const data = await response.json()
        setTimelineEvents(data)
      }
    } catch (error) {
      console.error('Error loading timeline events:', error)
    }
  }

  if (status === 'loading' || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Ładowanie Biblii Fabuły...</p>
        </div>
      </div>
    )
  }

  const tabs = [
    { id: 'characters' as Tab, name: 'Postacie', icon: User, count: characters.length },
    { id: 'locations' as Tab, name: 'Lokacje', icon: MapPin, count: locations.length },
    { id: 'threads' as Tab, name: 'Wątki Fabularne', icon: Sparkles, count: threads.length },
    { id: 'magic' as Tab, name: 'Magia i Zasady', icon: Wand2, count: magicSystems.length },
    { id: 'timeline' as Tab, name: 'Oś Czasu', icon: Clock, count: timelineEvents.length },
  ]

  const handleAddNew = () => {
    setEditingItem(null)
    if (activeTab === 'characters') setShowCharacterModal(true)
    if (activeTab === 'locations') setShowLocationModal(true)
    if (activeTab === 'threads') setShowThreadModal(true)
    if (activeTab === 'magic') setShowMagicModal(true)
    if (activeTab === 'timeline') setShowTimelineModal(true)
  }

  const handleEdit = (item: any) => {
    setEditingItem(item)
    if (activeTab === 'characters') setShowCharacterModal(true)
    if (activeTab === 'locations') setShowLocationModal(true)
    if (activeTab === 'threads') setShowThreadModal(true)
    if (activeTab === 'magic') setShowMagicModal(true)
    if (activeTab === 'timeline') setShowTimelineModal(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this item?')) return

    try {
      let endpoint = ''
      if (activeTab === 'characters') endpoint = `/api/canon/character/${id}`
      if (activeTab === 'locations') endpoint = `/api/canon/location/${id}`
      if (activeTab === 'threads') endpoint = `/api/canon/thread/${id}`
      if (activeTab === 'magic') endpoint = `/api/canon/magic/${id}`
      if (activeTab === 'timeline') endpoint = `/api/canon/event/${id}`

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

  const handleExport = async () => {
    try {
      const response = await fetch(`${API_URL}/api/canon/export/1`, {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })

      if (response.ok) {
        const data = await response.json()

        // Create filename with timestamp
        const timestamp = new Date().toISOString().split('T')[0]
        const filename = `biblia-fabuly-${timestamp}.json`

        // Download JSON file
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      } else {
        alert('Błąd podczas eksportu')
      }
    } catch (error) {
      console.error('Error exporting canon:', error)
      alert('Błąd podczas eksportu')
    }
  }

  const handleImport = async () => {
    if (!importFile) {
      alert('Wybierz plik do importu')
      return
    }

    if (importOverwrite && !confirm('UWAGA: Tryb nadpisywania usunie WSZYSTKIE istniejące dane! Czy jesteś pewien?')) {
      return
    }

    setImporting(true)
    setImportResult(null)

    try {
      // Read file
      const fileContent = await importFile.text()
      const importData = JSON.parse(fileContent)

      // Send to API
      const response = await fetch(`${API_URL}/api/canon/import/1`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          entities: importData.entities,
          overwrite: importOverwrite,
          commit_message: `Import z ${importFile.name}`
        }),
      })

      const result = await response.json()

      if (response.ok) {
        setImportResult(result)
        // Reload all data
        await loadAllData()

        if (result.success) {
          setTimeout(() => {
            setShowImportModal(false)
            setImportFile(null)
            setImportOverwrite(false)
            setImportResult(null)
          }, 3000)
        }
      } else {
        setImportResult({ success: false, errors: [result.detail || 'Import failed'] })
      }
    } catch (error) {
      console.error('Error importing canon:', error)
      setImportResult({ success: false, errors: [String(error)] })
    } finally {
      setImporting(false)
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
                <span>Biblia Fabuły</span>
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Twój kanon, postacie, świat i wątki fabularne
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleExport}
                className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition shadow-sm"
                title="Eksportuj całą biblię fabuły jako JSON"
              >
                <Download className="h-5 w-5" />
                <span>Eksportuj</span>
              </button>
              <button
                onClick={() => setShowImportModal(true)}
                className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition shadow-sm"
                title="Importuj biblię fabuły z JSON"
              >
                <Upload className="h-5 w-5" />
                <span>Importuj</span>
              </button>
              <button
                onClick={handleAddNew}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition shadow-sm"
              >
                <Plus className="h-5 w-5" />
                <span>Dodaj Nowy</span>
              </button>
            </div>
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
        {activeTab === 'magic' && (
          <MagicTab
            magicSystems={magicSystems}
            searchQuery={searchQuery}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        )}
        {activeTab === 'timeline' && (
          <TimelineTab
            events={timelineEvents}
            searchQuery={searchQuery}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
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
      {showMagicModal && (
        <MagicModal
          magicSystem={editingItem}
          onClose={() => {
            setShowMagicModal(false)
            setEditingItem(null)
          }}
          onSave={() => {
            loadMagicSystems()
            setShowMagicModal(false)
            setEditingItem(null)
          }}
          accessToken={session?.accessToken || ''}
        />
      )}
      {showTimelineModal && (
        <TimelineModal
          event={editingItem}
          onClose={() => {
            setShowTimelineModal(false)
            setEditingItem(null)
          }}
          onSave={() => {
            loadTimelineEvents()
            setShowTimelineModal(false)
            setEditingItem(null)
          }}
          accessToken={session?.accessToken || ''}
        />
      )}

      {/* Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
                  <Upload className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Importuj Biblię Fabuły</h2>
                  <p className="text-sm text-gray-600">Wczytaj dane z pliku JSON</p>
                </div>
              </div>
              <button
                onClick={() => {
                  setShowImportModal(false)
                  setImportFile(null)
                  setImportOverwrite(false)
                  setImportResult(null)
                }}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* File Upload */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Wybierz plik JSON *
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-indigo-500 transition">
                  <input
                    type="file"
                    accept=".json"
                    onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                    className="hidden"
                    id="import-file"
                  />
                  <label
                    htmlFor="import-file"
                    className="cursor-pointer flex flex-col items-center space-y-2"
                  >
                    <FileJson className="h-12 w-12 text-gray-400" />
                    {importFile ? (
                      <div>
                        <p className="text-sm font-medium text-gray-900">{importFile.name}</p>
                        <p className="text-xs text-gray-500">{(importFile.size / 1024).toFixed(2)} KB</p>
                      </div>
                    ) : (
                      <div>
                        <p className="text-sm font-medium text-gray-700">Kliknij aby wybrać plik</p>
                        <p className="text-xs text-gray-500">Tylko pliki JSON</p>
                      </div>
                    )}
                  </label>
                </div>
              </div>

              {/* Overwrite Option */}
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                <label className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={importOverwrite}
                    onChange={(e) => setImportOverwrite(e.target.checked)}
                    className="mt-1 h-4 w-4 text-amber-600 border-gray-300 rounded focus:ring-amber-500"
                  />
                  <div>
                    <p className="text-sm font-medium text-amber-900">Tryb nadpisywania (UWAGA!)</p>
                    <p className="text-xs text-amber-700 mt-1">
                      Usuń WSZYSTKIE istniejące dane przed importem. Ta operacja jest nieodwracalna!
                    </p>
                  </div>
                </label>
              </div>

              {/* Import Result */}
              {importResult && (
                <div className={`rounded-lg p-4 ${importResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                  <div className="flex items-start space-x-3">
                    {importResult.success ? (
                      <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center flex-shrink-0">
                        <svg className="h-4 w-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                    ) : (
                      <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <p className={`text-sm font-medium ${importResult.success ? 'text-green-900' : 'text-red-900'}`}>
                        {importResult.success ? 'Import zakończony sukcesem!' : 'Import zakończony błędami'}
                      </p>
                      {importResult.imported_counts && (
                        <div className="mt-2 text-xs text-green-700 space-y-1">
                          <p>Zaimportowano {importResult.imported_counts.total} elementów:</p>
                          <ul className="ml-4 space-y-0.5">
                            {importResult.imported_counts.character > 0 && <li>• Postacie: {importResult.imported_counts.character}</li>}
                            {importResult.imported_counts.location > 0 && <li>• Lokacje: {importResult.imported_counts.location}</li>}
                            {importResult.imported_counts.magic_rule > 0 && <li>• Systemy magii: {importResult.imported_counts.magic_rule}</li>}
                            {importResult.imported_counts.event > 0 && <li>• Wydarzenia: {importResult.imported_counts.event}</li>}
                            {importResult.imported_counts.promise > 0 && <li>• Obietnice: {importResult.imported_counts.promise}</li>}
                            {importResult.imported_counts.thread > 0 && <li>• Wątki: {importResult.imported_counts.thread}</li>}
                          </ul>
                        </div>
                      )}
                      {importResult.errors && importResult.errors.length > 0 && (
                        <div className="mt-2 text-xs text-red-700 space-y-1">
                          <p>Błędy:</p>
                          <ul className="ml-4 space-y-0.5">
                            {importResult.errors.map((error: string, idx: number) => (
                              <li key={idx}>• {error}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {importResult.warnings && importResult.warnings.length > 0 && (
                        <div className="mt-2 text-xs text-amber-700 space-y-1">
                          <p>Ostrzeżenia:</p>
                          <ul className="ml-4 space-y-0.5">
                            {importResult.warnings.map((warning: string, idx: number) => (
                              <li key={idx}>• {warning}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start space-x-2">
                  <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                  <div className="text-xs text-blue-700 space-y-1">
                    <p><strong>Import działa tylko z plikami eksportowanymi z tej aplikacji.</strong></p>
                    <p>• W trybie normalnym: dodaje nowe elementy do istniejących</p>
                    <p>• W trybie nadpisywania: usuwa wszystkie dane i importuje od zera</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
              <button
                onClick={() => {
                  setShowImportModal(false)
                  setImportFile(null)
                  setImportOverwrite(false)
                  setImportResult(null)
                }}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
              >
                Anuluj
              </button>
              <button
                onClick={handleImport}
                disabled={!importFile || importing}
                className={`px-6 py-2 rounded-lg transition font-medium ${
                  !importFile || importing
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white hover:from-emerald-700 hover:to-teal-700'
                }`}
              >
                {importing ? 'Importowanie...' : 'Importuj'}
              </button>
            </div>
          </div>
        </div>
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

// Magic Tab Component
function MagicTab({
  magicSystems,
  searchQuery,
  onEdit,
  onDelete
}: {
  magicSystems: MagicSystem[]
  searchQuery: string
  onEdit: (item: any) => void
  onDelete: (id: number) => void
}) {
  const filtered = magicSystems.filter(m =>
    m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    m.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (filtered.length === 0) {
    return (
      <div className="text-center py-12">
        <Wand2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No magic systems found</p>
        <p className="text-sm text-gray-500 mt-1">Create your first magic system to define the rules of your world</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {filtered.map((magic) => (
        <MagicCard
          key={magic.id}
          magicSystem={magic}
          onEdit={() => onEdit(magic)}
          onDelete={() => onDelete(magic.id)}
        />
      ))}
    </div>
  )
}

// Magic Card Component
function MagicCard({
  magicSystem,
  onEdit,
  onDelete
}: {
  magicSystem: MagicSystem
  onEdit: () => void
  onDelete: () => void
}) {
  const typeConfig = {
    hard: { icon: '⚙️', color: 'from-blue-500 to-indigo-600', label: 'Hard Magic' },
    soft: { icon: '✨', color: 'from-purple-500 to-pink-600', label: 'Soft Magic' },
    hybrid: { icon: '🌟', color: 'from-violet-500 to-fuchsia-600', label: 'Hybrid' },
  }

  const config = typeConfig[magicSystem.magic_type]

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition overflow-hidden">
      {/* Header with gradient */}
      <div className={`h-24 bg-gradient-to-br ${config.color} relative`}>
        <div className="absolute -bottom-8 left-6">
          <div className="w-16 h-16 rounded-full bg-white border-4 border-white shadow-lg flex items-center justify-center text-3xl">
            {config.icon}
          </div>
        </div>
        <div className="absolute top-4 right-4">
          <span className="px-3 py-1 bg-white bg-opacity-20 text-white text-xs font-medium rounded-full backdrop-blur-sm">
            {config.label}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="pt-10 px-6 pb-6">
        <div className="flex items-start justify-between mb-2">
          <div>
            <h3 className="text-lg font-bold text-gray-900">{magicSystem.name}</h3>
            {magicSystem.power_source && (
              <p className="text-sm text-gray-600 flex items-center space-x-1 mt-1">
                <Zap className="h-3 w-3" />
                <span>{magicSystem.power_source}</span>
              </p>
            )}
          </div>
          <div className="flex space-x-1">
            <button
              onClick={onEdit}
              className="p-1.5 text-gray-400 hover:text-purple-600 hover:bg-purple-50 rounded transition"
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

        {magicSystem.description && (
          <p className="text-sm text-gray-600 mt-2 mb-4 line-clamp-2">
            {magicSystem.description}
          </p>
        )}

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-100">
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Shield className="h-4 w-4 text-red-600" />
            </div>
            <p className="text-xs text-gray-600">Costs</p>
            <p className="text-sm font-semibold text-gray-900">{magicSystem.costs?.length || 0}</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <AlertCircle className="h-4 w-4 text-amber-600" />
            </div>
            <p className="text-xs text-gray-600">Limits</p>
            <p className="text-sm font-semibold text-gray-900">{magicSystem.limitations?.length || 0}</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-1">
              <Sparkles className="h-4 w-4 text-blue-600" />
            </div>
            <p className="text-xs text-gray-600">Rules</p>
            <p className="text-sm font-semibold text-gray-900">{magicSystem.rules?.length || 0}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

// Timeline Tab Component
function TimelineTab({
  events,
  searchQuery,
  onEdit,
  onDelete
}: {
  events: TimelineEvent[]
  searchQuery: string
  onEdit: (item: any) => void
  onDelete: (id: number) => void
}) {
  const filtered = events.filter(e =>
    e.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    e.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Sort by chapter number if available, otherwise by creation date
  const sorted = [...filtered].sort((a, b) => {
    if (a.chapter_number && b.chapter_number) {
      return a.chapter_number - b.chapter_number
    }
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })

  if (sorted.length === 0) {
    return (
      <div className="text-center py-12">
        <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No timeline events found</p>
        <p className="text-sm text-gray-500 mt-1">Create your first event to build your story's chronology</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {sorted.map((event, idx) => (
        <TimelineCard
          key={event.id}
          event={event}
          isFirst={idx === 0}
          isLast={idx === sorted.length - 1}
          onEdit={() => onEdit(event)}
          onDelete={() => onDelete(event.id)}
        />
      ))}
    </div>
  )
}

// Timeline Card Component
function TimelineCard({
  event,
  isFirst,
  isLast,
  onEdit,
  onDelete
}: {
  event: TimelineEvent
  isFirst: boolean
  isLast: boolean
  onEdit: () => void
  onDelete: () => void
}) {
  const typeConfig = {
    plot: { color: 'from-purple-500 to-indigo-600', badge: 'bg-purple-100 text-purple-700', icon: '📖', label: 'Plot' },
    backstory: { color: 'from-gray-500 to-slate-600', badge: 'bg-gray-100 text-gray-700', icon: '⏪', label: 'Backstory' },
    world: { color: 'from-blue-500 to-cyan-600', badge: 'bg-blue-100 text-blue-700', icon: '🌍', label: 'World' },
    character: { color: 'from-green-500 to-emerald-600', badge: 'bg-green-100 text-green-700', icon: '👤', label: 'Character' },
  }

  const config = typeConfig[event.event_type]

  return (
    <div className="flex items-start space-x-4">
      {/* Timeline Line */}
      <div className="flex flex-col items-center">
        <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${config.color} flex items-center justify-center text-2xl flex-shrink-0 shadow-lg`}>
          {config.icon}
        </div>
        {!isLast && (
          <div className="w-0.5 bg-gradient-to-b from-gray-300 to-gray-200 h-full min-h-[40px] flex-grow mt-2" />
        )}
      </div>

      {/* Content Card */}
      <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition p-6 mb-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <h3 className="text-lg font-bold text-gray-900">{event.name}</h3>
              <span className={`px-2 py-1 text-xs font-medium rounded ${config.badge}`}>
                {config.label}
              </span>
            </div>
            {event.description && (
              <p className="text-sm text-gray-600 mb-3">{event.description}</p>
            )}

            {/* Meta Info */}
            <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500">
              {event.chapter_number && (
                <span className="flex items-center space-x-1">
                  <Book className="h-3 w-3" />
                  <span>Ch. {event.chapter_number}</span>
                </span>
              )}
              {event.date_in_story && (
                <span className="flex items-center space-x-1">
                  <Clock className="h-3 w-3" />
                  <span>{event.date_in_story}</span>
                </span>
              )}
              {event.location && (
                <span className="flex items-center space-x-1">
                  <MapPin className="h-3 w-3" />
                  <span>{event.location}</span>
                </span>
              )}
              {event.participants && event.participants.length > 0 && (
                <span className="flex items-center space-x-1">
                  <Users className="h-3 w-3" />
                  <span>{event.participants.length} participants</span>
                </span>
              )}
              {event.consequences && event.consequences.length > 0 && (
                <span className="flex items-center space-x-1">
                  <Zap className="h-3 w-3" />
                  <span>{event.consequences.length} consequences</span>
                </span>
              )}
            </div>
          </div>

          <div className="flex space-x-1 flex-shrink-0 ml-4">
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
    </div>
  )
}
