'use client'

import Link from 'next/link'
import { ReactNode } from 'react'
import { BookOpen, Users, FileEdit, Target, Home, Book } from 'lucide-react'
import { useTranslations } from 'next-intl'
import UserNav from './UserNav'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const tNav = useTranslations('navigation')

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <nav className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-950">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            <Link href="/" className="flex items-center space-x-2">
              <BookOpen className="h-6 w-6 text-blue-600" />
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                Narrative OS
              </span>
            </Link>

            <div className="flex items-center space-x-6">
              <Link
                href="/"
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition"
              >
                <Home className="h-4 w-4" />
                <span className="hidden md:inline">{tNav('home')}</span>
              </Link>
              <Link
                href="/projects"
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition"
              >
                <BookOpen className="h-4 w-4" />
                <span className="hidden md:inline">{tNav('projects')}</span>
              </Link>
              <Link
                href="/story-bible"
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition"
              >
                <Book className="h-4 w-4" />
                <span className="hidden md:inline">{tNav('storyBible')}</span>
              </Link>
              <Link
                href="/planner"
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition"
              >
                <Users className="h-4 w-4" />
                <span className="hidden md:inline">{tNav('planner')}</span>
              </Link>
              <Link
                href="/ai-studio"
                className="flex items-center space-x-1 px-3 py-1.5 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition shadow-sm"
              >
                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
                <span className="hidden md:inline font-medium">{tNav('aiStudio')}</span>
              </Link>

              {/* User Navigation */}
              <div className="ml-4 pl-4 border-l border-gray-200 dark:border-gray-700">
                <UserNav />
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8">{children}</main>
    </div>
  )
}
