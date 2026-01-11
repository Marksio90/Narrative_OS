/**
 * Usage Statistics Page
 * Display LLM usage, storage, and subscription limits
 */
'use client'

import { useSession } from 'next-auth/react'
import { useQuery } from '@tanstack/react-query'
import { useTranslations } from 'next-intl'
import { Zap, HardDrive, Calendar, TrendingUp, Loader2, CreditCard } from 'lucide-react'
import Link from 'next/link'

interface UsageStats {
  llm_calls: number
  llm_calls_limit: number
  llm_calls_percentage: number
  storage_used_mb: number
  storage_limit_mb: number
  storage_percentage: number
  can_generate: boolean
  upgrade_recommended: boolean
}

async function fetchUsageStats(accessToken?: string): Promise<UsageStats> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/api/auth/me/usage`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  )

  if (!response.ok) {
    throw new Error('Nie udało się pobrać statystyk użycia')
  }

  return response.json()
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

function ProgressBar({
  value,
  max,
  label,
  color = 'blue',
  warningText,
}: {
  value: number
  max: number
  label: string
  color?: 'blue' | 'purple' | 'green' | 'yellow' | 'red'
  warningText?: string
}) {
  const percentage = Math.min((value / max) * 100, 100)
  const isNearLimit = percentage > 80

  const colorClasses = {
    blue: 'bg-blue-600',
    purple: 'bg-purple-600',
    green: 'bg-green-600',
    yellow: 'bg-yellow-500',
    red: 'bg-red-600',
  }

  const bgColor = isNearLimit ? colorClasses.red : colorClasses[color]

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-gray-700 dark:text-gray-300">{label}</span>
        <span className="text-gray-600 dark:text-gray-400">
          {value.toLocaleString()} / {max.toLocaleString()}
        </span>
      </div>
      <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full ${bgColor} transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {isNearLimit && warningText && (
        <p className="text-sm text-red-600 dark:text-red-400">
          {warningText}
        </p>
      )}
    </div>
  )
}

function StatCard({
  icon: Icon,
  title,
  value,
  subtitle,
  trend,
}: {
  icon: any
  title: string
  value: string
  subtitle: string
  trend?: string
}) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
          <Icon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
        </div>
        {trend && (
          <span className="text-sm text-green-600 dark:text-green-400 flex items-center space-x-1">
            <TrendingUp className="h-4 w-4" />
            <span>{trend}</span>
          </span>
        )}
      </div>
      <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">{value}</h3>
      <p className="text-sm text-gray-600 dark:text-gray-400">{title}</p>
      <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">{subtitle}</p>
    </div>
  )
}

export default function UsagePage() {
  const { data: session } = useSession()
  const accessToken = (session?.user as any)?.accessToken
  const t = useTranslations('usage')
  const tCommon = useTranslations('common')

  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['usage-stats', session?.user?.id],
    queryFn: () => fetchUsageStats(accessToken),
    enabled: !!accessToken,
    refetchInterval: 60000, // Refetch every minute
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
          <p className="text-gray-600 dark:text-gray-400 mt-4">{tCommon('loading')}</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
          <p className="text-red-800 dark:text-red-200">
            {t('loadError')}
          </p>
        </div>
      </div>
    )
  }

  const subscriptionTier = ((session?.user as any)?.subscriptionTier || 'free') as string

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          {t('title')}
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          {t('subtitle')}
        </p>
      </div>

      {/* Subscription tier banner */}
      <div className="mb-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-1">
              {subscriptionTier.toUpperCase()} Plan
            </h2>
            <p className="text-blue-100">
              {stats?.upgrade_recommended
                ? t('upgradeRecommended')
                : t('resourcesAvailable')}
            </p>
          </div>
          {subscriptionTier !== 'studio' && (
            <Link
              href="/pricing"
              className="px-6 py-3 bg-white text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition"
            >
              {t('upgradePlan')}
            </Link>
          )}
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatCard
          icon={Zap}
          title={t('llmCalls')}
          value={stats?.llm_calls.toLocaleString() || '0'}
          subtitle={`of ${stats?.llm_calls_limit.toLocaleString() || '0'} this month`}
        />
        <StatCard
          icon={HardDrive}
          title={t('storageUsed')}
          value={`${stats?.storage_used_mb.toFixed(1) || '0'} MB`}
          subtitle={`of ${stats?.storage_limit_mb.toLocaleString() || '0'} MB available`}
        />
        <StatCard
          icon={Calendar}
          title={t('generationStatus')}
          value={stats?.can_generate ? t('active') : t('limited')}
          subtitle={stats?.can_generate ? t('readyToGenerate') : t('limitReached')}
        />
      </div>

      {/* Usage progress bars */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
          {t('monthlyUsage')}
        </h3>
        <div className="space-y-6">
          <ProgressBar
            value={stats?.llm_calls || 0}
            max={stats?.llm_calls_limit || 100}
            label={t('llmApiCalls')}
            color="blue"
            warningText={t('approachingLimit')}
          />
          <ProgressBar
            value={stats?.storage_used_mb || 0}
            max={stats?.storage_limit_mb || 100}
            label={t('storage')}
            color="purple"
            warningText={t('approachingLimit')}
          />
        </div>
      </div>

      {/* Billing history */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {t('billingHistory')}
          </h3>
          <Link
            href="/settings/billing"
            className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
          >
            {t('managePayment')}
          </Link>
        </div>

        {/* Placeholder for billing history */}
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          <CreditCard className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>{t('noBillingHistory')}</p>
          <p className="text-sm mt-2">
            {t('invoicesAppear')}
          </p>
        </div>
      </div>

      {/* Upgrade CTA for free users */}
      {subscriptionTier === 'free' && (
        <div className="mt-8 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg border border-purple-200 dark:border-purple-800 p-8 text-center">
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {t('readyForMore')}
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {t('upgradePromo')}
          </p>
          <Link
            href="/pricing"
            className="inline-flex items-center space-x-2 px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition font-medium"
          >
            <span>{t('viewPricing')}</span>
          </Link>
        </div>
      )}
    </div>
  )
}
