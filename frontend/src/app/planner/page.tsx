'use client'

import { useState, useEffect } from 'react'
import Layout from '@/components/Layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import { ProjectStructure } from '@/types/planner'
import api from '@/lib/api'
import BookArcView from '@/components/planner/BookArcView'
import ChapterList from '@/components/planner/ChapterList'

export default function PlannerPage() {
  const [projectId] = useState(1) // TODO: Get from context/auth
  const [structure, setStructure] = useState<ProjectStructure | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchStructure = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/api/planner/structure`, {
        params: { project_id: projectId },
      })
      setStructure(response.data)
    } catch (error) {
      console.error('Failed to fetch project structure:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStructure()
  }, [projectId])

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Planner
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Structure your story with 3-level planning: Book Arc → Chapters → Scene Cards
          </p>
        </div>

        {loading ? (
          <Card>
            <CardContent>
              <div className="text-center py-12">Loading project structure...</div>
            </CardContent>
          </Card>
        ) : (
          <>
            <BookArcView
              projectId={projectId}
              bookArc={structure?.book_arc}
              onUpdate={fetchStructure}
            />

            <ChapterList
              projectId={projectId}
              chapters={structure?.chapters || []}
              scenesByChapter={structure?.scenes_by_chapter || {}}
              onUpdate={fetchStructure}
            />
          </>
        )}
      </div>
    </Layout>
  )
}
