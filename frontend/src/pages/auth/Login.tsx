import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, User, Lock, Loader2, AlertCircle } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
  rememberMe: z.boolean().default(false),
})

type LoginFormData = z.infer<typeof loginSchema>

export default function Login() {
  const { login } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: '',
      password: '',
      rememberMe: false,
    },
  })

  const onSubmit = async (data: LoginFormData) => {
    setServerError(null)
    try {
      await login(data.username, data.password)
    } catch (err: any) {
      const message =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        'Invalid username or password. Please try again.'
      setServerError(message)
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 px-4 py-12">
      {/* Background decoration */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 h-80 w-80 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute -bottom-40 -right-40 h-80 w-80 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute left-1/2 top-1/2 h-60 w-60 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/5 blur-3xl" />
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Card */}
        <div className="rounded-2xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-xl sm:p-10">
          {/* Logo / Branding */}
          <div className="mb-8 text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10 ring-1 ring-primary/20">
              <span className="text-2xl font-bold text-primary">S</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              SmartERP
            </h1>
            <p className="mt-1 text-sm text-slate-400">
              Enterprise Resource Planning System
            </p>
          </div>

          {/* Error alert */}
          {serverError && (
            <div className="mb-6 flex items-start gap-3 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3">
              <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-red-400" />
              <p className="text-sm text-red-300">{serverError}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {/* Username */}
            <div className="space-y-1.5">
              <label
                htmlFor="username"
                className="text-sm font-medium text-slate-300"
              >
                Username
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5">
                  <User className="h-4 w-4 text-slate-500" />
                </div>
                <input
                  id="username"
                  type="text"
                  autoComplete="username"
                  placeholder="Enter your username"
                  disabled={isSubmitting}
                  className={cn(
                    'block w-full rounded-lg border bg-white/5 py-2.5 pl-10 pr-4 text-sm text-white placeholder-slate-500 outline-none transition-colors',
                    'focus:border-primary/50 focus:ring-1 focus:ring-primary/50',
                    'disabled:cursor-not-allowed disabled:opacity-50',
                    errors.username
                      ? 'border-red-500/50'
                      : 'border-white/10'
                  )}
                  {...register('username')}
                />
              </div>
              {errors.username && (
                <p className="text-xs text-red-400">
                  {errors.username.message}
                </p>
              )}
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <label
                htmlFor="password"
                className="text-sm font-medium text-slate-300"
              >
                Password
              </label>
              <div className="relative">
                <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5">
                  <Lock className="h-4 w-4 text-slate-500" />
                </div>
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  placeholder="Enter your password"
                  disabled={isSubmitting}
                  className={cn(
                    'block w-full rounded-lg border bg-white/5 py-2.5 pl-10 pr-11 text-sm text-white placeholder-slate-500 outline-none transition-colors',
                    'focus:border-primary/50 focus:ring-1 focus:ring-primary/50',
                    'disabled:cursor-not-allowed disabled:opacity-50',
                    errors.password
                      ? 'border-red-500/50'
                      : 'border-white/10'
                  )}
                  {...register('password')}
                />
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-500 transition-colors hover:text-slate-300"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="text-xs text-red-400">
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* Remember me */}
            <div className="flex items-center justify-between">
              <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-400">
                <input
                  type="checkbox"
                  disabled={isSubmitting}
                  className="h-4 w-4 rounded border-white/20 bg-white/5 text-primary focus:ring-primary/50"
                  {...register('rememberMe')}
                />
                Remember me
              </label>
            </div>

            {/* Submit */}
            <Button
              type="submit"
              disabled={isSubmitting}
              className="h-11 w-full text-sm font-semibold"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </Button>
          </form>
        </div>

        {/* Footer */}
        <p className="mt-6 text-center text-xs text-slate-600">
          &copy; {new Date().getFullYear()} SmartERP. All rights reserved.
        </p>
      </div>
    </div>
  )
}
