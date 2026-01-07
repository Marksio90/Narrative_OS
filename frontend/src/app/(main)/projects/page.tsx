/**
 * Projects List Page
 * View all user's projects with export access
 */
'use client'

import Link from 'next/link'
import { BookOpen, FileEdit, Download, Plus } from 'lucide-react'

export default function ProjectsPage() {
  // Mock projects - in production, fetch from API
  const projects = [
    {
      id: 1,
      title: 'The Archive Chronicles',
      genre: 'Fantasy',
      status: 'in_progress',
      wordCount: 85000,
      chapterCount: 12,
      lastUpdated: '2026-01-06',
    },
    {
      id: 2,
      title: 'Silicon Dreams',
      genre: 'Sci-Fi',
      status: 'draft',
      wordCount: 45000,
      chapterCount: 7,
      lastUpdated: '2026-01-05',
    },
  ]

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            My Projects
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage your manuscripts and export them to various formats
          </p>
        </div>
        <button className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
          <Plus className="h-5 w-5" />
          <span>New Project</span>
        </button>
      </div>

      {/* Projects grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {projects.map((project) => (
          <div
            key={project.id}
            className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 hover:border-blue-300 dark:hover:border-blue-700 transition"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <BookOpen className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {project.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {project.genre}
                  </p>
                </div>
              </div>
              <span
                className={`px-2 py-1 rounded text-xs font-medium ${
                  project.status === 'in_progress'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                }`}
              >
                {project.status === 'in_progress' ? 'In Progress' : 'Draft'}
              </span>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-4 mb-4 py-4 border-t border-b border-gray-200 dark:border-gray-700">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Chapters</p>
                <p className="text-xl font-bold text-gray-900 dark:text-white">
                  {project.chapterCount}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Words</p>
                <p className="text-xl font-bold text-gray-900 dark:text-white">
                  {project.wordCount.toLocaleString()}
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-3">
              <Link
                href={`/projects/${project.id}/edit`}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
              >
                <FileEdit className="h-4 w-4" />
                <span>Edit</span>
              </Link>
              <Link
                href={`/projects/${project.id}/export`}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <Download className="h-4 w-4" />
                <span>Export</span>
              </Link>
            </div>

            {/* Last updated */}
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-4">
              Last updated: {new Date(project.lastUpdated).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>

      {/* Empty state if no projects */}
      {projects.length === 0 && (
        <div className="text-center py-16 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <BookOpen className="h-16 w-16 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            No projects yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Create your first project to start writing
          </p>
          <button className="inline-flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
            <Plus className="h-5 w-5" />
            <span>Create Project</span>
          </button>
        </div>
      )}
    </div>
  )
}
