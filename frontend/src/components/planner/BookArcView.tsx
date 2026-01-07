'use client'

import { useState } from 'react'
import { BookArc } from '@/types/planner'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import Button from '@/components/Button'
import { Edit2, Plus } from 'lucide-react'
import BookArcForm from './BookArcForm'

interface BookArcViewProps {
  projectId: number
  bookArc?: BookArc
  onUpdate: () => void
}

export default function BookArcView({ projectId, bookArc, onUpdate }: BookArcViewProps) {
  const [showForm, setShowForm] = useState(false)

  const handleFormClose = () => {
    setShowForm(false)
    onUpdate()
  }

  if (showForm) {
    return (
      <Card>
        <CardContent className="pt-6">
          <BookArcForm
            projectId={projectId}
            bookArc={bookArc}
            onClose={handleFormClose}
          />
        </CardContent>
      </Card>
    )
  }

  if (!bookArc) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Book Arc</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              No book arc defined yet. Create your story structure first.
            </p>
            <Button onClick={() => setShowForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Book Arc
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Book Arc</CardTitle>
          <Button variant="ghost" size="sm" onClick={() => setShowForm(true)}>
            <Edit2 className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Premise
            </h4>
            <p className="text-gray-900 dark:text-white mt-1">{bookArc.premise}</p>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Protagonist Goal
            </h4>
            <p className="text-gray-900 dark:text-white mt-1">
              {bookArc.protagonist_goal}
            </p>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Central Conflict
            </h4>
            <p className="text-gray-900 dark:text-white mt-1">
              {bookArc.central_conflict}
            </p>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Stakes
            </h4>
            <p className="text-gray-900 dark:text-white mt-1">{bookArc.stakes}</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Act 1 End
              </h4>
              <p className="text-lg font-semibold text-blue-600">
                Ch. {bookArc.act1_end}
              </p>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Midpoint
              </h4>
              <p className="text-lg font-semibold text-blue-600">
                Ch. {bookArc.midpoint}
              </p>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Act 2 End
              </h4>
              <p className="text-lg font-semibold text-blue-600">
                Ch. {bookArc.act2_end}
              </p>
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Climax
              </h4>
              <p className="text-lg font-semibold text-blue-600">
                Ch. {bookArc.climax}
              </p>
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Resolution
            </h4>
            <p className="text-gray-900 dark:text-white mt-1">
              {bookArc.resolution}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
