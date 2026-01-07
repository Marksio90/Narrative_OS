'use client'

import { Scene } from '@/types/planner'
import { ArrowRight } from 'lucide-react'

interface SceneCardProps {
  scene: Scene
}

export default function SceneCard({ scene }: SceneCardProps) {
  return (
    <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-sm font-semibold text-gray-900 dark:text-white">
          Scene {scene.scene_number}
        </h4>
        <div className="flex items-center space-x-2 text-xs">
          <span className="px-2 py-1 rounded bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
            {scene.entering_value}
          </span>
          <ArrowRight className="h-3 w-3 text-gray-400" />
          <span className="px-2 py-1 rounded bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300">
            {scene.exiting_value}
          </span>
        </div>
      </div>

      <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
        <span className="font-medium">Goal:</span> {scene.goal}
      </p>

      {scene.conflict && (
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          <span className="font-medium">Conflict:</span> {scene.conflict}
        </p>
      )}

      <p className="text-sm text-gray-600 dark:text-gray-400">
        <span className="font-medium">Change:</span> {scene.what_changes}
      </p>

      {scene.participants && scene.participants.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {scene.participants.map((participant, idx) => (
            <span
              key={idx}
              className="text-xs px-2 py-1 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
            >
              {participant}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
