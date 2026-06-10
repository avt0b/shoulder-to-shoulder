import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useLogin } from '@/shared/hooks'
import { authStore } from '@/shared/stores/authStore'
import { Button, Input, Card, CardHeader, CardTitle, Alert, AlertDescription, AlertIcon } from '@/shared/ui'
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
    <div className="page-container flex items-center justify-center">
      <div className="w-full max-w-md">
        <Card>
          <CardHeader>
            <CardTitle className="text-center text-3xl">CTF Platform</CardTitle>
          </CardHeader>
          <div className="space-y-4 px-6 pb-6">
            {error && (
              <Alert variant="destructive">
                <AlertIcon variant="destructive" />
                <AlertDescription>
                  {error instanceof Error ? error.message : 'Login failed. Please try again.'}
                </AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label
                  htmlFor="team_name"
                  className="text-sm font-medium text-gray-700 dark:text-gray-300"
                >
                  Team Name
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

              <div className="space-y-2">
                <label
                  htmlFor="password"
                  className="text-sm font-medium text-gray-700 dark:text-gray-300"
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

              <Button
                type="submit"
                className="w-full"
                disabled={isPending}
              >
                {isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Logging in...
                  </>
                ) : (
                  'Login'
                )}
              </Button>
            </form>
          </div>
        </Card>
      </div>
    </div>
  )
}
