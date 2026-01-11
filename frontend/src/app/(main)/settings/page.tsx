/**
 * Settings Page
 * Application preferences, notifications, theme
 */
'use client'

import { useState } from 'react'
import { useSession } from 'next-auth/react'
import { useTranslations } from 'next-intl'
import { useLocale } from '@/lib/locale-provider'
import {
  Bell,
  Moon,
  Sun,
  Globe,
  Shield,
  Mail,
  Smartphone,
  Save,
  Loader2,
} from 'lucide-react'

export default function SettingsPage() {
  const { data: session } = useSession()
  const { locale, setLocale } = useLocale()
  const t = useTranslations('settings')
  const tCommon = useTranslations('common')
  const [isLoading, setIsLoading] = useState(false)
  const [settings, setSettings] = useState({
    // Notifications
    emailNotifications: true,
    pushNotifications: false,
    weeklyDigest: true,

    // Preferences
    theme: 'system', // 'light', 'dark', 'system'

    // Privacy
    publicProfile: false,
    showActivity: true,
  })

  const handleSave = async () => {
    setIsLoading(true)
    try {
      // TODO: Call API to save settings
      await new Promise((resolve) => setTimeout(resolve, 1000))
      alert(t('saveSuccess'))
    } catch (error) {
      console.error('Error saving settings:', error)
      alert(t('saveError'))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          {t('title')}
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          {t('subtitle')}
        </p>
      </div>

      <div className="space-y-6">
        {/* Notifications */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center space-x-3 mb-6">
            <Bell className="h-5 w-5 text-gray-700 dark:text-gray-300" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              {t('notifications.title')}
            </h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-start space-x-3">
                <Mail className="h-5 w-5 text-gray-500 mt-1" />
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {t('notifications.email')}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {t('notifications.emailDescription')}
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.emailNotifications}
                  onChange={(e) =>
                    setSettings({ ...settings, emailNotifications: e.target.checked })
                  }
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-start space-x-3">
                <Smartphone className="h-5 w-5 text-gray-500 mt-1" />
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">
                    Powiadomienia Push
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Otrzymuj powiadomienia push na swoich urządzeniach
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.pushNotifications}
                  onChange={(e) =>
                    setSettings({ ...settings, pushNotifications: e.target.checked })
                  }
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-start space-x-3">
                <Mail className="h-5 w-5 text-gray-500 mt-1" />
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">
                    Tygodniowe Podsumowanie
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Otrzymuj cotygodniowe podsumowanie postępów
                  </p>
                </div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.weeklyDigest}
                  onChange={(e) =>
                    setSettings({ ...settings, weeklyDigest: e.target.checked })
                  }
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Appearance */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center space-x-3 mb-6">
            <Sun className="h-5 w-5 text-gray-700 dark:text-gray-300" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Wygląd
            </h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Motyw
              </label>
              <div className="grid grid-cols-3 gap-4">
                <button
                  onClick={() => setSettings({ ...settings, theme: 'light' })}
                  className={`flex flex-col items-center p-4 border-2 rounded-lg transition ${
                    settings.theme === 'light'
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Sun className="h-6 w-6 mb-2 text-yellow-500" />
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    Jasny
                  </span>
                </button>

                <button
                  onClick={() => setSettings({ ...settings, theme: 'dark' })}
                  className={`flex flex-col items-center p-4 border-2 rounded-lg transition ${
                    settings.theme === 'dark'
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Moon className="h-6 w-6 mb-2 text-purple-500" />
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    Ciemny
                  </span>
                </button>

                <button
                  onClick={() => setSettings({ ...settings, theme: 'system' })}
                  className={`flex flex-col items-center p-4 border-2 rounded-lg transition ${
                    settings.theme === 'system'
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Globe className="h-6 w-6 mb-2 text-blue-500" />
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    Systemowy
                  </span>
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Język
              </label>
              <select
                value={locale}
                onChange={(e) => setLocale(e.target.value as 'pl' | 'en' | 'fr' | 'de' | 'es')}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value="pl">🇵🇱 Polski</option>
                <option value="en">🇬🇧 English</option>
                <option value="fr">🇫🇷 Français</option>
                <option value="de">🇩🇪 Deutsch</option>
                <option value="es">🇪🇸 Español</option>
              </select>
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                Zmiana języka zostanie zastosowana natychmiast
              </p>
            </div>
          </div>
        </div>

        {/* Privacy */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center space-x-3 mb-6">
            <Shield className="h-5 w-5 text-gray-700 dark:text-gray-300" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Prywatność
            </h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">
                  Publiczny Profil
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Zezwalaj innym na przeglądanie twojego profilu
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.publicProfile}
                  onChange={(e) =>
                    setSettings({ ...settings, publicProfile: e.target.checked })
                  }
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">
                  Pokaż Aktywność
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Wyświetlaj swoją ostatnią aktywność współpracownikom
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.showActivity}
                  onChange={(e) =>
                    setSettings({ ...settings, showActivity: e.target.checked })
                  }
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Save button */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            disabled={isLoading}
            className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Zapisywanie...</span>
              </>
            ) : (
              <>
                <Save className="h-5 w-5" />
                <span>Zapisz Zmiany</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
