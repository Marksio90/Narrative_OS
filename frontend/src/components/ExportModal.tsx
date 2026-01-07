/**
 * Export Modal Component
 * Beautiful UI for exporting manuscripts to DOCX, EPUB, PDF
 */
'use client'

import { useState } from 'react'
import { useSession } from 'next-auth/react'
import { Download, FileText, BookOpen, FileType, X, Loader2, Check } from 'lucide-react'
import * as Dialog from '@radix-ui/react-dialog'

interface ExportModalProps {
  projectId: number
  projectTitle: string
  isOpen: boolean
  onClose: () => void
}

type ExportFormat = 'docx' | 'epub' | 'pdf'

interface FormatOption {
  id: ExportFormat
  name: string
  description: string
  icon: any
  color: string
  features: string[]
}

const formatOptions: FormatOption[] = [
  {
    id: 'docx',
    name: 'Microsoft Word',
    description: 'Editable document, perfect for revisions',
    icon: FileText,
    color: 'blue',
    features: ['Editable', 'Table of Contents', 'Professional Format'],
  },
  {
    id: 'epub',
    name: 'EPUB',
    description: 'E-book format for all readers',
    icon: BookOpen,
    color: 'green',
    features: ['E-readers', 'Responsive', 'Cover Support'],
  },
  {
    id: 'pdf',
    name: 'PDF',
    description: 'Print-ready, universal format',
    icon: FileType,
    color: 'red',
    features: ['Print-ready', 'Fixed Layout', 'Page Numbers'],
  },
]

export default function ExportModal({
  projectId,
  projectTitle,
  isOpen,
  onClose,
}: ExportModalProps) {
  const { data: session } = useSession()
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('docx')
  const [includePrologue, setIncludePrologue] = useState(true)
  const [includeEpilogue, setIncludeEpilogue] = useState(true)
  const [includeToc, setIncludeToc] = useState(true)
  const [isExporting, setIsExporting] = useState(false)
  const [exportSuccess, setExportSuccess] = useState(false)

  const handleExport = async () => {
    setIsExporting(true)
    setExportSuccess(false)

    try {
      const accessToken = (session?.user as any)?.accessToken

      const params = new URLSearchParams({
        format: selectedFormat,
        include_prologue: includePrologue.toString(),
        include_epilogue: includeEpilogue.toString(),
        include_toc: includeToc.toString(),
      })

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/export/projects/${projectId}/export?${params}`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error('Export failed')
      }

      // Get filename from headers
      const contentDisposition = response.headers.get('Content-Disposition')
      const filenameMatch = contentDisposition?.match(/filename="(.+)"/)
      const filename = filenameMatch ? filenameMatch[1] : `${projectTitle}.${selectedFormat}`

      // Download file
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      setExportSuccess(true)
      setTimeout(() => {
        onClose()
        setExportSuccess(false)
      }, 2000)
    } catch (error) {
      console.error('Export error:', error)
      alert('Export failed. Please try again.')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={onClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50" />
        <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto z-50">
          {/* Header */}
          <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <Download className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <Dialog.Title className="text-xl font-bold text-gray-900 dark:text-white">
                  Export Manuscript
                </Dialog.Title>
                <Dialog.Description className="text-sm text-gray-600 dark:text-gray-400">
                  {projectTitle}
                </Dialog.Description>
              </div>
            </div>
            <Dialog.Close asChild>
              <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition">
                <X className="h-5 w-5 text-gray-500" />
              </button>
            </Dialog.Close>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Format selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Choose Format
              </label>
              <div className="grid grid-cols-1 gap-3">
                {formatOptions.map((format) => {
                  const Icon = format.icon
                  const isSelected = selectedFormat === format.id

                  return (
                    <button
                      key={format.id}
                      onClick={() => setSelectedFormat(format.id)}
                      className={`flex items-start p-4 border-2 rounded-lg transition text-left ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                      }`}
                    >
                      <div
                        className={`p-2 rounded-lg mr-4 ${
                          format.color === 'blue'
                            ? 'bg-blue-100 dark:bg-blue-900/30'
                            : format.color === 'green'
                            ? 'bg-green-100 dark:bg-green-900/30'
                            : 'bg-red-100 dark:bg-red-900/30'
                        }`}
                      >
                        <Icon
                          className={`h-6 w-6 ${
                            format.color === 'blue'
                              ? 'text-blue-600 dark:text-blue-400'
                              : format.color === 'green'
                              ? 'text-green-600 dark:text-green-400'
                              : 'text-red-600 dark:text-red-400'
                          }`}
                        />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className="font-semibold text-gray-900 dark:text-white">
                            {format.name}
                          </h4>
                          {isSelected && (
                            <Check className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                          )}
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          {format.description}
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {format.features.map((feature) => (
                            <span
                              key={feature}
                              className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded"
                            >
                              {feature}
                            </span>
                          ))}
                        </div>
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Options */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Include
              </label>
              <div className="space-y-3">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includePrologue}
                    onChange={(e) => setIncludePrologue(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Prologue (if present)
                  </span>
                </label>

                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeEpilogue}
                    onChange={(e) => setIncludeEpilogue(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Epilogue (if present)
                  </span>
                </label>

                {selectedFormat === 'docx' && (
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={includeToc}
                      onChange={(e) => setIncludeToc(e.target.checked)}
                      className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      Table of Contents
                    </span>
                  </label>
                )}
              </div>
            </div>

            {/* Success message */}
            {exportSuccess && (
              <div className="flex items-center space-x-2 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <Check className="h-5 w-5 text-green-600 dark:text-green-400" />
                <span className="text-sm text-green-800 dark:text-green-200">
                  Export successful! Your download should start automatically.
                </span>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="sticky bottom-0 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 p-6 flex items-center justify-between">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Format: <span className="font-medium">.{selectedFormat}</span>
            </p>
            <div className="flex items-center space-x-3">
              <button
                onClick={onClose}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={handleExport}
                disabled={isExporting}
                className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {isExporting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Exporting...</span>
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4" />
                    <span>Export</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
