import Link from 'next/link'
import { ReactNode } from 'react'
import { BookOpen, Users, FileEdit, Target, Home } from 'lucide-react'
import UserNav from './UserNav'

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
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition"
              >
                <Home className="h-4 w-4" />
                <span className="hidden md:inline">Home</span>
              </Link>
              <Link
                href="/canon"
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition"
              >
                <BookOpen className="h-4 w-4" />
                <span className="hidden md:inline">Canon</span>
              </Link>
              <Link
                href="/planner"
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition"
              >
                <Users className="h-4 w-4" />
                <span className="hidden md:inline">Planner</span>
              </Link>
              <Link
                href="/editor"
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition"
              >
                <FileEdit className="h-4 w-4" />
                <span className="hidden md:inline">Editor</span>
              </Link>
              <Link
                href="/promises"
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition"
              >
                <Target className="h-4 w-4" />
                <span className="hidden md:inline">Promises</span>
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
