import { Moon, Sun, LogOut, Trophy, LayoutDashboard } from 'lucide-react'
import { useTheme } from '@/shared/hooks/useTheme'
import { authStore } from '@/shared/stores/authStore'
import { Button } from '@/shared/ui'
import { useNavigate } from 'react-router-dom'

export function Header() {
  const { isDark, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const logout = authStore((state) => state.logout)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="sticky top-0 z-50 border-b border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900">
      <div className="container py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            CTF Platform
          </h1>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate('/dashboard')}
              aria-label="Dashboard"
            >
              <LayoutDashboard className="h-5 w-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate('/scoreboard')}
              aria-label="Scoreboard"
            >
              <Trophy className="h-5 w-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              aria-label="Toggle theme"
            >
              {isDark ? (
                <Sun className="h-5 w-5" />
              ) : (
                <Moon className="h-5 w-5" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
              aria-label="Logout"
            >
              <LogOut className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
