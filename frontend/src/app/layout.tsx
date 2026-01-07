import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Narrative OS - AI-Powered Narrative Platform',
  description: 'Structural consistency tools for serious fiction writers',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
