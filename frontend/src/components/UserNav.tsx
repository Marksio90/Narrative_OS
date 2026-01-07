'use client'

import { useSession, signOut } from 'next-auth/react'
import Link from 'next/link'
import { User, Settings, LogOut, CreditCard, BarChart3 } from 'lucide-react'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import * as Avatar from '@radix-ui/react-avatar'

export default function UserNav() {
  const { data: session, status } = useSession()

  if (status === 'loading') {
    return (
      <div className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse" />
    )
  }

  if (!session) {
    return (
      <div className="flex items-center space-x-3">
        <Link
          href="/login"
          className="text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition"
        >
          Sign in
        </Link>
        <Link
          href="/register"
          className="text-sm font-medium px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition"
        >
          Get started
        </Link>
      </div>
    )
  }

  const user = session.user
  const subscriptionTier = (user as any).subscriptionTier || 'free'

  const getTierBadge = () => {
    switch (subscriptionTier) {
      case 'pro':
        return (
          <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 font-medium">
            PRO
          </span>
        )
      case 'studio':
        return (
          <span className="text-xs px-2 py-0.5 rounded-full bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 font-medium">
            STUDIO
          </span>
        )
      default:
        return (
          <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium">
            FREE
          </span>
        )
    }
  }

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button className="flex items-center space-x-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 p-2 transition">
          <Avatar.Root className="w-10 h-10 rounded-full overflow-hidden ring-2 ring-white dark:ring-gray-800 shadow-sm">
            <Avatar.Image
              src={user.image || undefined}
              alt={user.name || 'User'}
              className="w-full h-full object-cover"
            />
            <Avatar.Fallback
              className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-600 to-purple-600 text-white font-medium"
              delayMs={600}
            >
              {user.name?.charAt(0).toUpperCase() || user.email?.charAt(0).toUpperCase()}
            </Avatar.Fallback>
          </Avatar.Root>

          <div className="hidden md:block text-left">
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              {user.name}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {user.email}
            </p>
          </div>
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className="min-w-[240px] bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-2 z-50"
          sideOffset={5}
          align="end"
        >
          {/* User Info */}
          <div className="px-3 py-2 border-b border-gray-200 dark:border-gray-700">
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              {user.name}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
              {user.email}
            </p>
            <div className="mt-2">{getTierBadge()}</div>
          </div>

          {/* Menu Items */}
          <DropdownMenu.Item asChild>
            <Link
              href="/profile"
              className="flex items-center space-x-3 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 rounded hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer outline-none"
            >
              <User className="h-4 w-4" />
              <span>Profile</span>
            </Link>
          </DropdownMenu.Item>

          <DropdownMenu.Item asChild>
            <Link
              href="/usage"
              className="flex items-center space-x-3 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 rounded hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer outline-none"
            >
              <BarChart3 className="h-4 w-4" />
              <span>Usage & Billing</span>
            </Link>
          </DropdownMenu.Item>

          <DropdownMenu.Item asChild>
            <Link
              href="/subscription"
              className="flex items-center space-x-3 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 rounded hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer outline-none"
            >
              <CreditCard className="h-4 w-4" />
              <span>Upgrade Plan</span>
            </Link>
          </DropdownMenu.Item>

          <DropdownMenu.Item asChild>
            <Link
              href="/settings"
              className="flex items-center space-x-3 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 rounded hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer outline-none"
            >
              <Settings className="h-4 w-4" />
              <span>Settings</span>
            </Link>
          </DropdownMenu.Item>

          <DropdownMenu.Separator className="h-px bg-gray-200 dark:bg-gray-700 my-2" />

          <DropdownMenu.Item
            onSelect={() => signOut({ callbackUrl: '/login' })}
            className="flex items-center space-x-3 px-3 py-2 text-sm text-red-600 dark:text-red-400 rounded hover:bg-red-50 dark:hover:bg-red-900/20 cursor-pointer outline-none"
          >
            <LogOut className="h-4 w-4" />
            <span>Sign out</span>
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
