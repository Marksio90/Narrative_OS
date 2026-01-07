'use client'

import { useState } from 'react'
import Layout from '@/components/Layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card'
import Button from '@/components/Button'
import { Plus } from 'lucide-react'
import CharacterList from '@/components/canon/CharacterList'
import LocationList from '@/components/canon/LocationList'
import ContractList from '@/components/canon/ContractList'

type TabType = 'characters' | 'locations' | 'factions' | 'magic' | 'items' | 'events' | 'contracts'

export default function CanonPage() {
  const [activeTab, setActiveTab] = useState<TabType>('characters')
  const [projectId] = useState(1) // TODO: Get from context/auth

  const tabs: { id: TabType; label: string }[] = [
    { id: 'characters', label: 'Characters' },
    { id: 'locations', label: 'Locations' },
    { id: 'factions', label: 'Factions' },
    { id: 'magic', label: 'Magic Rules' },
    { id: 'items', label: 'Items' },
    { id: 'events', label: 'Events' },
    { id: 'contracts', label: 'Canon Contracts' },
  ]

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Canon Studio
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Your story bible - the source of truth for your narrative world
            </p>
          </div>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="border-b border-gray-200 dark:border-gray-700">
                <nav className="-mb-px flex space-x-8">
                  {tabs.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`
                        whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium
                        ${
                          activeTab === tab.id
                            ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                        }
                      `}
                    >
                      {tab.label}
                    </button>
                  ))}
                </nav>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {activeTab === 'characters' && <CharacterList projectId={projectId} />}
            {activeTab === 'locations' && <LocationList projectId={projectId} />}
            {activeTab === 'contracts' && <ContractList projectId={projectId} />}
            {activeTab === 'factions' && (
              <div className="text-center py-12 text-gray-500">
                Factions coming soon...
              </div>
            )}
            {activeTab === 'magic' && (
              <div className="text-center py-12 text-gray-500">
                Magic Rules coming soon...
              </div>
            )}
            {activeTab === 'items' && (
              <div className="text-center py-12 text-gray-500">
                Items coming soon...
              </div>
            )}
            {activeTab === 'events' && (
              <div className="text-center py-12 text-gray-500">
                Events coming soon...
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  )
}
