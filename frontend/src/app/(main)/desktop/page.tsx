'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import {
  Layout, BookOpen, Users, BarChart3, Sparkles,
  Clock, TrendingUp, Target, Zap, Book, FileText,
  Search, Bell, Settings, Plus, Folder, Calendar,
  Activity, Award, Flame, CheckCircle2
} from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Project {
  id: number
  name: string
  description: string
  genre: string
  target_words: number
  current_words: number
  last_updated: string
}

interface WritingStats {
  today_words: number
  week_words: number
  month_words: number
  streak_days: number
  total_words: number
  chapters_completed: number
}

export default function NarrativeDesktop() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [currentProject, setCurrentProject] = useState<Project | null>(null)
  const [stats, setStats] = useState<WritingStats>({
    today_words: 0,
    week_words: 0,
    month_words: 0,
    streak_days: 0,
    total_words: 0,
    chapters_completed: 0
  })
  const [showQuickActions, setShowQuickActions] = useState(false)
  const [quickSearch, setQuickSearch] = useState('')

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/auth/login')
    }
  }, [status, router])

  useEffect(() => {
    if (session?.accessToken) {
      loadProjects()
      loadStats()
    }
  }, [session?.accessToken])

  const loadProjects = async () => {
    // Mock data - replace with real API
    setProjects([
      {
        id: 1,
        name: "Mroczna Forteca",
        description: "Fantasy o magicznej twierdzy",
        genre: "Fantasy",
        target_words: 100000,
        current_words: 45230,
        last_updated: new Date().toISOString()
      }
    ])
    setCurrentProject({
      id: 1,
      name: "Mroczna Forteca",
      description: "Fantasy o magicznej twierdzy",
      genre: "Fantasy",
      target_words: 100000,
      current_words: 45230,
      last_updated: new Date().toISOString()
    })
  }

  const loadStats = async () => {
    // Mock data - replace with real API
    setStats({
      today_words: 1250,
      week_words: 7890,
      month_words: 28450,
      streak_days: 12,
      total_words: 145230,
      chapters_completed: 8
    })
  }

  const quickActions = [
    { label: 'Nowy Rozdział', icon: FileText, action: () => router.push('/chapters/new'), shortcut: 'Ctrl+N' },
    { label: 'Biblia Fabuły', icon: Book, action: () => router.push('/story-bible'), shortcut: 'Ctrl+B' },
    { label: 'AI Asystent', icon: Sparkles, action: () => {}, shortcut: 'Ctrl+K' },
    { label: 'Statystyki', icon: BarChart3, action: () => router.push('/analytics'), shortcut: 'Ctrl+A' },
    { label: 'Projekty', icon: Folder, action: () => router.push('/projects'), shortcut: 'Ctrl+P' },
  ]

  if (status === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-indigo-900">
      {/* Top Bar */}
      <div className="bg-black bg-opacity-30 backdrop-blur-lg border-b border-white border-opacity-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            {/* Logo & Project Selector */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Layout className="h-8 w-8 text-purple-400" />
                <span className="text-2xl font-bold text-white">Narrative OS</span>
              </div>
              <div className="h-8 w-px bg-white bg-opacity-20"></div>
              <button
                onClick={() => router.push('/projects')}
                className="flex items-center space-x-2 px-4 py-2 bg-white bg-opacity-10 hover:bg-opacity-20 rounded-lg transition"
              >
                <Folder className="h-4 w-4 text-purple-300" />
                <span className="text-white font-medium">{currentProject?.name || 'Wybierz projekt'}</span>
              </button>
            </div>

            {/* Quick Actions */}
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowQuickActions(!showQuickActions)}
                className="flex items-center space-x-2 px-4 py-2 bg-white bg-opacity-10 hover:bg-opacity-20 rounded-lg transition group"
              >
                <Search className="h-4 w-4 text-purple-300 group-hover:text-purple-200" />
                <span className="text-sm text-gray-300">Szybkie akcje</span>
                <kbd className="px-2 py-1 text-xs bg-black bg-opacity-30 rounded border border-white border-opacity-20 text-gray-400">
                  Ctrl+K
                </kbd>
              </button>
              <button className="p-2 bg-white bg-opacity-10 hover:bg-opacity-20 rounded-lg transition relative">
                <Bell className="h-5 w-5 text-purple-300" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              <button className="p-2 bg-white bg-opacity-10 hover:bg-opacity-20 rounded-lg transition">
                <Settings className="h-5 w-5 text-purple-300" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Witaj, {session?.user?.email?.split('@')[0] || 'Pisarzu'}! 👋
          </h1>
          <p className="text-purple-200">
            {new Date().toLocaleDateString('pl-PL', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Today's Words */}
          <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-white bg-opacity-20 flex items-center justify-center">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <TrendingUp className="h-6 w-6 text-white opacity-50" />
            </div>
            <p className="text-sm text-white opacity-80 mb-1">Dziś napisane</p>
            <p className="text-3xl font-bold text-white">{stats.today_words.toLocaleString()}</p>
            <p className="text-xs text-white opacity-70 mt-2">słów</p>
          </div>

          {/* Streak */}
          <div className="bg-gradient-to-br from-orange-500 to-red-600 rounded-xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-white bg-opacity-20 flex items-center justify-center">
                <Flame className="h-6 w-6 text-white" />
              </div>
              <Activity className="h-6 w-6 text-white opacity-50" />
            </div>
            <p className="text-sm text-white opacity-80 mb-1">Passa</p>
            <p className="text-3xl font-bold text-white">{stats.streak_days}</p>
            <p className="text-xs text-white opacity-70 mt-2">dni z rzędu 🔥</p>
          </div>

          {/* Progress */}
          <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-white bg-opacity-20 flex items-center justify-center">
                <Target className="h-6 w-6 text-white" />
              </div>
              <BarChart3 className="h-6 w-6 text-white opacity-50" />
            </div>
            <p className="text-sm text-white opacity-80 mb-1">Postęp projektu</p>
            <p className="text-3xl font-bold text-white">
              {currentProject ? Math.round((currentProject.current_words / currentProject.target_words) * 100) : 0}%
            </p>
            <p className="text-xs text-white opacity-70 mt-2">
              {currentProject?.current_words.toLocaleString()} / {currentProject?.target_words.toLocaleString()} słów
            </p>
          </div>

          {/* Chapters */}
          <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-white bg-opacity-20 flex items-center justify-center">
                <CheckCircle2 className="h-6 w-6 text-white" />
              </div>
              <Award className="h-6 w-6 text-white opacity-50" />
            </div>
            <p className="text-sm text-white opacity-80 mb-1">Ukończone</p>
            <p className="text-3xl font-bold text-white">{stats.chapters_completed}</p>
            <p className="text-xs text-white opacity-70 mt-2">rozdziałów</p>
          </div>
        </div>

        {/* Main Widgets Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick Start Widget */}
          <div className="lg:col-span-2 bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-10">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center space-x-2">
              <Zap className="h-5 w-5 text-yellow-400" />
              <span>Szybki Start</span>
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => router.push('/chapters/new')}
                className="p-4 bg-gradient-to-br from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 rounded-lg transition group"
              >
                <FileText className="h-8 w-8 text-white mb-2" />
                <p className="text-white font-semibold">Nowy Rozdział</p>
                <p className="text-xs text-purple-200 mt-1">Rozpocznij pisanie</p>
              </button>
              <button
                onClick={() => router.push('/story-bible')}
                className="p-4 bg-gradient-to-br from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 rounded-lg transition"
              >
                <Book className="h-8 w-8 text-white mb-2" />
                <p className="text-white font-semibold">Biblia Fabuły</p>
                <p className="text-xs text-emerald-200 mt-1">Zarządzaj kanonem</p>
              </button>
              <button className="p-4 bg-gradient-to-br from-pink-500 to-rose-600 hover:from-pink-600 hover:to-rose-700 rounded-lg transition">
                <Sparkles className="h-8 w-8 text-white mb-2" />
                <p className="text-white font-semibold">AI Asystent</p>
                <p className="text-xs text-pink-200 mt-1">Generuj i analizuj</p>
              </button>
              <button
                onClick={() => router.push('/analytics')}
                className="p-4 bg-gradient-to-br from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 rounded-lg transition"
              >
                <BarChart3 className="h-8 w-8 text-white mb-2" />
                <p className="text-white font-semibold">Statystyki</p>
                <p className="text-xs text-amber-200 mt-1">Analizuj postępy</p>
              </button>
            </div>
          </div>

          {/* Recent Activity Widget */}
          <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-10">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center space-x-2">
              <Clock className="h-5 w-5 text-blue-400" />
              <span>Ostatnia Aktywność</span>
            </h2>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 rounded-full bg-green-400 mt-2 flex-shrink-0"></div>
                <div>
                  <p className="text-sm text-white">Dodano postać "Elara"</p>
                  <p className="text-xs text-gray-400">2 godziny temu</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 rounded-full bg-blue-400 mt-2 flex-shrink-0"></div>
                <div>
                  <p className="text-sm text-white">Ukończono rozdział 8</p>
                  <p className="text-xs text-gray-400">5 godzin temu</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 rounded-full bg-purple-400 mt-2 flex-shrink-0"></div>
                <div>
                  <p className="text-sm text-white">AI sprawdził spójność</p>
                  <p className="text-xs text-gray-400">wczoraj</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 rounded-full bg-amber-400 mt-2 flex-shrink-0"></div>
                <div>
                  <p className="text-sm text-white">Eksport biblii fabuły</p>
                  <p className="text-xs text-gray-400">2 dni temu</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Weekly Progress */}
        <div className="mt-6 bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-10">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center space-x-2">
            <Calendar className="h-5 w-5 text-purple-400" />
            <span>Aktywność w tym tygodniu</span>
          </h2>
          <div className="flex items-end justify-between space-x-2 h-48">
            {['Pon', 'Wt', 'Śr', 'Czw', 'Pt', 'Sob', 'Niedz'].map((day, idx) => {
              const height = Math.random() * 100
              return (
                <div key={day} className="flex-1 flex flex-col items-center">
                  <div className="w-full bg-gradient-to-t from-purple-600 to-indigo-500 rounded-t-lg transition-all hover:from-purple-500 hover:to-indigo-400 cursor-pointer"
                    style={{ height: `${height}%` }}
                  ></div>
                  <p className="text-xs text-gray-400 mt-2">{day}</p>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Quick Actions Modal */}
      {showQuickActions && (
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-start justify-center pt-32 z-50"
          onClick={() => setShowQuickActions(false)}
        >
          <div className="bg-gray-900 rounded-xl shadow-2xl w-full max-w-2xl border border-gray-700"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-4 border-b border-gray-700">
              <input
                type="text"
                value={quickSearch}
                onChange={(e) => setQuickSearch(e.target.value)}
                placeholder="Szukaj akcji, rozdziałów, postaci..."
                className="w-full bg-gray-800 text-white px-4 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                autoFocus
              />
            </div>
            <div className="p-2 max-h-96 overflow-y-auto">
              {quickActions.map((action, idx) => {
                const Icon = action.icon
                return (
                  <button
                    key={idx}
                    onClick={() => {
                      action.action()
                      setShowQuickActions(false)
                    }}
                    className="w-full flex items-center justify-between p-3 hover:bg-gray-800 rounded-lg transition group"
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className="h-5 w-5 text-purple-400 group-hover:text-purple-300" />
                      <span className="text-white">{action.label}</span>
                    </div>
                    <kbd className="px-2 py-1 text-xs bg-gray-800 rounded border border-gray-700 text-gray-400">
                      {action.shortcut}
                    </kbd>
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
