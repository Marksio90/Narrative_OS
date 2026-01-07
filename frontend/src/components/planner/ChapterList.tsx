'use client'

import { useState } from 'react'
import { Chapter, Scene } from '@/types/planner'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import Button from '@/components/Button'
import { Plus, ChevronDown, ChevronRight } from 'lucide-react'
import ChapterForm from './ChapterForm'
import SceneCard from './SceneCard'

interface ChapterListProps {
  projectId: number
  chapters: Chapter[]
  scenesByChapter: Record<number, Scene[]>
  onUpdate: () => void
}

export default function ChapterList({
  projectId,
  chapters,
  scenesByChapter,
  onUpdate,
}: ChapterListProps) {
  const [showForm, setShowForm] = useState(false)
  const [expandedChapters, setExpandedChapters] = useState<Set<number>>(new Set())

  const toggleChapter = (chapterId: number) => {
    const newExpanded = new Set(expandedChapters)
    if (newExpanded.has(chapterId)) {
      newExpanded.delete(chapterId)
    } else {
      newExpanded.add(chapterId)
    }
    setExpandedChapters(newExpanded)
  }

  const handleFormClose = () => {
    setShowForm(false)
    onUpdate()
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Chapters ({chapters.length})</CardTitle>
          <Button onClick={() => setShowForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Chapter
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {showForm && (
          <div className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
            <ChapterForm
              projectId={projectId}
              nextChapterNumber={(chapters[chapters.length - 1]?.chapter_number || 0) + 1}
              onClose={handleFormClose}
            />
          </div>
        )}

        {chapters.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            No chapters yet. Add your first chapter to start planning.
          </div>
        ) : (
          <div className="space-y-3">
            {chapters.map((chapter) => {
              const scenes = scenesByChapter[chapter.id] || []
              const isExpanded = expandedChapters.has(chapter.id)

              return (
                <div
                  key={chapter.id}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg"
                >
                  <button
                    onClick={() => toggleChapter(chapter.id)}
                    className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      {isExpanded ? (
                        <ChevronDown className="h-5 w-5 text-gray-500" />
                      ) : (
                        <ChevronRight className="h-5 w-5 text-gray-500" />
                      )}
                      <div className="text-left">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          Chapter {chapter.chapter_number}
                          {chapter.title && `: ${chapter.title}`}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {chapter.summary}
                        </p>
                        {scenes.length > 0 && (
                          <p className="text-xs text-gray-500 mt-1">
                            {scenes.length} scene{scenes.length !== 1 ? 's' : ''}
                          </p>
                        )}
                      </div>
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="px-4 pb-4 space-y-2">
                      <div className="flex items-center justify-between mb-3 pt-2 border-t border-gray-200 dark:border-gray-700">
                        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Scene Cards
                        </h4>
                      </div>

                      {scenes.length === 0 ? (
                        <p className="text-sm text-gray-500 text-center py-4">
                          No scenes yet. Scene creation coming soon...
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {scenes.map((scene) => (
                            <SceneCard key={scene.id} scene={scene} />
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
