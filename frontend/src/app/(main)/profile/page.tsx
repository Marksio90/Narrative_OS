/**
 * User Profile Page
 * Account settings, avatar upload, personal information
 */
'use client'

import { useState } from 'react'
import { useSession } from 'next-auth/react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { User, Mail, Camera, Save, Loader2 } from 'lucide-react'
import * as Avatar from '@radix-ui/react-avatar'

const profileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
})

type ProfileFormData = z.infer<typeof profileSchema>

export default function ProfilePage() {
  const { data: session, update } = useSession()
  const [isLoading, setIsLoading] = useState(false)
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: session?.user?.name || '',
      email: session?.user?.email || '',
    },
  })

  const onSubmit = async (data: ProfileFormData) => {
    setIsLoading(true)
    try {
      // TODO: Call API to update profile
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/me`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${(session?.user as any)?.accessToken}`,
        },
        body: JSON.stringify(data),
      })

      if (response.ok) {
        // Update session
        await update({
          ...session,
          user: {
            ...session?.user,
            name: data.name,
            email: data.email,
          },
        })

        alert('Profile updated successfully!')
      } else {
        throw new Error('Failed to update profile')
      }
    } catch (error) {
      console.error('Error updating profile:', error)
      alert('Failed to update profile. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string)
      }
      reader.readAsDataURL(file)

      // TODO: Upload avatar to server
    }
  }

  if (!session) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  const user = session.user
  const subscriptionTier = (user as any)?.subscriptionTier || 'free'

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Profile Settings
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Manage your account information and preferences
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        {/* Header with gradient */}
        <div className="h-32 bg-gradient-to-r from-blue-500 to-purple-600" />

        {/* Avatar section */}
        <div className="px-8 pb-8">
          <div className="relative -mt-16 mb-6">
            <Avatar.Root className="w-32 h-32 rounded-full border-4 border-white dark:border-gray-800 shadow-lg">
              <Avatar.Image
                src={avatarPreview || user.image || undefined}
                alt={user.name || 'User'}
                className="w-full h-full rounded-full object-cover"
              />
              <Avatar.Fallback className="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-600 to-purple-600 text-white text-3xl font-bold">
                {user.name?.charAt(0).toUpperCase() || 'U'}
              </Avatar.Fallback>
            </Avatar.Root>

            <label
              htmlFor="avatar-upload"
              className="absolute bottom-2 right-2 p-2 bg-white dark:bg-gray-700 rounded-full shadow-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-600 transition"
            >
              <Camera className="h-5 w-5 text-gray-700 dark:text-gray-300" />
              <input
                id="avatar-upload"
                type="file"
                accept="image/*"
                className="hidden"
                onChange={handleAvatarChange}
              />
            </label>
          </div>

          {/* Subscription badge */}
          <div className="mb-6">
            <span
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                subscriptionTier === 'studio'
                  ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
                  : subscriptionTier === 'pro'
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
              }`}
            >
              {subscriptionTier.toUpperCase()} Plan
            </span>
          </div>

          {/* Profile form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <User className="inline h-4 w-4 mr-1" />
                Full Name
              </label>
              <input
                type="text"
                {...register('name')}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="John Doe"
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Mail className="inline h-4 w-4 mr-1" />
                Email Address
              </label>
              <input
                type="email"
                {...register('email')}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="john@example.com"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Member since {new Date(user.email || '').toLocaleDateString()}
              </p>
              <button
                type="submit"
                disabled={isLoading}
                className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4" />
                    <span>Save Changes</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Danger zone */}
      <div className="mt-8 bg-red-50 dark:bg-red-900/20 rounded-lg shadow-sm border border-red-200 dark:border-red-800 p-6">
        <h3 className="text-lg font-semibold text-red-900 dark:text-red-200 mb-2">
          Danger Zone
        </h3>
        <p className="text-sm text-red-700 dark:text-red-300 mb-4">
          Once you delete your account, there is no going back. Please be certain.
        </p>
        <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">
          Delete Account
        </button>
      </div>
    </div>
  )
}
