/**
 * Project Export Page
 * Dedicated page for exporting manuscripts
 */
'use client'

import { useState } from 'react'
import { Download, ArrowLeft, FileText, BookOpen, FileType, Info } from 'lucide-react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import ExportModal from '@/components/ExportModal'

export default function ProjectExportPage() {
  const params = useParams()
  const projectId = parseInt(params.id as string)
  const [isModalOpen, setIsModalOpen] = useState(false)

  // Mock project data - in production, fetch from API
  const project = {
    id: projectId,
    title: 'The Archive Chronicles',
    genre: 'Fantasy',
    chapterCount: 12,
    wordCount: 85000,
    estimatedPages: 340,
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back button */}
      <Link
        href={`/projects/${projectId}`}
        className="inline-flex items-center space-x-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-6 transition"
      >
        <ArrowLeft className="h-4 w-4" />
        <span>Powrót do Projektu</span>
      </Link>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Eksportuj Manuskrypt
        </h1>
        <p className="text-gray-600 dark:text-gray-400">{project.title}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Rozdziały</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {project.chapterCount}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Słowa</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {project.wordCount.toLocaleString()}
          </p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Szac. Strony</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">
            {project.estimatedPages}
          </p>
        </div>
      </div>

      {/* Export formats */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Dostępne Formaty Eksportu
        </h2>

        <div className="space-y-4">
          {/* DOCX */}
          <div className="flex items-start p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-700 transition">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg mr-4">
              <FileText className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                Microsoft Word (.docx)
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Edytowalny dokument z profesjonalnym formatowaniem manuskryptu
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                  Edytowalny
                </span>
                <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                  Spis Treści
                </span>
                <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                  Standardowy Format
                </span>
              </div>
            </div>
          </div>

          {/* EPUB */}
          <div className="flex items-start p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-green-300 dark:hover:border-green-700 transition">
            <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg mr-4">
              <BookOpen className="h-6 w-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                EPUB (.epub)
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Format e-booka kompatybilny ze wszystkimi głównymi czytnikami
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                  Czytniki
                </span>
                <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                  Responsywny
                </span>
                <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                  Menu Nawigacji
                </span>
              </div>
            </div>
          </div>

          {/* PDF */}
          <div className="flex items-start p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-red-300 dark:hover:border-red-700 transition">
            <div className="p-3 bg-red-100 dark:bg-red-900/30 rounded-lg mr-4">
              <FileType className="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                PDF (.pdf)
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Uniwersalny format, idealny do drukowania i archiwizacji
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                  Gotowy do druku
                </span>
                <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                  Numery Stron
                </span>
                <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">
                  Stały Układ
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Info box */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6 flex items-start space-x-3">
        <Info className="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" />
        <div className="flex-1">
          <p className="text-sm text-blue-900 dark:text-blue-200">
            Wszystkie eksporty zawierają stronę tytułową, organizację rozdziałów i profesjonalne formatowanie.
            Możesz dostosować opcje takie jak prolog, epilog i spis treści.
          </p>
        </div>
      </div>

      {/* Export button */}
      <button
        onClick={() => setIsModalOpen(true)}
        className="w-full flex items-center justify-center space-x-2 px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition font-medium text-lg shadow-lg"
      >
        <Download className="h-5 w-5" />
        <span>Eksportuj Manuskrypt</span>
      </button>

      {/* Export Modal */}
      <ExportModal
        projectId={projectId}
        projectTitle={project.title}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  )
}
