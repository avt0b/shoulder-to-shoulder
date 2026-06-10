import { createBrowserRouter, Navigate } from 'react-router-dom'
import { LoginPage, DashboardPage, ScoreboardPage, AdminPage } from '@/pages'
import { ProtectedRoute } from '@/shared/components'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/dashboard" />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/scoreboard',
    element: (
      <ProtectedRoute>
        <ScoreboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/admin',
    element: (
      <ProtectedRoute>
        <AdminPage />
      </ProtectedRoute>
    ),
  },
])
