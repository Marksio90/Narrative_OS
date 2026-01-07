import Link from 'next/link'
import { BookOpen, Users, FileEdit, Target } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <header className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Narrative OS
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            AI-powered narrative platform for serious fiction writers.
            Maintain structural consistency across 300-600 page novels.
          </p>
        </header>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <Link
            href="/canon"
            className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
          >
            <BookOpen className="w-12 h-12 text-blue-600 mb-4" />
            <h2 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">
              Canon Studio
            </h2>
            <p className="text-gray-600 dark:text-gray-300">
              Define and manage your story bible: characters, locations, factions, magic rules, and more.
            </p>
          </Link>

          <Link
            href="/planner"
            className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
          >
            <Users className="w-12 h-12 text-green-600 mb-4" />
            <h2 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">
              Planner
            </h2>
            <p className="text-gray-600 dark:text-gray-300">
              Structure your story with 3-level planning: Book Arc, Chapters, and Scene Cards.
            </p>
          </Link>

          <Link
            href="/editor"
            className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
          >
            <FileEdit className="w-12 h-12 text-purple-600 mb-4" />
            <h2 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">
              Editor
            </h2>
            <p className="text-gray-600 dark:text-gray-300">
              Generate prose scene-by-scene with multi-agent quality control and validation.
            </p>
          </Link>

          <Link
            href="/promises"
            className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
          >
            <Target className="w-12 h-12 text-orange-600 mb-4" />
            <h2 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">
              Promise Ledger
            </h2>
            <p className="text-gray-600 dark:text-gray-300">
              Track narrative promises and payoffs. Never abandon a setup or miss a deadline.
            </p>
          </Link>
        </div>

        <footer className="text-center mt-16 text-gray-600 dark:text-gray-400">
          <p className="text-sm">
            Built for fantasy and thriller authors writing 300-600 page novels.
          </p>
        </footer>
      </div>
    </div>
  )
}
