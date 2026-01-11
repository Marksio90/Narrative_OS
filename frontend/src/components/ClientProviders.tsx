'use client'

import { ReactNode } from 'react'
import { SessionProvider } from 'next-auth/react'
import { QueryProvider } from '@/lib/query-client'
import { AuthProvider } from '@/lib/auth-context'
import { LocaleProvider } from '@/lib/locale-provider'

export function ClientProviders({ children }: { children: ReactNode }) {
  return (
    <SessionProvider>
      <QueryProvider>
        <AuthProvider>
          <LocaleProvider>
            {children}
          </LocaleProvider>
        </AuthProvider>
      </QueryProvider>
    </SessionProvider>
  )
}
