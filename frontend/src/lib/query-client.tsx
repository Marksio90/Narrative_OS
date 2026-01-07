/**
 * TanStack Query v5 (React Query) Configuration
 * Modern data fetching + caching
 */
"use client"

import {
  QueryClient,
  QueryClientProvider,
  useQuery,
  useMutation,
} from "@tanstack/react-query"
import { ReactQueryDevtools } from "@tanstack/react-query-devtools"
import { ReactNode, useState } from "react"

export function QueryProvider({ children }: { children: ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // Stale time: data considered fresh for 5 minutes
            staleTime: 5 * 60 * 1000,
            // Cache time: data kept in cache for 10 minutes
            gcTime: 10 * 60 * 1000,
            // Retry failed requests 3 times
            retry: 3,
            // Refetch on window focus (good for stale data)
            refetchOnWindowFocus: true,
          },
          mutations: {
            // Retry mutations once on network error
            retry: 1,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* Development tools - shows queries/mutations in dev */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}

// Export TanStack Query hooks for convenience
export { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
