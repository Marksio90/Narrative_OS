/**
 * NextAuth.js v5 Middleware
 * Protects routes that require authentication
 */
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'
import { auth } from './auth'

// Routes that require authentication
const protectedRoutes = [
  '/canon',
  '/planner',
  '/editor',
  '/promises',
  '/profile',
  '/settings',
]

// Routes that should redirect to home if already authenticated
const authRoutes = ['/login', '/register']

export async function middleware(request: NextRequest) {
  const session = await auth()
  const { pathname } = request.nextUrl

  // Check if route is protected
  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname.startsWith(route)
  )

  // Check if route is auth page
  const isAuthRoute = authRoutes.some((route) => pathname.startsWith(route))

  // Redirect to login if accessing protected route without session
  if (isProtectedRoute && !session) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('callbackUrl', pathname)
    return NextResponse.redirect(loginUrl)
  }

  // Redirect to home if accessing auth pages with active session
  if (isAuthRoute && session) {
    return NextResponse.redirect(new URL('/', request.url))
  }

  return NextResponse.next()
}

// Configure which routes to run middleware on
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api routes (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!api|_next/static|_next/image|favicon.ico|public).*)',
  ],
}
