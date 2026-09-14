import { Moon, Sun, LogOut, Trophy, LayoutDashboard } from 'lucide-react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useTheme } from '@/shared/hooks/useTheme'
import { authStore } from '@/shared/stores/authStore'
import { Button } from '@/shared/ui'
import { cn } from '@/lib/utils'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/scoreboard', label: 'Scoreboard', icon: Trophy },
]

interface HeaderProps {
  /** Show the team navigation (Dashboard / Scoreboard). Hidden for admin,
   *  whose token cannot access team-scoped endpoints. */
  showNav?: boolean
  /** Where the brand mark links to. */
  home?: string
}

export function Header({ showNav = true, home = '/dashboard' }: HeaderProps) {
  const { isDark, toggleTheme } = useTheme()
  const navigate = useNavigate()
  const logout = authStore((state) => state.logout)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="sticky top-0 z-50 border-b border-neutral-200 bg-neutral-50/80 backdrop-blur dark:border-neutral-800 dark:bg-neutral-950/80">
      <div className="container flex h-16 items-center justify-between gap-4">
        <NavLink to={home} className="flex items-center gap-2.5">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-neutral-900 text-sm font-bold text-white dark:bg-white dark:text-neutral-900">
            S2
          </span>
          <span className="text-sm font-semibold tracking-tight text-neutral-900 dark:text-white">
            CTF Platform
          </span>
        </NavLink>

        <nav className="flex items-center gap-1">
          {showNav && navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  'inline-flex h-9 items-center gap-2 rounded-lg px-3 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-neutral-900 text-white dark:bg-white dark:text-neutral-900'
                    : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 dark:text-neutral-300 dark:hover:bg-neutral-800 dark:hover:text-white'
                )
              }
            >
              <Icon className="h-4 w-4" />
              <span className="hidden sm:inline">{label}</span>
            </NavLink>
          ))}

          {showNav && <span className="mx-1 h-5 w-px bg-neutral-200 dark:bg-neutral-800" />}

          <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
          <Button variant="ghost" size="icon" onClick={handleLogout} aria-label="Logout">
            <LogOut className="h-4 w-4" />
          </Button>
        </nav>
      </div>
    </header>
  )
}
