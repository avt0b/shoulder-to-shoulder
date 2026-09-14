import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLogin } from '@/shared/hooks'
import { authStore } from '@/shared/stores/authStore'
import { Footer } from '@/shared/components'
import { Button, Input, Card, Alert, AlertDescription, AlertIcon } from '@/shared/ui'
import { Loader2 } from 'lucide-react'

export function LoginPage() {
  const navigate = useNavigate()
  const { mutate: login, isPending, error } = useLogin()
  const setToken = authStore((state) => state.setToken)

  const [formData, setFormData] = useState({
    team_name: '',
    password: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    login(formData, {
      onSuccess: (response) => {
        const token = response.data.access_token
        setToken(token)
        navigate(response.data.role === 'admin' ? '/admin' : '/dashboard')
      },
    })
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  return (
    <div className="flex min-h-screen flex-col bg-neutral-50 dark:bg-neutral-950">
      <main className="flex flex-1 items-center justify-center px-4 py-12">
        <div className="w-full max-w-sm">
          <div className="mb-8 flex flex-col items-center text-center">
            <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-neutral-900 text-lg font-bold text-white dark:bg-white dark:text-neutral-900">
              S2
            </span>
            <h1 className="text-xl font-semibold tracking-tight text-neutral-900 dark:text-white">
              CTF Platform
            </h1>
            <p className="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
              Sign in with your team credentials
            </p>
          </div>

          <Card>
            <div className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertIcon variant="destructive" />
                  <AlertDescription>
                    {error instanceof Error ? error.message : 'Login failed. Please try again.'}
                  </AlertDescription>
                </Alert>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-1.5">
                  <label
                    htmlFor="team_name"
                    className="text-sm font-medium text-neutral-700 dark:text-neutral-300"
                  >
                    Team name
                  </label>
                  <Input
                    id="team_name"
                    name="team_name"
                    type="text"
                    placeholder="Enter your team name"
                    value={formData.team_name}
                    onChange={handleChange}
                    required
                    disabled={isPending}
                  />
                </div>

                <div className="space-y-1.5">
                  <label
                    htmlFor="password"
                    className="text-sm font-medium text-neutral-700 dark:text-neutral-300"
                  >
                    Password
                  </label>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    disabled={isPending}
                  />
                </div>

                <Button type="submit" className="w-full" disabled={isPending}>
                  {isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Signing in...
                    </>
                  ) : (
                    'Sign in'
                  )}
                </Button>
              </form>
            </div>
          </Card>
        </div>
      </main>
      <Footer />
    </div>
  )
}
