/**
 * Main Layout - Pages with navigation
 * Wraps all authenticated pages (canon, planner, editor, profile, etc.)
 */
import Layout from '@/components/Layout'

export default function MainLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <Layout>{children}</Layout>
}
