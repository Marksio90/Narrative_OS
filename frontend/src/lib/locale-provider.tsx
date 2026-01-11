'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { IntlProvider } from 'next-intl'

type Locale = 'pl' | 'en' | 'fr' | 'de' | 'es'

interface LocaleContextType {
  locale: Locale
  setLocale: (locale: Locale) => void
}

const LocaleContext = createContext<LocaleContextType | undefined>(undefined)

export function useLocale() {
  const context = useContext(LocaleContext)
  if (!context) {
    throw new Error('useLocale must be used within LocaleProvider')
  }
  return context
}

interface LocaleProviderProps {
  children: ReactNode
}

export function LocaleProvider({ children }: LocaleProviderProps) {
  const [locale, setLocaleState] = useState<Locale>('pl')
  const [messages, setMessages] = useState<any>(null)

  useEffect(() => {
    // Load locale from localStorage on mount
    const savedLocale = localStorage.getItem('locale') as Locale
    if (savedLocale && ['pl', 'en', 'fr', 'de', 'es'].includes(savedLocale)) {
      setLocaleState(savedLocale)
    }
  }, [])

  useEffect(() => {
    // Load messages for current locale
    async function loadMessages() {
      try {
        const msgs = await import(`../../messages/${locale}.json`)
        setMessages(msgs.default)
      } catch (error) {
        console.error(`Failed to load messages for locale: ${locale}`, error)
      }
    }
    loadMessages()
  }, [locale])

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale)
    localStorage.setItem('locale', newLocale)
    // Also set document language
    document.documentElement.lang = newLocale
  }

  if (!messages) {
    // Show loading state while messages are loading
    return null
  }

  return (
    <LocaleContext.Provider value={{ locale, setLocale }}>
      <IntlProvider locale={locale} messages={messages}>
        {children}
      </IntlProvider>
    </LocaleContext.Provider>
  )
}
