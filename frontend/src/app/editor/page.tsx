'use client'

import { useState } from 'react'
import Layout from '@/components/Layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import Button from '@/components/Button'
import Input from '@/components/Input'
import { FileEdit } from 'lucide-react'
import api from '@/lib/api'
import { SceneDraft, QCReport } from '@/types/draft'

export default function EditorPage() {
  const [projectId] = useState(1) // TODO: Get from context/auth
  const [sceneId, setSceneId] = useState('')
  const [loading, setLoading] = useState(false)
  const [draft, setDraft] = useState<SceneDraft | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    if (!sceneId) return

    setLoading(true)
    setError(null)
    setDraft(null)

    try {
      const response = await api.post('/api/draft/generate-scene', {
        scene_id: parseInt(sceneId),
        canon_context: {},
        style_profile: {},
        auto_validate: true,
      })
      setDraft(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate scene')
      console.error('Failed to generate scene:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
        return 'text-green-600'
      case 'needs_regeneration':
        return 'text-orange-600'
      case 'rejected':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  const getIssueColor = (type: string) => {
    switch (type) {
      case 'blocker':
        return 'border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950'
      case 'warning':
        return 'border-orange-300 bg-orange-50 dark:border-orange-800 dark:bg-orange-950'
      case 'suggestion':
        return 'border-blue-300 bg-blue-50 dark:border-blue-800 dark:bg-blue-950'
      default:
        return ''
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Editor
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Generate prose scene-by-scene with multi-agent quality control
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Generate Scene</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex space-x-3">
              <Input
                type="number"
                placeholder="Scene ID"
                value={sceneId}
                onChange={(e) => setSceneId(e.target.value)}
                className="flex-1"
              />
              <Button onClick={handleGenerate} disabled={loading || !sceneId}>
                <FileEdit className="h-4 w-4 mr-2" />
                {loading ? 'Generating...' : 'Generate'}
              </Button>
            </div>

            {error && (
              <div className="mt-4 p-4 border border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950 rounded-lg">
                <p className="text-red-800 dark:text-red-200">{error}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {draft && (
          <>
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Generated Prose</CardTitle>
                  <span className={`text-sm font-medium ${getStatusColor(draft.status)}`}>
                    Status: {draft.status.toUpperCase()}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="prose dark:prose-invert max-w-none">
                  <div className="whitespace-pre-wrap font-serif text-base leading-relaxed">
                    {draft.prose}
                  </div>
                </div>
              </CardContent>
            </Card>

            {draft.qc_report && (
              <Card>
                <CardHeader>
                  <CardTitle>Quality Control Report</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          Overall Score
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {draft.qc_report.passed ? 'PASSED' : 'FAILED'}
                        </p>
                      </div>
                      <div className="text-3xl font-bold text-blue-600">
                        {draft.qc_report.score}/100
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-4">
                      <div className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Continuity
                        </h4>
                        <p className="text-xl font-semibold text-gray-900 dark:text-white">
                          {draft.qc_report.breakdown.continuity}
                        </p>
                      </div>
                      <div className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Character
                        </h4>
                        <p className="text-xl font-semibold text-gray-900 dark:text-white">
                          {draft.qc_report.breakdown.character}
                        </p>
                      </div>
                      <div className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Plot
                        </h4>
                        <p className="text-xl font-semibold text-gray-900 dark:text-white">
                          {draft.qc_report.breakdown.plot}
                        </p>
                      </div>
                    </div>

                    {draft.qc_report.issues.length > 0 && (
                      <div className="space-y-2">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          Issues ({draft.qc_report.issues.length})
                        </h3>
                        {draft.qc_report.issues.map((issue, idx) => (
                          <div
                            key={idx}
                            className={`border rounded-lg p-4 ${getIssueColor(issue.type)}`}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-2">
                                  <span className="text-xs px-2 py-1 rounded-full bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 uppercase font-medium">
                                    {issue.type}
                                  </span>
                                  <span className="text-xs text-gray-600 dark:text-gray-400">
                                    {issue.editor}
                                  </span>
                                </div>
                                <p className="text-sm text-gray-900 dark:text-white mb-2">
                                  {issue.message}
                                </p>
                                {issue.quote && (
                                  <div className="p-2 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700 mb-2">
                                    <p className="text-xs font-mono text-gray-700 dark:text-gray-300">
                                      {issue.quote}
                                    </p>
                                  </div>
                                )}
                                {issue.suggestion && (
                                  <p className="text-sm text-gray-700 dark:text-gray-300">
                                    <span className="font-medium">Suggestion:</span>{' '}
                                    {issue.suggestion}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {draft.extracted_facts && draft.extracted_facts.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Extracted Facts ({draft.extracted_facts.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {draft.extracted_facts.map((fact, idx) => (
                      <div
                        key={idx}
                        className="border border-gray-200 dark:border-gray-700 rounded-lg p-3"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className="text-xs px-2 py-1 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                                {fact.category}
                              </span>
                              <span className="text-xs text-gray-500">
                                {Math.round(fact.confidence * 100)}% confidence
                              </span>
                            </div>
                            <p className="text-sm text-gray-900 dark:text-white">
                              {fact.fact}
                            </p>
                            {fact.source_quote && (
                              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 italic">
                                "{fact.source_quote}"
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>
    </Layout>
  )
}
