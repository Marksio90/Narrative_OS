'use client'

import { useState, useEffect } from 'react'
import Layout from '@/components/Layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import { Promise } from '@/types/canon'
import api from '@/lib/api'
import { Target, AlertCircle, CheckCircle, XCircle, Clock } from 'lucide-react'

export default function PromisesPage() {
  const [projectId] = useState(1) // TODO: Get from context/auth
  const [promises, setPromises] = useState<Promise[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'open' | 'fulfilled' | 'abandoned'>('all')

  const fetchPromises = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/api/promises/promise`, {
        params: { project_id: projectId },
      })
      setPromises(response.data)
    } catch (error) {
      console.error('Failed to fetch promises:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchPromises()
  }, [projectId])

  const filteredPromises = promises.filter((p) => {
    if (filter === 'all') return true
    return p.status === filter
  })

  const stats = {
    total: promises.length,
    open: promises.filter((p) => p.status === 'open').length,
    fulfilled: promises.filter((p) => p.status === 'fulfilled').length,
    abandoned: promises.filter((p) => p.status === 'abandoned').length,
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open':
        return <Clock className="h-5 w-5 text-blue-600" />
      case 'fulfilled':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'abandoned':
        return <XCircle className="h-5 w-5 text-red-600" />
      default:
        return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'border-blue-300 bg-blue-50 dark:border-blue-800 dark:bg-blue-950'
      case 'fulfilled':
        return 'border-green-300 bg-green-50 dark:border-green-800 dark:bg-green-950'
      case 'abandoned':
        return 'border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950'
      default:
        return ''
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Promise Ledger
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Track narrative promises and payoffs across your story
          </p>
        </div>

        <div className="grid md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {stats.total}
                  </p>
                </div>
                <Target className="h-8 w-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Open</p>
                  <p className="text-2xl font-bold text-blue-600">{stats.open}</p>
                </div>
                <Clock className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Fulfilled</p>
                  <p className="text-2xl font-bold text-green-600">
                    {stats.fulfilled}
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Abandoned</p>
                  <p className="text-2xl font-bold text-red-600">
                    {stats.abandoned}
                  </p>
                </div>
                <XCircle className="h-8 w-8 text-red-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Promises ({filteredPromises.length})</CardTitle>
              <div className="flex space-x-2">
                <button
                  onClick={() => setFilter('all')}
                  className={`px-3 py-1 rounded text-sm ${
                    filter === 'all'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                  }`}
                >
                  All
                </button>
                <button
                  onClick={() => setFilter('open')}
                  className={`px-3 py-1 rounded text-sm ${
                    filter === 'open'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                  }`}
                >
                  Open
                </button>
                <button
                  onClick={() => setFilter('fulfilled')}
                  className={`px-3 py-1 rounded text-sm ${
                    filter === 'fulfilled'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                  }`}
                >
                  Fulfilled
                </button>
                <button
                  onClick={() => setFilter('abandoned')}
                  className={`px-3 py-1 rounded text-sm ${
                    filter === 'abandoned'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                  }`}
                >
                  Abandoned
                </button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-center py-12">Loading promises...</div>
            ) : filteredPromises.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                No promises found. Promises are automatically detected during prose generation.
              </div>
            ) : (
              <div className="space-y-3">
                {filteredPromises.map((promise) => (
                  <div
                    key={promise.id}
                    className={`border rounded-lg p-4 ${getStatusColor(promise.status)}`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          {getStatusIcon(promise.status)}
                          <span className="text-xs px-2 py-1 rounded-full bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 uppercase font-medium">
                            {promise.status}
                          </span>
                          <span className="text-xs text-gray-600 dark:text-gray-400">
                            Ch. {promise.chapter_introduced}
                            {promise.payoff_deadline &&
                              ` → Deadline: Ch. ${promise.payoff_deadline}`}
                          </span>
                          {promise.payoff_chapter && (
                            <span className="text-xs text-green-600 dark:text-green-400">
                              Payoff: Ch. {promise.payoff_chapter}
                            </span>
                          )}
                        </div>

                        <div className="space-y-2">
                          <div>
                            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                              Setup:
                            </h4>
                            <p className="text-sm text-gray-900 dark:text-white">
                              {promise.setup}
                            </p>
                          </div>

                          <div>
                            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                              Required Payoff:
                            </h4>
                            <p className="text-sm text-gray-900 dark:text-white">
                              {promise.payoff_required}
                            </p>
                          </div>

                          <div className="flex items-center space-x-2 pt-2">
                            <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full"
                                style={{ width: `${promise.confidence * 100}%` }}
                              />
                            </div>
                            <span className="text-xs text-gray-600 dark:text-gray-400">
                              {Math.round(promise.confidence * 100)}% confidence
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  )
}
