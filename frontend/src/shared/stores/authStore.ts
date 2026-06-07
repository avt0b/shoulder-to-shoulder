import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { AuthStore } from '@/shared/types'

export const authStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      token: null,

      setToken: (token: string | null) => {
        set({ token })
      },

      login: (token: string) => {
        set({ token })
      },

      logout: () => {
        set({ token: null })
      },

      isAuthed: () => {
        return get().token !== null && get().token !== ''
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)
