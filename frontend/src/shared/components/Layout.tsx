import { ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { Header } from './Header'
import { Footer } from './Footer'

interface LayoutProps {
  children: ReactNode
  /** Extra classes for the inner container (e.g. spacing overrides). */
  className?: string
  /** Show the team navigation in the header (hidden for admin). */
  nav?: boolean
  /** Where the header brand links to. */
  home?: string
}

/**
 * Standard authenticated page shell: top navigation, a centered content
 * container, and the shared authors footer pinned to the bottom.
 */
export function Layout({ children, className, nav = true, home = '/dashboard' }: LayoutProps) {
  return (
    <div className="flex min-h-screen flex-col bg-neutral-50 dark:bg-neutral-950">
      <Header showNav={nav} home={home} />
      <main className="flex-1">
        <div className={cn('container py-8 sm:py-10', className)}>{children}</div>
      </main>
      <Footer />
    </div>
  )
}
