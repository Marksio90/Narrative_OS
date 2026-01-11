'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { signIn } from 'next-auth/react'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useTranslations } from 'next-intl'
import { Mail, Lock, User, Loader2, Github, Chrome, Check } from 'lucide-react'
import Button from '@/components/Button'
import api from '@/lib/api'

type RegisterFormData = {
  name: string
  email: string
  password: string
  confirmPassword: string
}

export default function RegisterPage() {
  const router = useRouter()
  const tAuth = useTranslations('auth')
  const tValidation = useTranslations('validation')
  const tCommon = useTranslations('common')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  // Create schema with dynamic validation messages
  const registerSchema = z
    .object({
      name: z.string().min(2, tValidation('nameMin', { min: 2 })),
      email: z.string().email(tValidation('emailInvalid')),
      password: z.string().min(8, tValidation('passwordMin', { min: 8 })),
      confirmPassword: z.string(),
    })
    .refine((data) => data.password === data.confirmPassword, {
      message: tValidation('passwordMismatch'),
      path: ['confirmPassword'],
    })

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true)
    setError('')

    try {
      // Register user via backend
      const response = await api.post('/api/auth/register', {
        email: data.email,
        password: data.password,
        name: data.name,
      })

      // Auto-login after registration
      const result = await signIn('credentials', {
        email: data.email,
        password: data.password,
        redirect: false,
      })

      if (result?.error) {
        setError(tAuth('registrationSuccessLoginFailed'))
        setIsLoading(false)
        return
      }

      // Redirect to onboarding or home
      router.push('/onboarding')
      router.refresh()
    } catch (err: any) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail)
      } else {
        setError(tCommon('errorOccurred'))
      }
      setIsLoading(false)
    }
  }

  const handleSocialRegister = (provider: 'google' | 'github') => {
    setIsLoading(true)
    signIn(provider, {
      callbackUrl: '/onboarding',
    })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-white to-blue-50 dark:from-purple-950 dark:via-gray-800 dark:to-gray-900 px-4 py-12">
      <div className="max-w-md w-full space-y-8">
        {/* Logo + Title */}
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-600 to-blue-600 shadow-lg mb-4">
            <span className="text-2xl font-bold text-white">N</span>
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
            {tAuth('startJourney')}
          </h2>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            {tAuth('joinAuthors')}
          </p>
        </div>

        {/* Auth Card */}
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-gray-200/50 dark:border-gray-700/50">
          {/* Social Register Buttons */}
          <div className="space-y-3">
            <Button
              type="button"
              variant="secondary"
              className="w-full flex items-center justify-center space-x-2"
              onClick={() => handleSocialRegister('google')}
              disabled={isLoading}
            >
              <Chrome className="h-5 w-5" />
              <span>{tAuth('continueWithGoogle')}</span>
            </Button>

            <Button
              type="button"
              variant="secondary"
              className="w-full flex items-center justify-center space-x-2"
              onClick={() => handleSocialRegister('github')}
              disabled={isLoading}
            >
              <Github className="h-5 w-5" />
              <span>{tAuth('continueWithGithub')}</span>
            </Button>
          </div>

          {/* Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300 dark:border-gray-600"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white/80 dark:bg-gray-800/80 text-gray-500">
                {tAuth('orRegisterWithEmail')}
              </span>
            </div>
          </div>

          {/* Register Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </div>
            )}

            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 block">
                {tAuth('fullName')}
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  {...register('name')}
                  type="text"
                  placeholder={tAuth('fullNamePlaceholder')}
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                  disabled={isLoading}
                />
              </div>
              {errors.name && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.name.message}
                </p>
              )}
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 block">
                {tAuth('email')}
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  {...register('email')}
                  type="email"
                  placeholder={tAuth('emailPlaceholder')}
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                  disabled={isLoading}
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.email.message}
                </p>
              )}
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 block">
                {tAuth('password')}
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  {...register('password')}
                  type="password"
                  placeholder={tAuth('passwordPlaceholder')}
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                  disabled={isLoading}
                />
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.password.message}
                </p>
              )}
            </div>

            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 block">
                {tAuth('confirmPassword')}
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  {...register('confirmPassword')}
                  type="password"
                  placeholder={tAuth('passwordPlaceholder')}
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
                  disabled={isLoading}
                />
              </div>
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.confirmPassword.message}
                </p>
              )}
            </div>

            <div className="flex items-start space-x-2">
              <input
                type="checkbox"
                required
                className="w-4 h-4 rounded border-gray-300 text-purple-600 focus:ring-purple-500 mt-1"
              />
              <label className="text-sm text-gray-600 dark:text-gray-400">
                {tAuth('agreeToTerms')}{' '}
                <Link
                  href="/terms"
                  className="text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 font-medium"
                >
                  {tAuth('terms')}
                </Link>{' '}
                {tAuth('and')}{' '}
                <Link
                  href="/privacy"
                  className="text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 font-medium"
                >
                  {tAuth('privacy')}
                </Link>
              </label>
            </div>

            <Button
              type="submit"
              className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>{tAuth('creatingAccount')}</span>
                </>
              ) : (
                <>
                  <Check className="h-5 w-5" />
                  <span>{tAuth('createAccount')}</span>
                </>
              )}
            </Button>
          </form>

          {/* Features List */}
          <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
              {tAuth('whatYouGet')}
            </p>
            <ul className="space-y-2 text-xs text-gray-600 dark:text-gray-400">
              <li className="flex items-center space-x-2">
                <Check className="h-3 w-3 text-green-600" />
                <span>{tAuth('freeCallsPerMonth')}</span>
              </li>
              <li className="flex items-center space-x-2">
                <Check className="h-3 w-3 text-green-600" />
                <span>{tAuth('unlimitedProjects')}</span>
              </li>
              <li className="flex items-center space-x-2">
                <Check className="h-3 w-3 text-green-600" />
                <span>{tAuth('aiQualityControl')}</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Sign in link */}
        <p className="text-center text-sm text-gray-600 dark:text-gray-400">
          {tAuth('alreadyHaveAccount')}{' '}
          <Link
            href="/login"
            className="font-medium text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300"
          >
            {tAuth('signIn')}
          </Link>
        </p>
      </div>
    </div>
  )
}
