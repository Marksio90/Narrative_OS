/**
 * Permission Guard Components
 * Conditionally render UI based on user permissions
 */
import { ReactNode } from 'react'
import { usePermissions } from '@/hooks/usePermissions'

interface PermissionGuardProps {
  projectId: number
  children: ReactNode
  fallback?: ReactNode
  requireOwner?: boolean
  requireEditor?: boolean
  requireWriter?: boolean
  requireViewer?: boolean
}

/**
 * Render children only if user has required permissions
 *
 * @example
 * <PermissionGuard projectId={1} requireEditor>
 *   <EditButton />
 * </PermissionGuard>
 */
export function PermissionGuard({
  projectId,
  children,
  fallback = null,
  requireOwner = false,
  requireEditor = false,
  requireWriter = false,
  requireViewer = false,
}: PermissionGuardProps) {
  const permissions = usePermissions(projectId)

  if (permissions.isLoading) {
    return <>{fallback}</>
  }

  // Check role requirements
  if (requireOwner && !permissions.isOwner) {
    return <>{fallback}</>
  }

  if (requireEditor && !(permissions.isEditor || permissions.isOwner)) {
    return <>{fallback}</>
  }

  if (requireWriter && !permissions.canWrite) {
    return <>{fallback}</>
  }

  if (requireViewer && !permissions.canView) {
    return <>{fallback}</>
  }

  return <>{children}</>
}

/**
 * Render children only if user can edit
 */
export function CanEdit({
  projectId,
  children,
  fallback = null,
}: {
  projectId: number
  children: ReactNode
  fallback?: ReactNode
}) {
  const { canEdit, isLoading } = usePermissions(projectId)

  if (isLoading || !canEdit) return <>{fallback}</>
  return <>{children}</>
}

/**
 * Render children only if user can manage (owner only)
 */
export function CanManage({
  projectId,
  children,
  fallback = null,
}: {
  projectId: number
  children: ReactNode
  fallback?: ReactNode
}) {
  const { canManage, isLoading } = usePermissions(projectId)

  if (isLoading || !canManage) return <>{fallback}</>
  return <>{children}</>
}

/**
 * Render children only if user can write prose
 */
export function CanWrite({
  projectId,
  children,
  fallback = null,
}: {
  projectId: number
  children: ReactNode
  fallback?: ReactNode
}) {
  const { canWrite, isLoading } = usePermissions(projectId)

  if (isLoading || !canWrite) return <>{fallback}</>
  return <>{children}</>
}

/**
 * Show role badge for current user
 */
export function RoleBadge({ projectId }: { projectId: number }) {
  const { role, isLoading } = usePermissions(projectId)

  if (isLoading) return null

  const roleColors = {
    owner: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    editor: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    writer: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    viewer: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
  }

  const colorClass = role ? roleColors[role] : roleColors.viewer

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}
    >
      {role?.toUpperCase()}
    </span>
  )
}
