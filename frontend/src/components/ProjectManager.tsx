'use client'

import { useState, useEffect } from 'react'
import {
  BookOpen,
  Plus,
  Search,
  Filter,
  Grid3x3,
  List,
  MoreVertical,
  Edit2,
  Copy,
  Archive,
  Trash2,
  Star,
  Calendar,
  TrendingUp,
  Users,
  MapPin,
  Sparkles,
  FileText,
  Clock,
  Target,
  CheckCircle2,
  X,
} from 'lucide-react'

interface ProjectStats {
  current_word_count: number
  chapters_count: number
  characters_count: number
  locations_count: number
  threads_count: number
  promises_count: number
  last_edited: string | null
  completion_percent: number
}

interface Project {
  id: number
  title: string
  genre: string | null
  target_word_count: number
  status: 'draft' | 'in_progress' | 'completed' | 'archived'
  metadata: Record<string, any>
  created_at: string
  updated_at: string
  stats: ProjectStats
}

interface ProjectManagerProps {
  accessToken: string
  onSelectProject: (projectId: number) => void
  currentProjectId?: number
}

export default function ProjectManager({
  accessToken,
  onSelectProject,
  currentProjectId,
}: ProjectManagerProps) {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showProjectMenu, setShowProjectMenu] = useState<number | null>(null)

  // Create project form
  const [newProject, setNewProject] = useState({
    title: '',
    genre: '',
    target_word_count: 80000,
    description: '',
  })

  useEffect(() => {
    fetchProjects()
  }, [statusFilter])

  const fetchProjects = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (statusFilter !== 'all') {
        params.append('status', statusFilter)
      }
      params.append('include_archived', statusFilter === 'archived' ? 'true' : 'false')

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/projects?${params}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setProjects(data.projects)
      }
    } catch (error) {
      console.error('Failed to fetch projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateProject = async () => {
    if (!newProject.title.trim()) return

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/projects`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: newProject.title,
          genre: newProject.genre || null,
          target_word_count: newProject.target_word_count,
          description: newProject.description,
        }),
      })

      if (response.ok) {
        const created = await response.json()
        setProjects([created, ...projects])
        setShowCreateModal(false)
        setNewProject({ title: '', genre: '', target_word_count: 80000, description: '' })
        onSelectProject(created.id)
      }
    } catch (error) {
      console.error('Failed to create project:', error)
    }
  }

  const handleDuplicateProject = async (projectId: number, title: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/projects/${projectId}/duplicate`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            new_title: `${title} (Kopia)`,
            include_canon: true,
            include_chapters: false,
            include_settings: true,
          }),
        }
      )

      if (response.ok) {
        fetchProjects()
      }
    } catch (error) {
      console.error('Failed to duplicate project:', error)
    }
  }

  const handleArchiveProject = async (projectId: number) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/projects/${projectId}/archive`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ archive: true }),
        }
      )

      if (response.ok) {
        fetchProjects()
      }
    } catch (error) {
      console.error('Failed to archive project:', error)
    }
  }

  const handleDeleteProject = async (projectId: number) => {
    if (!confirm('Czy na pewno chcesz trwale usunąć ten projekt? Tej operacji nie można cofnąć!')) {
      return
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/projects/${projectId}?permanent=true`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      )

      if (response.ok) {
        fetchProjects()
      }
    } catch (error) {
      console.error('Failed to delete project:', error)
    }
  }

  const filteredProjects = projects.filter((project) => {
    if (searchQuery && !project.title.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false
    }
    return true
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft':
        return 'bg-gray-500'
      case 'in_progress':
        return 'bg-blue-500'
      case 'completed':
        return 'bg-green-500'
      case 'archived':
        return 'bg-orange-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'draft':
        return 'Szkic'
      case 'in_progress':
        return 'W trakcie'
      case 'completed':
        return 'Ukończony'
      case 'archived':
        return 'Archiwum'
      default:
        return status
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
              <BookOpen className="w-10 h-10 text-purple-400" />
              Moje Projekty
            </h1>
            <p className="text-gray-400">
              Zarządzaj swoimi książkami i wybierz workspace do pracy
            </p>
          </div>

          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg hover:shadow-purple-500/50"
          >
            <Plus className="w-5 h-5" />
            Nowy Projekt
          </button>
        </div>

        {/* Filters & Search */}
        <div className="flex items-center gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Szukaj projektów..."
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
            />
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
          >
            <option value="all">Wszystkie</option>
            <option value="draft">Szkice</option>
            <option value="in_progress">W trakcie</option>
            <option value="completed">Ukończone</option>
            <option value="archived">Archiwum</option>
          </select>

          <div className="flex items-center gap-2 bg-gray-800 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded ${
                viewMode === 'grid' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              <Grid3x3 className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded ${
                viewMode === 'list' ? 'bg-purple-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Stats Summary */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
            <p className="text-gray-400 text-sm mb-1">Wszystkie projekty</p>
            <p className="text-2xl font-bold text-white">{projects.length}</p>
          </div>
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
            <p className="text-gray-400 text-sm mb-1">W trakcie</p>
            <p className="text-2xl font-bold text-blue-400">
              {projects.filter((p) => p.status === 'in_progress').length}
            </p>
          </div>
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
            <p className="text-gray-400 text-sm mb-1">Ukończone</p>
            <p className="text-2xl font-bold text-green-400">
              {projects.filter((p) => p.status === 'completed').length}
            </p>
          </div>
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
            <p className="text-gray-400 text-sm mb-1">Całkowite słowa</p>
            <p className="text-2xl font-bold text-purple-400">
              {projects
                .reduce((sum, p) => sum + (p.stats?.current_word_count || 0), 0)
                .toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Projects Grid/List */}
      <div className="max-w-7xl mx-auto">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-gray-400 mt-4">Ładowanie projektów...</p>
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 text-lg">Brak projektów do wyświetlenia</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Stwórz pierwszy projekt
            </button>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProjects.map((project) => (
              <div
                key={project.id}
                className={`bg-gray-800/50 backdrop-blur-sm rounded-xl border-2 transition-all cursor-pointer hover:shadow-xl hover:shadow-purple-500/20 ${
                  currentProjectId === project.id
                    ? 'border-purple-500 shadow-lg shadow-purple-500/30'
                    : 'border-gray-700 hover:border-purple-500'
                }`}
                onClick={() => onSelectProject(project.id)}
              >
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-white mb-2">{project.title}</h3>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 ${getStatusColor(project.status)} text-white text-xs rounded-full`}>
                          {getStatusLabel(project.status)}
                        </span>
                        {project.genre && (
                          <span className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded-full">
                            {project.genre}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="relative">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setShowProjectMenu(showProjectMenu === project.id ? null : project.id)
                        }}
                        className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                      >
                        <MoreVertical className="w-5 h-5 text-gray-400" />
                      </button>

                      {showProjectMenu === project.id && (
                        <div className="absolute right-0 top-full mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-10">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDuplicateProject(project.id, project.title)
                              setShowProjectMenu(null)
                            }}
                            className="w-full px-4 py-2 text-left text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                          >
                            <Copy className="w-4 h-4" />
                            Duplikuj
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleArchiveProject(project.id)
                              setShowProjectMenu(null)
                            }}
                            className="w-full px-4 py-2 text-left text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                          >
                            <Archive className="w-4 h-4" />
                            Archiwizuj
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleDeleteProject(project.id)
                              setShowProjectMenu(null)
                            }}
                            className="w-full px-4 py-2 text-left text-red-400 hover:bg-gray-700 flex items-center gap-2"
                          >
                            <Trash2 className="w-4 h-4" />
                            Usuń
                          </button>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-sm mb-2">
                      <span className="text-gray-400">Postęp</span>
                      <span className="text-purple-400 font-semibold">
                        {project.stats?.completion_percent || 0}%
                      </span>
                    </div>
                    <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                        style={{ width: `${project.stats?.completion_percent || 0}%` }}
                      />
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-3 mb-4">
                    <div className="flex items-center gap-2 text-sm">
                      <FileText className="w-4 h-4 text-blue-400" />
                      <span className="text-gray-400">
                        {project.stats?.current_word_count?.toLocaleString() || 0} słów
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Target className="w-4 h-4 text-green-400" />
                      <span className="text-gray-400">
                        {project.target_word_count?.toLocaleString() || 0} cel
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Users className="w-4 h-4 text-purple-400" />
                      <span className="text-gray-400">
                        {project.stats?.characters_count || 0} postaci
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <MapPin className="w-4 h-4 text-orange-400" />
                      <span className="text-gray-400">
                        {project.stats?.locations_count || 0} lokacji
                      </span>
                    </div>
                  </div>

                  {/* Footer */}
                  <div className="pt-4 border-t border-gray-700 flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      <span>
                        {project.stats?.last_edited
                          ? new Date(project.stats.last_edited).toLocaleDateString('pl-PL')
                          : 'Brak edycji'}
                      </span>
                    </div>
                    {currentProjectId === project.id && (
                      <span className="flex items-center gap-1 text-purple-400 font-semibold">
                        <CheckCircle2 className="w-3 h-3" />
                        Aktywny
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          // List view
          <div className="space-y-3">
            {filteredProjects.map((project) => (
              <div
                key={project.id}
                className={`bg-gray-800/50 backdrop-blur-sm rounded-lg border-2 p-4 flex items-center gap-6 cursor-pointer hover:border-purple-500 transition-all ${
                  currentProjectId === project.id ? 'border-purple-500' : 'border-gray-700'
                }`}
                onClick={() => onSelectProject(project.id)}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-bold text-white">{project.title}</h3>
                    <span className={`px-2 py-1 ${getStatusColor(project.status)} text-white text-xs rounded-full`}>
                      {getStatusLabel(project.status)}
                    </span>
                    {project.genre && (
                      <span className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded-full">
                        {project.genre}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-6 text-sm text-gray-400">
                    <span>{project.stats?.current_word_count?.toLocaleString() || 0} słów</span>
                    <span>{project.stats?.characters_count || 0} postaci</span>
                    <span>{project.stats?.locations_count || 0} lokacji</span>
                    <span>{project.stats?.completion_percent || 0}% ukończone</span>
                  </div>
                </div>

                {currentProjectId === project.id && (
                  <span className="flex items-center gap-2 text-purple-400 font-semibold">
                    <CheckCircle2 className="w-5 h-5" />
                    Aktywny workspace
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-2xl border border-gray-700 max-w-2xl w-full p-8 shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                <Sparkles className="w-7 h-7 text-purple-400" />
                Nowy Projekt
              </h2>
              <button
                onClick={() => setShowCreateModal(false)}
                className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-6 h-6 text-gray-400" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Tytuł projektu *
                </label>
                <input
                  type="text"
                  value={newProject.title}
                  onChange={(e) => setNewProject({ ...newProject, title: e.target.value })}
                  placeholder="Mroczna Forteca"
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                  autoFocus
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Gatunek</label>
                  <input
                    type="text"
                    value={newProject.genre}
                    onChange={(e) => setNewProject({ ...newProject, genre: e.target.value })}
                    placeholder="Fantasy, Thriller..."
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Cel słów
                  </label>
                  <input
                    type="number"
                    value={newProject.target_word_count}
                    onChange={(e) =>
                      setNewProject({ ...newProject, target_word_count: parseInt(e.target.value) })
                    }
                    className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Opis</label>
                <textarea
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  placeholder="Krótki opis projektu..."
                  rows={3}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 resize-none"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  onClick={handleCreateProject}
                  disabled={!newProject.title.trim()}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-purple-500/50"
                >
                  Stwórz Projekt
                </button>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-6 py-3 bg-gray-700 text-white rounded-lg font-semibold hover:bg-gray-600 transition-colors"
                >
                  Anuluj
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
