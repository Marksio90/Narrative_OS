/**
 * NextAuth.js v5 Configuration (Auth.js)
 * Modern authentication with credentials + OAuth providers
 */
import type { NextAuthConfig } from "next-auth"
import Credentials from "next-auth/providers/credentials"
import Google from "next-auth/providers/google"
import GitHub from "next-auth/providers/github"

export const authConfig: NextAuthConfig = {
  providers: [
    // Credentials provider (email + password)
    Credentials({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        try {
          // Call our FastAPI backend
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/api/auth/jwt/login`,
            {
              method: "POST",
              headers: { "Content-Type": "application/x-www-form-urlencoded" },
              body: new URLSearchParams({
                username: credentials.email as string,
                password: credentials.password as string,
              }),
            }
          )

          if (!response.ok) {
            return null
          }

          const data = await response.json()

          // Return user object (must match User type)
          return {
            id: data.user.id.toString(),
            email: data.user.email,
            name: data.user.name,
            image: data.user.avatar_url,
            accessToken: data.access_token,
            subscriptionTier: data.user.subscription_tier,
          }
        } catch (error) {
          console.error("Auth error:", error)
          return null
        }
      },
    }),

    // Google OAuth (optional, requires setup)
    ...(process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET
      ? [
          Google({
            clientId: process.env.GOOGLE_CLIENT_ID,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET,
          }),
        ]
      : []),

    // GitHub OAuth (optional, requires setup)
    ...(process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET
      ? [
          GitHub({
            clientId: process.env.GITHUB_CLIENT_ID,
            clientSecret: process.env.GITHUB_CLIENT_SECRET,
          }),
        ]
      : []),
  ],

  pages: {
    signIn: "/login",
    signOut: "/",
    error: "/login",
  },

  callbacks: {
    async jwt({ token, user, account }) {
      // Initial sign in
      if (user) {
        token.id = user.id
        token.email = user.email
        token.name = user.name
        token.picture = user.image
        token.accessToken = (user as any).accessToken
        token.subscriptionTier = (user as any).subscriptionTier
      }

      // OAuth sign in
      if (account?.provider && account?.access_token) {
        token.accessToken = account.access_token
      }

      return token
    },

    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string
        session.user.email = token.email as string
        session.user.name = token.name as string
        session.user.image = token.picture as string
        ;(session.user as any).accessToken = token.accessToken
        ;(session.user as any).subscriptionTier = token.subscriptionTier
      }

      return session
    },
  },

  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },

  secret: process.env.NEXTAUTH_SECRET,
}
