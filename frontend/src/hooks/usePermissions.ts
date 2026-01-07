/**
 * React hooks for project permissions and role checking
 * Uses TanStack Query for caching permission checks
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useSession } from 'next-auth/react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

type CollaboratorRole = 'owner' | 'editor' | 'writer' | 'viewer'

interface UserProjectRole {
  project_id: number
  user_id: number
  role: CollaboratorRole
  can_view: boolean
  can_edit: boolean
  can_write: boolean
  can_manage: boolean
}

interface Collaborator {
  id: number
  project_id: number
  user_id: number
  user_name: string
  user_email: string
  user_avatar: string | null
  role: CollaboratorRole
  invited_at: string
  accepted_at: string | null
  is_pending: boolean
  project_title?: string
}

interface CollaboratorInvite {
  email: string
  role: 'viewer' | 'writer' | 'editor'
  auto_accept?: boolean
}

/**
 * Fetch user's role and permissions for a project
 */
async function fetchProjectRole(
  projectId: number,
  accessToken?: string
): Promise<UserProjectRole> {
  const response = await fetch(
    `${API_URL}/api/projects/${projectId}/role`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  )

  if (!response.ok) {
    if (response.status === 403) {
      throw new Error('No access to this project')
    }
    throw new Error('Failed to fetch project role')
  }

  return response.json()
}

/**
 * Hook to get user's role and permissions for a project
 * Returns permission flags (can_view, can_edit, can_write, can_manage)
 *
 * @example
 * const { role, can_edit, can_manage, isLoading } = useProjectRole(projectId)
 *
 * if (can_edit) {
 *   // Show edit UI
 * }
 */
export function useProjectRole(projectId: number | undefined) {
  const { data: session } = useSession()
  const accessToken = (session?.user as any)?.accessToken

  return useQuery({
    queryKey: ['project-role', projectId, session?.user?.id],
    queryFn: () => fetchProjectRole(projectId!, accessToken),
    enabled: !!projectId && !!accessToken,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false,
  })
}

/**
 * Hook for permission-based UI rendering
 * Returns boolean flags for common permissions
 *
 * @example
 * const permissions = usePermissions(projectId)
 *
 * {permissions.canEdit && <EditButton />}
 * {permissions.canManage && <InviteButton />}
 */
export function usePermissions(projectId: number | undefined) {
  const { data, isLoading } = useProjectRole(projectId)

  return {
    role: data?.role,
    canView: data?.can_view ?? false,
    canEdit: data?.can_edit ?? false,
    canWrite: data?.can_write ?? false,
    canManage: data?.can_manage ?? false,
    isOwner: data?.role === 'owner',
    isEditor: data?.role === 'editor',
    isWriter: data?.role === 'writer',
    isViewer: data?.role === 'viewer',
    isLoading,
  }
}

/**
 * Fetch all collaborators for a project
 */
async function fetchCollaborators(
  projectId: number,
  accessToken?: string
): Promise<Collaborator[]> {
  const response = await fetch(
    `${API_URL}/api/projects/${projectId}/collaborators`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  )

  if (!response.ok) {
    throw new Error('Failed to fetch collaborators')
  }

  return response.json()
}

/**
 * Hook to list all collaborators for a project
 */
export function useCollaborators(projectId: number | undefined) {
  const { data: session } = useSession()
  const accessToken = (session?.user as any)?.accessToken

  return useQuery({
    queryKey: ['collaborators', projectId],
    queryFn: () => fetchCollaborators(projectId!, accessToken),
    enabled: !!projectId && !!accessToken,
  })
}

/**
 * Hook to invite a collaborator to a project
 */
export function useInviteCollaborator(projectId: number) {
  const { data: session } = useSession()
  const accessToken = (session?.user as any)?.accessToken
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (invite: CollaboratorInvite) => {
      const response = await fetch(
        `${API_URL}/api/projects/${projectId}/collaborators`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify(invite),
        }
      )

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to invite collaborator')
      }

      return response.json()
    },
    onSuccess: () => {
      // Invalidate collaborators list
      queryClient.invalidateQueries({ queryKey: ['collaborators', projectId] })
    },
  })
}

/**
 * Hook to remove a collaborator from a project
 */
export function useRemoveCollaborator(projectId: number) {
  const { data: session } = useSession()
  const accessToken = (session?.user as any)?.accessToken
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (collaboratorId: number) => {
      const response = await fetch(
        `${API_URL}/api/projects/${projectId}/collaborators/${collaboratorId}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error('Failed to remove collaborator')
      }

      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['collaborators', projectId] })
    },
  })
}

/**
 * Hook to fetch pending invitations for current user
 */
export function useMyInvitations() {
  const { data: session } = useSession()
  const accessToken = (session?.user as any)?.accessToken

  return useQuery({
    queryKey: ['my-invitations', session?.user?.id],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/api/me/invitations`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to fetch invitations')
      }

      return response.json() as Promise<Collaborator[]>
    },
    enabled: !!accessToken,
  })
}

/**
 * Hook to accept a collaboration invitation
 */
export function useAcceptInvitation() {
  const { data: session } = useSession()
  const accessToken = (session?.user as any)?.accessToken
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (collaborationId: number) => {
      const response = await fetch(
        `${API_URL}/api/collaborations/${collaborationId}/accept`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error('Failed to accept invitation')
      }

      return response.json()
    },
    onSuccess: () => {
      // Refresh invitations list
      queryClient.invalidateQueries({ queryKey: ['my-invitations'] })
    },
  })
}
