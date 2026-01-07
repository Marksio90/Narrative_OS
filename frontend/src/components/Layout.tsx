import Link from 'next/link'
import { ReactNode } from 'react'
import { BookOpen, Users, FileEdit, Target, Home } from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
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
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
              >
                <Home className="h-4 w-4" />
                <span>Home</span>
              </Link>
              <Link
                href="/canon"
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
              >
                <BookOpen className="h-4 w-4" />
                <span>Canon</span>
              </Link>
              <Link
                href="/planner"
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
              >
                <Users className="h-4 w-4" />
                <span>Planner</span>
              </Link>
              <Link
                href="/editor"
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
              >
                <FileEdit className="h-4 w-4" />
                <span>Editor</span>
              </Link>
              <Link
                href="/promises"
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
              >
                <Target className="h-4 w-4" />
                <span>Promises</span>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8">{children}</main>
    </div>
  )
}
