'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import { useAuth } from '@/lib/auth-context'
import { useRouter } from 'next/navigation'
import {
  FileText,
  Save,
  Clock,
  TrendingUp,
  Target,
  Plus,
  ChevronLeft,
  ChevronRight,
  Settings,
  Maximize2,
  Eye,
  EyeOff,
  Sparkles,
  Book,
  List,
  Trash2,
  MoreVertical,
  CheckCircle2,
  Circle,
  AlertCircle,
} from 'lucide-react'

interface Chapter {
  id: number
  project_id: number
  chapter_number: number
  scene_number: number | null
  title: string
  word_count: number
  status: string
  last_edited_at: string
}

interface WritingSession {
  id: number
  started_at: string
  words_added: number
  keystrokes: number
}

export default function WritingStudioPage() {
  const { user, accessToken } = useAuth()
  const router = useRouter()

  const [projectId, setProjectId] = useState<number | null>(null)
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [currentChapter, setCurrentChapter] = useState<Chapter | null>(null)
  const [content, setContent] = useState('')
  const [initialWordCount, setInitialWordCount] = useState(0)
  const [wordCount, setWordCount] = useState(0)
  const [targetWords, setTargetWords] = useState(3000)

  // UI State
  const [showSidebar, setShowSidebar] = useState(true)
  const [focusMode, setFocusMode] = useState(false)
  const [autoSaveStatus, setAutoSaveStatus] = useState<'saved' | 'saving' | 'unsaved'>('saved')

  // Writing Session
  const [session, setSession] = useState<WritingSession | null>(null)
  const [sessionStartTime, setSessionStartTime] = useState<Date | null>(null)
  const [sessionDuration, setSessionDuration] = useState(0)
  const [keystrokes, setKeystrokes] = useState(0)

  // Refs
  const editorRef = useRef<HTMLTextAreaElement>(null)
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!user) {
      router.push('/login')
      return
    }

    // Load project ID from localStorage
    const savedProjectId = localStorage.getItem('currentProjectId')
    if (savedProjectId) {
      setProjectId(parseInt(savedProjectId))
    } else {
      router.push('/projects')
    }
  }, [user, router])

  useEffect(() => {
    if (projectId && accessToken) {
      loadChapters()
    }
  }, [projectId, accessToken])

  useEffect(() => {
    if (currentChapter && accessToken) {
      loadChapterContent()
    }
  }, [currentChapter?.id])

  // Session duration ticker
  useEffect(() => {
    if (!sessionStartTime) return

    const interval = setInterval(() => {
      const duration = Math.floor((new Date().getTime() - sessionStartTime.getTime()) / 1000)
      setSessionDuration(duration)
    }, 1000)

    return () => clearInterval(interval)
  }, [sessionStartTime])

  // Auto-save
  useEffect(() => {
    if (!currentChapter || autoSaveStatus !== 'unsaved') return

    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current)
    }

    autoSaveTimerRef.current = setTimeout(() => {
      handleAutoSave()
    }, 3000) // Auto-save after 3 seconds of no typing

    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current)
      }
    }
  }, [content, autoSaveStatus])

  const loadChapters = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/projects/${projectId}/chapters`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setChapters(data.chapters)

        // Auto-select first chapter if none selected
        if (!currentChapter && data.chapters.length > 0) {
          setCurrentChapter(data.chapters[0])
        }
      }
    } catch (error) {
      console.error('Failed to load chapters:', error)
    }
  }

  const loadChapterContent = async () => {
    if (!currentChapter) return

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/chapters/${currentChapter.id}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      )

      if (response.ok) {
        const data = await response.json()
        setContent(data.content || '')
        setWordCount(data.word_count)
        setInitialWordCount(data.word_count)
        setTargetWords(data.target_word_count)
        setAutoSaveStatus('saved')

        // Start writing session
        startWritingSession()
      }
    } catch (error) {
      console.error('Failed to load chapter:', error)
    }
  }

  const startWritingSession = async () => {
    if (!projectId || !currentChapter) return

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/projects/${projectId}/writing-sessions`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            chapter_id: currentChapter.id,
            metadata: {},
          }),
        }
      )

      if (response.ok) {
        const data = await response.json()
        setSession(data)
        setSessionStartTime(new Date())
      }
    } catch (error) {
      console.error('Failed to start session:', error)
    }
  }

  const handleAutoSave = async () => {
    if (!currentChapter) return

    setAutoSaveStatus('saving')

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/chapters/${currentChapter.id}/autosave`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            content,
            word_count: wordCount,
          }),
        }
      )

      if (response.ok) {
        setAutoSaveStatus('saved')
      } else {
        setAutoSaveStatus('unsaved')
      }
    } catch (error) {
      console.error('Auto-save failed:', error)
      setAutoSaveStatus('unsaved')
    }
  }

  const handleManualSave = async () => {
    if (!currentChapter) return

    setAutoSaveStatus('saving')

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/chapters/${currentChapter.id}`,
        {
          method: 'PATCH',
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            content,
          }),
        }
      )

      if (response.ok) {
        setAutoSaveStatus('saved')
        alert('Rozdział zapisany!')
      }
    } catch (error) {
      console.error('Save failed:', error)
    }
  }

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value
    setContent(newContent)
    setWordCount(newContent.trim().split(/\s+/).filter(Boolean).length)
    setAutoSaveStatus('unsaved')
    setKeystrokes(keystrokes + 1)
  }

  const handleCreateChapter = async () => {
    if (!projectId) return

    const newChapterNumber = chapters.length + 1
    const title = prompt('Tytuł nowego rozdziału:', `Rozdział ${newChapterNumber}`)

    if (!title) return

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/projects/${projectId}/chapters`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title,
            chapter_number: newChapterNumber,
            content: '',
            status: 'draft',
          }),
        }
      )

      if (response.ok) {
        const newChapter = await response.json()
        setChapters([...chapters, newChapter])
        setCurrentChapter(newChapter)
      }
    } catch (error) {
      console.error('Failed to create chapter:', error)
    }
  }

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60

    if (hours > 0) {
      return `${hours}h ${minutes}m`
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`
    } else {
      return `${secs}s`
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft':
        return 'text-gray-400'
      case 'in_progress':
        return 'text-blue-400'
      case 'complete':
        return 'text-green-400'
      case 'revision':
        return 'text-orange-400'
      default:
        return 'text-gray-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'complete':
        return <CheckCircle2 className="w-4 h-4" />
      case 'in_progress':
        return <Circle className="w-4 h-4 fill-current" />
      case 'revision':
        return <AlertCircle className="w-4 h-4" />
      default:
        return <Circle className="w-4 h-4" />
    }
  }

  if (!user || !accessToken || !projectId) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-400 mt-4">Ładowanie...</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`h-screen flex flex-col bg-gray-900 ${focusMode ? 'focus-mode' : ''}`}>
      {/* Top Bar */}
      {!focusMode && (
        <div className="bg-gray-800 border-b border-gray-700 px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/desktop')}
              className="flex items-center gap-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
            >
              <ChevronLeft className="w-4 h-4 text-gray-300" />
              <span className="text-sm text-gray-300">Desktop</span>
            </button>

            <div className="h-6 w-px bg-gray-700"></div>

            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <FileText className="w-6 h-6 text-purple-400" />
              Writing Studio
            </h1>
          </div>

          <div className="flex items-center gap-3">
            {/* Word Count Stats */}
            <div className="flex items-center gap-6 px-4 py-2 bg-gray-700 rounded-lg">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-green-400" />
                <span className="text-sm text-gray-300">{wordCount} słów</span>
              </div>
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-blue-400" />
                <span className="text-sm text-gray-300">{targetWords} cel</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-orange-400" />
                <span className="text-sm text-gray-300">{formatDuration(sessionDuration)}</span>
              </div>
            </div>

            {/* Auto-save Status */}
            <div className="flex items-center gap-2 px-3 py-2 bg-gray-700 rounded-lg">
              {autoSaveStatus === 'saved' ? (
                <>
                  <CheckCircle2 className="w-4 h-4 text-green-400" />
                  <span className="text-xs text-gray-300">Zapisano</span>
                </>
              ) : autoSaveStatus === 'saving' ? (
                <>
                  <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-xs text-gray-300">Zapisywanie...</span>
                </>
              ) : (
                <>
                  <Circle className="w-4 h-4 text-yellow-400" />
                  <span className="text-xs text-gray-300">Niezapisane</span>
                </>
              )}
            </div>

            {/* Actions */}
            <button
              onClick={handleManualSave}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
            >
              <Save className="w-4 h-4" />
              Zapisz
            </button>

            <button
              onClick={() => setFocusMode(!focusMode)}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            >
              {focusMode ? (
                <Eye className="w-5 h-5 text-gray-300" />
              ) : (
                <Maximize2 className="w-5 h-5 text-gray-300" />
              )}
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - Chapters List */}
        {showSidebar && !focusMode && (
          <div className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col">
            <div className="p-4 border-b border-gray-700">
              <button
                onClick={handleCreateChapter}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
              >
                <Plus className="w-4 h-4" />
                Nowy Rozdział
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {chapters.map((chapter) => (
                <button
                  key={chapter.id}
                  onClick={() => setCurrentChapter(chapter)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    currentChapter?.id === chapter.id
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-sm">
                      Rozdział {chapter.chapter_number}
                      {chapter.scene_number && ` - Scena ${chapter.scene_number}`}
                    </span>
                    <span className={getStatusColor(chapter.status)}>
                      {getStatusIcon(chapter.status)}
                    </span>
                  </div>
                  <p className="text-xs opacity-80 mb-1">{chapter.title}</p>
                  <div className="flex items-center justify-between text-xs opacity-60">
                    <span>{chapter.word_count} słów</span>
                    <span>{new Date(chapter.last_edited_at).toLocaleDateString('pl-PL')}</span>
                  </div>
                </button>
              ))}

              {chapters.length === 0 && (
                <div className="text-center py-12">
                  <Book className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400 text-sm">Brak rozdziałów</p>
                  <p className="text-gray-500 text-xs mt-1">Stwórz pierwszy rozdział</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Editor */}
        <div className="flex-1 flex flex-col">
          {currentChapter ? (
            <>
              {/* Editor Header */}
              {!focusMode && (
                <div className="px-8 py-4 bg-gray-800 border-b border-gray-700">
                  <input
                    type="text"
                    value={currentChapter.title}
                    readOnly
                    className="text-2xl font-bold text-white bg-transparent border-none focus:outline-none w-full"
                  />
                  <p className="text-sm text-gray-400 mt-1">
                    Rozdział {currentChapter.chapter_number} • {wordCount} / {targetWords} słów •{' '}
                    {Math.round((wordCount / targetWords) * 100)}% ukończone
                  </p>
                </div>
              )}

              {/* Text Editor */}
              <div className="flex-1 overflow-y-auto">
                <textarea
                  ref={editorRef}
                  value={content}
                  onChange={handleContentChange}
                  placeholder="Zacznij pisać swoją historię..."
                  className={`w-full h-full p-8 bg-gray-900 text-gray-100 focus:outline-none resize-none font-serif text-lg leading-relaxed ${
                    focusMode ? 'max-w-4xl mx-auto' : ''
                  }`}
                  style={{
                    lineHeight: '1.8',
                  }}
                  autoFocus
                />
              </div>

              {/* Progress Bar */}
              {!focusMode && (
                <div className="bg-gray-800 border-t border-gray-700 p-4">
                  <div className="flex items-center justify-between mb-2 text-sm">
                    <span className="text-gray-400">Postęp rozdziału</span>
                    <span className="text-purple-400 font-semibold">
                      {Math.min(100, Math.round((wordCount / targetWords) * 100))}%
                    </span>
                  </div>
                  <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                      style={{
                        width: `${Math.min(100, (wordCount / targetWords) * 100)}%`,
                      }}
                    />
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400 text-lg mb-2">Wybierz rozdział lub stwórz nowy</p>
                <button
                  onClick={handleCreateChapter}
                  className="flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors mx-auto"
                >
                  <Plus className="w-5 h-5" />
                  Stwórz pierwszy rozdział
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Toggle Sidebar Button */}
        {!focusMode && (
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="absolute left-80 top-1/2 -translate-y-1/2 -translate-x-1/2 p-2 bg-gray-800 border border-gray-700 rounded-full hover:bg-gray-700 transition-colors z-10"
            style={{ left: showSidebar ? '320px' : '0px' }}
          >
            {showSidebar ? (
              <ChevronLeft className="w-4 h-4 text-gray-300" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-300" />
            )}
          </button>
        )}
      </div>

      {/* Focus Mode Exit Hint */}
      {focusMode && (
        <div className="absolute top-4 right-4 bg-gray-800 bg-opacity-90 backdrop-blur-sm border border-gray-700 rounded-lg px-4 py-2 text-sm text-gray-300 flex items-center gap-2">
          <EyeOff className="w-4 h-4" />
          Tryb skupienia • Naciśnij ESC aby wyjść
        </div>
      )}
    </div>
  )
}
