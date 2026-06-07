# Project Structure Complete Guide

## 📁 Full Directory Tree

```
frontend/
├── public/                          # Static assets
│
├── src/
│   ├── app/                         # Application core
│   │   ├── App.tsx                 # Root component with providers
│   │   ├── router.tsx              # React Router v7 configuration
│   │   └── index.ts                # Module exports
│   │
│   ├── pages/                       # Page components (route-level)
│   │   ├── LoginPage.tsx           # Team login page
│   │   ├── DashboardPage.tsx       # Main dashboard page
│   │   ├── ScoreboardPage.tsx      # Leaderboard page
│   │   └── index.ts                # Barrel exports
│   │
│   ├── features/                    # Feature modules (business logic)
│   │   ├── auth/
│   │   │   ├── api.ts              # Authentication API calls
│   │   │   └── index.ts
│   │   ├── team/
│   │   │   └── index.ts
│   │   ├── flags/
│   │   │   └── index.ts
│   │   └── scoreboard/
│   │       └── index.ts
│   │
│   ├── shared/                      # Shared across all features
│   │   ├── components/             # Reusable business components
│   │   │   ├── ProtectedRoute.tsx # Route guard component
│   │   │   ├── Header.tsx         # App header with theme toggle
│   │   │   └── index.ts           # Barrel export
│   │   │
│   │   ├── ui/                    # shadcn/ui components library
│   │   │   ├── Button.tsx         # Cta button component
│   │   │   ├── Input.tsx          # Form input component
│   │   │   ├── Card.tsx           # Container component
│   │   │   ├── Alert.tsx          # Notification alerts
│   │   │   ├── Table.tsx          # Data table component
│   │   │   ├── Skeleton.tsx       # Loading skeletons
│   │   │   └── index.ts           # Barrel export
│   │   │
│   │   ├── hooks/                 # Custom React hooks
│   │   │   ├── useTheme.ts        # Theme management (dark/light)
│   │   │   ├── useApi.ts         # API query & mutation hooks
│   │   │   └── index.ts           # Barrel export
│   │   │
│   │   ├── types/                 # TypeScript interfaces & types
│   │   │   ├── api.ts             # API request/response types
│   │   │   ├── errors.ts          # Error types
│   │   │   └── index.ts           # Barrel export
│   │   │
│   │   ├── services/              # External services & clients
│   │   │   ├── api.ts             # Axios HTTP client with interceptors
│   │   │   └── index.ts           # Module exports
│   │   │
│   │   ├── stores/                # State management (Zustand)
│   │   │   ├── authStore.ts       # Auth state with persist middleware
│   │   │   └── index.ts           # Module exports
│   │   │
│   │   └── lib/                   # Utility functions & helpers
│   │       ├── queryClient.ts     # TanStack Query client config
│   │       ├── errorHandler.ts    # Error handling utilities
│   │       ├── utils/
│   │       │   ├── cn.ts          # Class name merger
│   │       │   └── index.ts
│   │       └── index.ts           # Barrel export
│   │
│   ├── main.tsx                    # React app entry point
│   └── index.css                   # Global TailwindCSS styles
│
├── index.html                       # HTML template
│
├── package.json                     # NPM dependencies & scripts
├── tsconfig.json                    # TypeScript configuration
├── tsconfig.node.json               # TypeScript node config
├── vite.config.ts                   # Vite build configuration
├── tailwind.config.ts               # TailwindCSS theme config
├── postcss.config.js                # PostCSS configuration
├── eslint.config.js                 # ESLint rules
├── .editorconfig                    # Editor configuration
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
│
├── README.md                        # Main documentation
├── GETTING_STARTED.md               # Quick start guide
├── ARCHITECTURE.md                  # Architecture guide
└── DEVELOPMENT.md                   # Development best practices

```

## 📋 File Descriptions

### Core Files

#### `src/main.tsx`
Entry point for the React application. Initializes React root and mounts the App component.

#### `src/index.css`
Global TailwindCSS styles, base layer styling, and utility classes.

#### `src/app/App.tsx`
Root component that wraps the app with:
- QueryClientProvider (TanStack Query)
- RouterProvider (React Router)

#### `src/app/router.tsx`
React Router v7 configuration with:
- `/login` - Public route
- `/dashboard` - Protected route
- `/scoreboard` - Protected route

### Pages

#### `src/pages/LoginPage.tsx`
Unauthenticated login page with:
- Team name input
- Password input
- Login form handling
- Error alerts

#### `src/pages/DashboardPage.tsx`
Main dashboard with:
- Team info card (score, rank, name)
- Flag submission form
- Recent submissions history
- Success/error alerts

#### `src/pages/ScoreboardPage.tsx`
Leaderboard display with:
- Ranked team standings
- Auto-refresh every 15 seconds
- Medal icons for top 3
- Score sorting

### Features

#### `src/features/auth/api.ts`
Authentication API functions:
- `authApi.login()` - POST /api/auth/login

#### `src/shared/hooks/useApi.ts`
Custom React hooks using TanStack Query:
- `useLogin()` - Login mutation
- `useTeam()` - Fetch current team
- `useSubmitFlag()` - Submit flag mutation
- `useSubmissions()` - Fetch flag history
- `useScoreboard()` - Fetch leaderboard (refetch every 15s)

### Shared Components

#### `src/shared/components/ProtectedRoute.tsx`
Route guard component that:
- Checks for valid authentication token
- Redirects to `/login` if not authenticated

#### `src/shared/components/Header.tsx`
Sticky header with:
- Team name branding
- Theme toggle (dark/light)
- Logout button

### UI Components

#### `src/shared/ui/Button.tsx`
Customizable button component with variants:
- `default` - Primary blue button
- `outline` - Border button
- `destructive` - Red error button
- `ghost` - Transparent button

#### `src/shared/ui/Input.tsx`
Form input field with:
- Border styling
- Focus state
- Disabled state
- Dark mode support

#### `src/shared/ui/Card.tsx`
Container component with sub-components:
- `Card` - Main container
- `CardHeader` - Header section
- `CardTitle` - Title
- `CardDescription` - Subtitle
- `CardContent` - Main content
- `CardFooter` - Footer section

#### `src/shared/ui/Alert.tsx`
Notification component with variants:
- `default` - Neutral alert
- `destructive` - Red error alert
- `success` - Green success alert
- `info` - Blue info alert

#### `src/shared/ui/Table.tsx`
Data table component with sections:
- `Table` - Main table
- `TableHeader` - Head section
- `TableBody` - Body section
- `TableFooter` - Footer section
- `TableRow` - Row
- `TableHead` - Header cell
- `TableCell` - Data cell

#### `src/shared/ui/Skeleton.tsx`
Loading placeholder component with animation.

### Services

#### `src/shared/services/api.ts`
Axios HTTP client with:
- Base URL configuration
- Request interceptor (adds JWT token)
- Response interceptor (handles 401 errors)
- Helper methods (get, post, put, patch, delete)

### Stores

#### `src/shared/stores/authStore.ts`
Zustand authentication store with:
- `token` - JWT access token
- `setToken()` - Update token
- `login()` - Set token on login
- `logout()` - Clear token
- `isAuthed()` - Check if authenticated
- localStorage persistence

### Types

#### `src/shared/types/api.ts`
TypeScript interfaces for:
- `LoginRequest` - Login form data
- `LoginResponse` - Login response with JWT
- `TeamMe` - Current team info
- `SubmitFlagRequest` - Flag submission data
- `SubmitFlagResponse` - Flag check result
- `Submission` - Historical submission entry
- `ScoreboardEntry` - Leaderboard entry
- `AuthStore` - Store types

#### `src/shared/types/errors.ts`
Error type definitions:
- `QueryErrorType` - TanStack Query error type

### Utilities

#### `src/shared/lib/queryClient.ts`
TanStack Query configuration with:
- 5 minute stale time
- 10 minute cache time
- 1 retry attempt
- No auto-refetch on focus

#### `src/shared/lib/errorHandler.ts`
Error handling utilities:
- `getErrorMessage()` - Extract error message
- `isAxiosError()` - Type guard for axios errors

#### `src/shared/lib/utils/cn.ts`
Class name utility for merging conditional classes.

### Configuration Files

#### `package.json`
Dependencies:
- react@19
- react-router-dom@7
- @tanstack/react-query@5
- zustand@4
- axios@1.6
- tailwindcss@3
- shadcn/ui components

Scripts:
- `dev` - Start dev server
- `build` - Build for production
- `preview` - Preview production build
- `type-check` - Run TypeScript check
- `lint` - Lint code

#### `vite.config.ts`
Vite configuration with:
- React plugin
- Path aliases (@/)
- API proxy to backend

#### `tailwind.config.ts`
TailwindCSS configuration with:
- Dark mode class support
- Content paths
- No theme extensions (uses defaults)

#### `tsconfig.json`
TypeScript strict configuration with:
- ES2020 target
- DOM types
- Path aliases
- Strict mode enabled
- No unused variables/parameters

### Documentation Files

#### `README.md`
Complete project documentation covering:
- Features overview
- Installation instructions
- Running the application
- API integration details
- State management guide
- Component descriptions
- Browser support
- Development tips

#### `GETTING_STARTED.md`
Quick start guide with:
- Installation steps
- Environment setup
- Starting dev server
- Testing login
- Troubleshooting tips

#### `ARCHITECTURE.md`
Detailed architecture documentation:
- Directory structure explanation
- Design patterns used
- Data flow diagrams
- Best practices (do's and don'ts)
- Adding new features guide
- Performance considerations

#### `DEVELOPMENT.md`
Development best practices with:
- 10 code examples
- Common patterns
- Debugging tips
- Performance optimization
- Testing examples
- Troubleshooting guide

## 🎯 Key Features

### Authentication Flow
1. User enters credentials
2. `LoginPage` calls `useLogin()` hook
3. Hook uses `authApi.login()` to POST to backend
4. JWT token received and stored in `authStore`
5. Axios interceptor auto-adds token to requests
6. User navigated to `/dashboard`
7. On 401 error, user logged out and redirected

### Query System
- **TanStack Query** handles all server state
- **Zustand** handles client state (auth)
- **React Router** handles URL state
- Auto-refetch scoreboard every 15 seconds
- 5-minute stale time for queries
- Automatic cache management

### Protected Routes
- `<ProtectedRoute>` wrapper checks `authStore.token`
- Unauthenticated users redirected to `/login`
- Token persisted in localStorage

### Theme Support
- Light/Dark mode toggle in header
- System preference detection on first load
- Theme preference saved to localStorage
- TailwindCSS `dark:` prefix used throughout

### Error Handling
- Axios interceptors catch errors
- 401 responses trigger logout
- User-friendly error alerts
- Detailed error messages from backend

## 📦 Bundling

### Build Output
```
dist/
├── index.html
├── assets/
│   ├── main-xxxxx.js       # Main bundle
│   ├── index-xxxxx.css     # Styles
│   └── ...other assets
```

### Size (Est.)
- Main JS: ~150KB (minified)
- CSS: ~50KB (minified)
- Gzipped total: ~50-60KB

## ✅ Verification Checklist

- [x] React 19 with TypeScript
- [x] Vite build configuration
- [x] React Router v7
- [x] TanStack Query v5
- [x] Zustand state management
- [x] Axios HTTP client
- [x] TailwindCSS styling
- [x] shadcn/ui components
- [x] Feature-based architecture
- [x] Strict TypeScript
- [x] ProtectedRoute component
- [x] Theme toggle
- [x] All required pages
- [x] All required API hooks
- [x] Error handling
- [x] Loading states
- [x] Complete documentation

## 🚀 Next Steps

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   ```

3. **Start development:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   npm run preview
   ```

---

**Project Status:** ✅ Production Ready
**Last Updated:** June 2, 2026
