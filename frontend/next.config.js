const createNextIntlPlugin = require('next-intl/plugin')

const withNextIntl = createNextIntlPlugin('./src/i18n.ts')

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone', // Enable standalone output for Docker
  eslint: {
    // Disable ESLint during production builds (Docker)
    // Fix linting issues in development with: npm run lint
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Disable type checking during builds (for faster Docker builds)
    // Run type check separately with: npm run type-check
    ignoreBuildErrors: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = withNextIntl(nextConfig)
