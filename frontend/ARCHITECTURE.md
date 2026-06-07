# Frontend Architecture

## Overview

This frontend follows a **feature-based architecture** with clear separation of concerns. Each feature is self-contained with its own API layer, components, and hooks.

## Directory Structure

```
src/
├── app/                        # Application core
│   ├── App.tsx                # Root component with providers
│   ├── router.tsx             # React Router configuration
│   └── index.ts               # Module exports
│
├── pages/                      # Page components (routes)
│   ├── LoginPage.tsx          # Login page
│   ├── DashboardPage.tsx      # Dashboard page
│   ├── ScoreboardPage.tsx     # Scoreboard page
│   └── index.ts               # Module exports
│
├── features/                   # Feature modules
│   ├── auth/                  # Authentication feature
│   │   ├── api.ts             # Auth API calls
│   │   └── index.ts           # Module exports
│   ├── team/                  # Team feature
│   │   └── index.ts
│   ├── flags/                 # Flags feature
│   │   └── index.ts
│   └── scoreboard/            # Scoreboard feature
│       └── index.ts
│
├── shared/                     # Shared resources
│   ├── components/            # Reusable components
│   │   ├── ProtectedRoute.tsx # Route protection
│   │   ├── Header.tsx         # Header component
│   │   └── index.ts           # Module exports
│   │
│   ├── ui/                    # UI component library
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Alert.tsx
│   │   ├── Table.tsx
│   │   ├── Skeleton.tsx
│   │   └── index.ts           # Barrel export
│   │
│   ├── hooks/                 # Custom hooks
│   │   ├── useTheme.ts        # Theme management
│   │   ├── useApi.ts          # API query hooks
│   │   └── index.ts           # Barrel export
│   │
│   ├── types/                 # TypeScript types
│   │   ├── api.ts             # API request/response types
│   │   ├── errors.ts          # Error types
│   │   └── index.ts           # Barrel export
│   │
│   ├── services/              # External services
│   │   ├── api.ts             # Axios instance & interceptors
│   │   └── index.ts           # Module exports
│   │
│   ├── stores/                # State management
│   │   ├── authStore.ts       # Auth Zustand store
│   │   └── index.ts           # Module exports
│   │
│   └── lib/                   # Utilities & helpers
│       ├── queryClient.ts     # TanStack Query configuration
│       ├── errorHandler.ts    # Error handling utilities
│       ├── cn.ts              # Class name utility
│       ├── utils/
│       │   ├── cn.ts
│       │   └── index.ts
│       └── index.ts           # Barrel export
│
├── main.tsx                   # Entry point
└── index.css                  # Global styles with TailwindCSS
```

## Key Patterns

### 1. Feature-Based Organization

Each feature (auth, flags, scoreboard) is isolated with its own:
- **API layer** (`features/*/api.ts`) - HTTP requests
- **Hooks** (`shared/hooks/useApi.ts`) - React Query wrappers
- **Types** (`shared/types/api.ts`) - TypeScript interfaces

**Example: Adding a new flag feature**

```
features/flags/
├── api.ts              # Contains flagsApi with submit, getSubmissions
├── index.ts            # Exports
└── components/         # Feature-specific components (if needed)
```

### 2. State Management

- **Server State** - TanStack Query (queries, mutations)
- **Client State** - Zustand (authentication state)
- **URL State** - React Router (navigation)

### 3. Type Safety

All files with API interaction are strictly typed:

```typescript
// types/api.ts
export interface LoginRequest {
  team_name: string
  password: string
}

export interface LoginResponse {
  access_token: string
}

// features/auth/api.ts
export const authApi = {
  login: (data: LoginRequest) =>
    request.post<LoginResponse>('/api/auth/login', data),
}
```

### 4. Error Handling

Centralized error handling through:
- **Axios interceptors** - Catch 401, handle globally
- **Error utilities** - `getErrorMessage()`, `isAxiosError()`
- **UI feedback** - Alert components for user-facing errors

### 5. Protected Routes

Routes are wrapped with `<ProtectedRoute>` to require authentication:

```typescript
// app/router.tsx
{
  path: '/dashboard',
  element: (
    <ProtectedRoute>
      <DashboardPage />
    </ProtectedRoute>
  ),
}
```

## Data Flow

### Login Flow
```
LoginPage (form)
  ↓
useLogin hook (mutation)
  ↓
authApi.login (axios request)
  ↓
Backend API
  ↓
Response with JWT
  ↓
authStore.login(token) (store token)
  ↓
Navigate to /dashboard
```

### Data Fetching Flow
```
Component mounts
  ↓
useTeam hook (useQuery)
  ↓
Check query cache
  ↓
If stale/missing, fetch from API
  ↓
teamApi.getMe (axios GET request)
  ↓
Interceptor adds Authorization header
  ↓
Backend API
  ↓
Query cache updated
  ↓
Component re-renders with data
```

## Best Practices

### ✅ Do's

- Use custom hooks for all API interactions
- Keep components focused on UI, not logic
- Use TypeScript strict mode
- Centralize API configuration
- Organize by features, not file types
- Use barrel exports (`index.ts`)
- Separate concerns clearly

### ❌ Don'ts

- Don't make API calls directly in components
- Don't use inline setTimeout for debouncing
- Don't pass entire objects as props when you need one field
- Don't create class components
- Don't ignore TypeScript errors
- Don't mix server and client state
- Don't hardcode API URLs

## Adding a New Feature

### Step 1: Create Feature Directory
```bash
mkdir -p src/features/newfeature
```

### Step 2: Add API Layer
Create `src/features/newfeature/api.ts`:
```typescript
import { request } from '@/shared/services/api'
import { NewFeatureData } from '@/shared/types'

export const newFeatureApi = {
  getData: () =>
    request.get<NewFeatureData>('/api/newfeature'),
}
```

### Step 3: Add Hooks
Update `src/shared/hooks/useApi.ts`:
```typescript
export const useNewFeature = () => {
  return useQuery({
    queryKey: ['newfeature'],
    queryFn: async () => {
      const response = await newFeatureApi.getData()
      return response.data
    },
  })
}
```

### Step 4: Add Types
Update `src/shared/types/api.ts`:
```typescript
export interface NewFeatureData {
  id: string
  name: string
}
```

### Step 5: Use in Components
```typescript
function NewFeaturePage() {
  const { data, isLoading } = useNewFeature()
  
  return (
    <YourComponent data={data} loading={isLoading} />
  )
}
```

## Performance Considerations

- **Code Splitting** - Routes lazy-loaded by Vite
- **Query Caching** - TanStack Query caches results (5 min stale time)
- **Request Deduplication** - Auto-deduped identical requests
- **Refetch Strategy** - Scoreboard refetches every 15 seconds
- **Component Memoization** - Use React.memo for expensive renders

## Testing Structure

Components are designed for easy testing:
- Hooks are separate from components
- API calls are centralized
- State management is isolated
- UI components are reusable

## Deployment

1. **Build:**
   ```bash
   npm run build
   ```

2. **Output:** `dist/` directory ready for hosting

3. **Environment:** Set `VITE_API_URL` for backend URL

4. **Hosting:** Any static file server (Vercel, Netlify, etc.)

## Module Aliasing

Path aliases are configured in `tsconfig.json`:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

Use `import { Button } from '@/shared/ui'` instead of relative paths.

## Conclusion

This architecture ensures:
- ✅ Scalability
- ✅ Maintainability
- ✅ Type Safety
- ✅ Code Reusability
- ✅ Clear Separation of Concerns
- ✅ Easy Testing
