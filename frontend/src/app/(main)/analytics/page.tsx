'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import {
  BarChart3,
  TrendingUp,
  Calendar,
  Clock,
  Target,
  Flame,
  Award,
  Zap,
  BookOpen,
  Users,
  MapPin,
  FileText,
  Activity,
  CheckCircle2,
  ChevronLeft,
  Download,
  Filter,
} from 'lucide-react'

interface WritingStats {
  today_words: number
  week_words: number
  month_words: number
  year_words: number
  streak_days: number
  total_words: number
  chapters_completed: number
  avg_words_per_day: number
  best_day_words: number
  total_sessions: number
}

interface DailyActivity {
  date: string
  words_written: number
  minutes_spent: number
  chapters_worked: number
  ai_generations: number
}

interface Session {
  id: number
  started_at: string
  ended_at: string
  duration_seconds: number
  words_added: number
  net_words: number
}

export default function AnalyticsPage() {
  const { user, accessToken } = useAuth()
  const router = useRouter()
  const t = useTranslations('analytics')
  const tCommon = useTranslations('common')

  const [projectId, setProjectId] = useState<number | null>(null)
  const [stats, setStats] = useState<WritingStats | null>(null)
  const [dailyActivity, setDailyActivity] = useState<DailyActivity[]>([])
  const [sessions, setSessions] = useState<Session[]>([])
  const [timeRange, setTimeRange] = useState<'week' | 'month' | 'year'>('week')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) {
      router.push('/login')
      return
    }

    const savedProjectId = localStorage.getItem('currentProjectId')
    if (savedProjectId) {
      setProjectId(parseInt(savedProjectId))
    } else {
      router.push('/projects')
    }
  }, [user, router])

  useEffect(() => {
    if (projectId && accessToken) {
      loadAnalytics()
    }
  }, [projectId, accessToken, timeRange])

  const loadAnalytics = async () => {
    setLoading(true)

    try {
      // Load writing stats
      const statsResponse = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/desktop/stats?project_id=${projectId}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      )

      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData)
      }

      // Mock daily activity for now
      setDailyActivity(generateMockDailyActivity(timeRange))

      // Mock sessions
      setSessions(generateMockSessions())
    } catch (error) {
      console.error('Failed to load analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateMockDailyActivity = (range: 'week' | 'month' | 'year'): DailyActivity[] => {
    const days = range === 'week' ? 7 : range === 'month' ? 30 : 365
    const activity: DailyActivity[] = []

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)

      activity.push({
        date: date.toISOString().split('T')[0],
        words_written: Math.floor(Math.random() * 2000) + 500,
        minutes_spent: Math.floor(Math.random() * 120) + 30,
        chapters_worked: Math.random() > 0.5 ? 1 : 0,
        ai_generations: Math.floor(Math.random() * 5),
      })
    }

    return activity
  }

  const generateMockSessions = (): Session[] => {
    const sessions: Session[] = []
    for (let i = 0; i < 10; i++) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      const started = date.toISOString()
      date.setMinutes(date.getMinutes() + Math.floor(Math.random() * 120) + 30)
      const ended = date.toISOString()

      sessions.push({
        id: i + 1,
        started_at: started,
        ended_at: ended,
        duration_seconds: Math.floor(Math.random() * 7200) + 1800,
        words_added: Math.floor(Math.random() * 2000) + 500,
        net_words: Math.floor(Math.random() * 1800) + 400,
      })
    }
    return sessions
  }

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)

    if (hours > 0) {
      return `${hours}h ${minutes}m`
    } else {
      return `${minutes}m`
    }
  }

  const getMaxWords = () => {
    return Math.max(...dailyActivity.map((d) => d.words_written))
  }

  if (loading || !stats) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-400 mt-4">{tCommon('loading')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <button
              onClick={() => router.push('/desktop')}
              className="flex items-center gap-2 px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors mb-4"
            >
              <ChevronLeft className="w-4 h-4 text-gray-300" />
              <span className="text-sm text-gray-300">{t('backToDesktop')}</span>
            </button>

            <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
              <BarChart3 className="w-10 h-10 text-purple-400" />
              {t('title')}
            </h1>
            <p className="text-gray-400">{t('subtitle')}</p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as any)}
              className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-purple-500"
            >
              <option value="week">{t('timeRange.week')}</option>
              <option value="month">{t('timeRange.month')}</option>
              <option value="year">{t('timeRange.year')}</option>
            </select>

            <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors">
              <Download className="w-4 h-4" />
              {tCommon('export')}
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Words */}
          <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-white bg-opacity-20 flex items-center justify-center">
                <FileText className="h-6 w-6 text-white" />
              </div>
              <TrendingUp className="h-6 w-6 text-white opacity-50" />
            </div>
            <p className="text-sm text-white opacity-80 mb-1">{t('metrics.totalWords')}</p>
            <p className="text-3xl font-bold text-white">{stats.total_words.toLocaleString()}</p>
            <p className="text-xs text-white opacity-70 mt-2">
              +{stats.month_words.toLocaleString()} {tCommon('thisMonth')}
            </p>
          </div>

          {/* Streak */}
          <div className="bg-gradient-to-br from-orange-500 to-red-600 rounded-xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-white bg-opacity-20 flex items-center justify-center">
                <Flame className="h-6 w-6 text-white" />
              </div>
              <Activity className="h-6 w-6 text-white opacity-50" />
            </div>
            <p className="text-sm text-white opacity-80 mb-1">{t('metrics.currentStreak')}</p>
            <p className="text-3xl font-bold text-white">{stats.streak_days}</p>
            <p className="text-xs text-white opacity-70 mt-2">{tCommon('daysInRow')}</p>
          </div>

          {/* Average */}
          <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-white bg-opacity-20 flex items-center justify-center">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <BarChart3 className="h-6 w-6 text-white opacity-50" />
            </div>
            <p className="text-sm text-white opacity-80 mb-1">{t('metrics.dailyAverage')}</p>
            <p className="text-3xl font-bold text-white">{stats.avg_words_per_day.toLocaleString()}</p>
            <p className="text-xs text-white opacity-70 mt-2">{tCommon('wordsPerDay')}</p>
          </div>

          {/* Best Day */}
          <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 rounded-lg bg-white bg-opacity-20 flex items-center justify-center">
                <Award className="h-6 w-6 text-white" />
              </div>
              <CheckCircle2 className="h-6 w-6 text-white opacity-50" />
            </div>
            <p className="text-sm text-white opacity-80 mb-1">{t('metrics.bestDay')}</p>
            <p className="text-3xl font-bold text-white">{stats.best_day_words.toLocaleString()}</p>
            <p className="text-xs text-white opacity-70 mt-2">{tCommon('wordsInOneDay')}</p>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Daily Words Chart */}
          <div className="lg:col-span-2 bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-xl p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-purple-400" />
              {t('writingActivity')}
            </h2>

            <div className="flex items-end justify-between space-x-2 h-64">
              {dailyActivity.map((day, idx) => {
                const height = (day.words_written / getMaxWords()) * 100
                const date = new Date(day.date)
                const dayName = date.toLocaleDateString('pl-PL', { weekday: 'short' })

                return (
                  <div key={idx} className="flex-1 flex flex-col items-center group">
                    <div className="relative w-full mb-2">
                      {/* Tooltip */}
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                        <div className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-xs text-white whitespace-nowrap shadow-xl">
                          <p className="font-bold">{day.words_written} {tCommon('words')}</p>
                          <p className="text-gray-400">{day.minutes_spent} {tCommon('minutes')}</p>
                          <p className="text-gray-400">{date.toLocaleDateString('pl-PL')}</p>
                        </div>
                      </div>

                      {/* Bar */}
                      <div
                        className="w-full bg-gradient-to-t from-purple-600 to-indigo-500 rounded-t-lg transition-all hover:from-purple-500 hover:to-indigo-400 cursor-pointer"
                        style={{ height: `${Math.max(height, 5)}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-gray-400">{timeRange === 'week' ? dayName : date.getDate()}</p>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Session Summary */}
          <div className="bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-xl p-6 border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-400" />
              {t('sessionsOverview')}
            </h2>

            <div className="space-y-4">
              <div className="p-4 bg-gray-700 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">{t('totalSessions')}</p>
                <p className="text-2xl font-bold text-white">{stats.total_sessions}</p>
              </div>

              <div className="p-4 bg-gray-700 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">{tCommon('completedChapters')}</p>
                <p className="text-2xl font-bold text-green-400">{stats.chapters_completed}</p>
              </div>

              <div className="p-4 bg-gray-700 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">{tCommon('thisWeek')}</p>
                <p className="text-2xl font-bold text-purple-400">{stats.week_words.toLocaleString()}</p>
                <p className="text-xs text-gray-400 mt-1">{tCommon('words')}</p>
              </div>

              <div className="p-4 bg-gray-700 rounded-lg">
                <p className="text-sm text-gray-400 mb-1">{tCommon('thisMonth')}</p>
                <p className="text-2xl font-bold text-blue-400">{stats.month_words.toLocaleString()}</p>
                <p className="text-xs text-gray-400 mt-1">{tCommon('words')}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Sessions */}
        <div className="bg-gray-800 bg-opacity-50 backdrop-blur-lg rounded-xl p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-green-400" />
            {t('recentSessions')}
          </h2>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left text-sm font-semibold text-gray-400 pb-3">{tCommon('date')}</th>
                  <th className="text-left text-sm font-semibold text-gray-400 pb-3">{t('duration')}</th>
                  <th className="text-left text-sm font-semibold text-gray-400 pb-3">{t('wordsWritten')}</th>
                  <th className="text-left text-sm font-semibold text-gray-400 pb-3">{t('netWords')}</th>
                  <th className="text-left text-sm font-semibold text-gray-400 pb-3">{t('productivity')}</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((session) => {
                  const wordsPerHour = Math.round(
                    (session.net_words / session.duration_seconds) * 3600
                  )

                  return (
                    <tr key={session.id} className="border-b border-gray-700 hover:bg-gray-700 transition-colors">
                      <td className="py-3 text-sm text-gray-300">
                        {new Date(session.started_at).toLocaleDateString('pl-PL', {
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </td>
                      <td className="py-3 text-sm text-gray-300">
                        {formatDuration(session.duration_seconds)}
                      </td>
                      <td className="py-3 text-sm text-green-400 font-semibold">
                        +{session.words_added}
                      </td>
                      <td className="py-3 text-sm text-blue-400 font-semibold">
                        {session.net_words}
                      </td>
                      <td className="py-3 text-sm text-purple-400 font-semibold">
                        {wordsPerHour}/h
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
