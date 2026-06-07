# Quick Reference Guide

## Directory Quick Access

```
frontend/
├── src/app/           # Router, App wrapper
├── src/pages/         # Page components
├── src/features/      # API & business logic
├── src/shared/        # Reusable resources
│   ├── components/    # UI components
│   ├── ui/           # shadcn/ui
│   ├── hooks/        # Custom hooks
│   ├── types/        # TypeScript interfaces
│   ├── services/     # Axios client
│   ├── stores/       # Zustand stores
│   └── lib/          # Utilities
```

## Common Commands

```bash
# Development
npm run dev              # Start dev server (http://localhost:5173)
npm run build           # Build for production
npm run preview         # Preview production build
npm run type-check     # TypeScript check
npm run lint           # ESLint check

# Package management
npm install            # Install dependencies
npm update            # Update packages
npm outdated          # Check for updates
```

## Imports Reference

```typescript
// UI Components
import { Button, Input, Card, Alert, Table, Skeleton } from '@/shared/ui'

// Custom Hooks
import { useTheme, useApi, useLogin, useTeam, useSubmitFlag } from '@/shared/hooks'

// Types
import type { LoginRequest, TeamMe, SubmitFlagResponse } from '@/shared/types'

// Services
import { apiClient, request } from '@/shared/services/api'

// Stores
import { authStore } from '@/shared/stores/authStore'

// Utilities
import { cn, getErrorMessage, isAxiosError } from '@/shared/lib'

// Query Client
import { queryClient } from '@/shared/lib/queryClient'

// Components
import { ProtectedRoute, Header } from '@/shared/components'

// Pages
import { LoginPage, DashboardPage, ScoreboardPage } from '@/pages'
```

## Component Usage Quick Examples

### Button
```typescript
<Button>Click me</Button>
<Button variant="outline">Outline</Button>
<Button variant="destructive">Delete</Button>
<Button disabled>Disabled</Button>
```

### Input
```typescript
<Input type="text" placeholder="Name" />
<Input type="email" placeholder="Email" />
<Input type="password" placeholder="Password" />
```

### Card
```typescript
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>
```

### Alert
```typescript
<Alert variant="destructive">
  <AlertIcon variant="destructive" />
  <AlertDescription>Error message</AlertDescription>
</Alert>
```

### Table
```typescript
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Header</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>Data</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

## Hook Usage Quick Examples

### useTheme
```typescript
const { isDark, toggleTheme } = useTheme()
```

### useLogin
```typescript
const { mutate: login, isPending } = useLogin()
login(data, {
  onSuccess: (response) => { /* ... */ },
  onError: (error) => { /* ... */ }
})
```

### useTeam
```typescript
const { data: team, isLoading } = useTeam()
```

### useSubmitFlag
```typescript
const { mutate: submitFlag, isPending } = useSubmitFlag()
```

### useSubmissions
```typescript
const { data: submissions, isLoading } = useSubmissions()
```

### useScoreboard
```typescript
const { data: scoreboard, isLoading } = useScoreboard()
// Auto-refreshes every 15 seconds
```

## API Calls Quick Examples

```typescript
// Post request
const response = await authApi.login({ team_name: 'team1', password: 'pass' })

// Get request
const team = await teamApi.getMe()

// Error handling
try {
  await api.getData()
} catch (error) {
  const message = getErrorMessage(error)
  console.error(message)
}
```

## Store Usage Quick Examples

```typescript
// Get state
const token = authStore((state) => state.token)
const logout = authStore((state) => state.logout)

// Set state
authStore.getState().login('token')
authStore.getState().logout()

// Check auth
const isAuthed = authStore.getState().isAuthed()
```

## Type Definitions Quick Reference

```typescript
// Auth
LoginRequest: { team_name, password }
LoginResponse: { access_token }

// Team
TeamMe: { id, name, score, rank }

// Flags
SubmitFlagRequest: { flag }
SubmitFlagResponse: { success, message, points? }
Submission: { id, flag, correct, created_at }

// Scoreboard
ScoreboardEntry: { rank, team_name, score }
```

## File Organization Quick Guide

**Adding a Feature:**
1. Create feature dir: `src/features/feature/`
2. Add API: `src/features/feature/api.ts`
3. Add hook: `src/shared/hooks/useApi.ts`
4. Add types: `src/shared/types/api.ts`
5. Create page: `src/pages/FeaturePage.tsx`

**Adding a Component:**
1. Reusable → `src/shared/components/Component.tsx`
2. UI only → `src/shared/ui/Component.tsx`
3. Page-specific → Keep in page file

## Environment Variables

```env
# Local dev
VITE_API_URL=http://localhost:8000

# Production
VITE_API_URL=https://api.yourdomain.com

# Staging
VITE_API_URL=https://staging-api.yourdomain.com
```

## Path Aliases

All paths use `@/` alias:
- `@/app` → src/app
- `@/pages` → src/pages
- `@/features` → src/features
- `@/shared` → src/shared
- `@/shared/ui` → src/shared/ui
- `@/shared/hooks` → src/shared/hooks
- `@/shared/types` → src/shared/types
- `@/shared/services` → src/shared/services
- `@/shared/stores` → src/shared/stores
- `@/shared/lib` → src/shared/lib

## Router Quick Reference

```typescript
// Public routes
/login              # Login page

// Protected routes
/dashboard         # Main dashboard
/scoreboard        # Leaderboard
/                  # Redirects to /dashboard
```

## State Flow

```
User Input → Component → Hook → TanStack Query → API → Server
                          ↓
                      Zustand Store
                      (Auth state)
```

## Common Patterns

### Form Submission
```typescript
const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault()
  mutate(data, {
    onSuccess: () => { /* ... */ },
    onError: (error) => { /* ... */ }
  })
}
```

### Loading State
```typescript
{isLoading ? <Skeleton /> : <Content />}
```

### Error Alert
```typescript
{error && (
  <Alert variant="destructive">
    <AlertIcon variant="destructive" />
    <AlertDescription>{getErrorMessage(error)}</AlertDescription>
  </Alert>
)}
```

### Protected Route
```typescript
<ProtectedRoute>
  <ProtectedPage />
</ProtectedRoute>
```

## Debugging

```typescript
// Console logging
console.log('Value:', value)
console.table(array)
console.error('Error:', error)

// In React DevTools
// - Inspect component hierarchy
// - Check props and state

// In Network tab
// - Check API requests/responses
// - Check headers (Authorization, etc)

// TypeScript errors
npm run type-check
```

## Performance Tips

1. **Memoize expensive components:**
   ```typescript
   const Memoized = React.memo(ExpensiveComponent)
   ```

2. **Use queryKey properly:**
   ```typescript
   useQuery({
     queryKey: ['team', teamId],
     // Cache invalidation works better
   })
   ```

3. **Disable unnecessary queries:**
   ```typescript
   useQuery({
     enabled: !!id,  // Only fetch when id exists
   })
   ```

4. **Set appropriate staleTime:**
   ```typescript
   useQuery({
     staleTime: 5 * 60 * 1000,  // 5 minutes
   })
   ```

## Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| Port 5173 in use | `npm run dev -- --port 3000` |
| API connection refused | Check backend is running |
| Types not updating | `npm run type-check` |
| Build fails | `npm cache clean --force && npm install` |
| Theme not persisting | Check localStorage settings |
| Token not sent | Check interceptors in api.ts |
| Infinite loading | Check network tab for errors |
| Page won't load | Check for 404 in browser console |

## Build Output

```
dist/
├── index.html           # Main html file
├── assets/
│   ├── index-xyz.js     # Main bundle
│   ├── index-abc.css    # Styles
│   └── ...other chunks
```

## Deployment Checklist

- [ ] `npm run type-check` passes
- [ ] `npm run lint` passes
- [ ] `npm run build` succeeds
- [ ] .env configured for environment
- [ ] Backend API URL correct
- [ ] Test login flow
- [ ] Test all pages
- [ ] Test mobile view
- [ ] Test dark mode
- [ ] Check browser console (no errors)

## Resources

- README.md - Full documentation
- GETTING_STARTED.md - Quick start
- ARCHITECTURE.md - Design patterns
- DEVELOPMENT.md - Best practices + examples
- DEPLOYMENT.md - Deployment guides
- TESTING.md - Testing strategies
- PROJECT_STRUCTURE.md - File organization

## Version Information

- React: 19.0.0
- TypeScript: 5.3.0
- Vite: 5.0.0
- React Router: 7.0.0
- TanStack Query: 5.28.0
- Zustand: 4.4.0
- Axios: 1.6.0
- TailwindCSS: 3.3.0

---

**Last Updated**: June 2, 2026
**Status**: Production Ready ✅
