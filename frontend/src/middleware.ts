import createMiddleware from 'next-intl/middleware'
import { locales, defaultLocale } from './i18n'

export default createMiddleware({
  // A list of all locales that are supported
  locales,

  // Used when no locale matches
  defaultLocale,

  // Always use Polish as default locale
  localePrefix: 'as-needed',
})

export const config = {
  // Match only internationalized pathnames
  matcher: ['/', '/(pl|en|fr|de|es)/:path*', '/((?!api|_next|_vercel|.*\\..*).*)'],
}
