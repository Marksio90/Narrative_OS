'use client'

import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'
import ProjectManager from '@/components/ProjectManager'
import { useEffect, useState } from 'react'
import { useTranslations } from 'next-intl'

export default function ProjectsPage() {
  const { user, accessToken } = useAuth()
  const router = useRouter()
  const [currentProjectId, setCurrentProjectId] = useState<number | undefined>()
  const t = useTranslations('projects')
  const tCommon = useTranslations('common')

  useEffect(() => {
    if (!user) {
      router.push('/login')
    }

    // Load current project from localStorage
    const savedProjectId = localStorage.getItem('currentProjectId')
    if (savedProjectId) {
      setCurrentProjectId(parseInt(savedProjectId))
    }
  }, [user, router])

  const handleSelectProject = (projectId: number) => {
    // Save to localStorage
    localStorage.setItem('currentProjectId', projectId.toString())
    setCurrentProjectId(projectId)

    // Navigate to desktop with this project active
    router.push('/desktop')
  }

  if (!user || !accessToken) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-400 mt-4">{tCommon('loading')}</p>
        </div>
      </div>
    )
  }

  return (
    <ProjectManager
      accessToken={accessToken}
      onSelectProject={handleSelectProject}
      currentProjectId={currentProjectId}
    />
  )
}
