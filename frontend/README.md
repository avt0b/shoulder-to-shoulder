# CTF Platform Frontend

Production-ready frontend для платформы CTF-флагов, разработана с использованием современного stack-а инструментов.

## Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **React Router v7** - Routing
- **TanStack Query v5** - Server state management
- **Zustand** - Client state management
- **Axios** - HTTP client
- **TailwindCSS** - Styling
- **shadcn/ui** - UI components

## Architecture

```
frontend/
├── src/
│   ├── app/                 # Application core
│   │   ├── App.tsx          # Main component
│   │   └── router.tsx       # Router configuration
│   ├── pages/               # Page components
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   └── ScoreboardPage.tsx
│   ├── features/            # Feature modules
│   │   ├── auth/            # Auth feature
│   │   │   └── api.ts
│   │   ├── team/            # Team feature
│   │   ├── flags/           # Flags feature
│   │   └── scoreboard/      # Scoreboard feature
│   ├── shared/              # Shared resources
│   │   ├── components/      # Reusable components
│   │   ├── ui/              # UI components
│   │   ├── hooks/           # Custom hooks
│   │   ├── types/           # TypeScript types
│   │   ├── services/        # HTTP services
│   │   ├── stores/          # Zustand stores
│   │   └── lib/             # Util functions
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── index.html               # HTML template
├── package.json             # Dependencies
├── vite.config.ts           # Vite config
├── tailwind.config.ts       # TailwindCSS config
├── tsconfig.json            # TypeScript config
└── .env.example             # Environment variables

```

## Features

### 1. Authentication
- Team login with credentials
- JWT token handling
- Auto-redirect on 401
- Persistent authentication with localStorage

### 2. Dashboard
- Team info card (name, score, rank)
- Flag submission form
- Real-time feedback on submission result
- Recent submissions history

### 3. Scoreboard
- Real-time leaderboard
- Auto-refresh every 15 seconds
- Rank badges (🥇🥈🥉)
- Team standings

### 4. Theme Support
- Dark/Light theme toggle
- System preference detection
- Persistent theme selection

## Installation

### Prerequisites
- Node.js >= 18
- npm or yarn

### Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Create environment file:**
```bash
cp .env.example .env
```

4. **Edit .env if needed:**
```env
VITE_API_URL=http://localhost:8000
```

## Running the Application

### Development Server

```bash
npm run dev
```

Server will start at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

### Type Checking

```bash
npm run type-check
```

### Linting

```bash
npm run lint
```

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`.

### Endpoints

#### Authentication
- `POST /api/auth/login` - Team login

#### Team
- `GET /api/team/me` - Get current team info

#### Flags
- `POST /api/flags/submit` - Submit a flag
- `GET /api/submissions` - Get submission history

#### Scoreboard
- `GET /api/scoreboard` - Get current standings

## State Management

### Zustand Store (authStore)
```typescript
// Login
const token = authStore((state) => state.token)
authStore.getState().login(token)

// Logout
authStore.getState().logout()

// Check if authenticated
authStore.getState().isAuthed()
```

### TanStack Query Hooks
```typescript
// Auth
const { mutate: login } = useLogin()

// Team
const { data: team } = useTeam()

// Flags
const { mutate: submitFlag } = useSubmitFlag()
const { data: submissions } = useSubmissions()

// Scoreboard
const { data: scoreboard } = useScoreboard() // Auto-refreshes every 15s
```

## Key Components

### ProtectedRoute
Wrapper component that checks authentication and redirects to login if needed.

```typescript
<ProtectedRoute>
  <DashboardPage />
</ProtectedRoute>
```

### Shadcn/UI Components
- Button - Action buttons with variants
- Input - Form input fields
- Card - Container component
- Alert - Notification alerts
- Table - Data tables
- Skeleton - Loading skeleton

### Header
Sticky header with:
- Theme toggle
- Logout button

## Styling

### TailwindCSS
- Custom configuration in `tailwind.config.ts`
- Dark mode support via `dark:` prefix
- Global styles in `index.css`

### Color Scheme
- Light: White background, gray text
- Dark: Gray-950 background, white text
- Primary: Blue-600 (light) / Blue-400 (dark)
- Success: Green
- Error: Red

## Error Handling

### API Error Handling
- Axios interceptors catch errors
- 401 responses trigger logout and redirect to login
- Error messages displayed in alerts

### Form Validation
- Required fields validation
- Error feedback to user

## TypeScript

Strict TypeScript configuration with:
- `noUnusedLocals` - Detect unused variables
- `noUnusedParameters` - Detect unused parameters
- `noFallthroughCasesInSwitch` - Detect fallthrough in switch
- `strict` mode enabled

## Performance

- **Lazy loading** - Pages loaded on demand
- **Request caching** - TanStack Query handles caching
- **Auto-refetch** - Scoreboard refetches every 15 seconds
- **Interceptors** - Token added automatically to requests

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development Tips

1. **Adding new pages:**
   - Create component in `src/pages/`
   - Add route in `src/app/router.tsx`
   - Wrap in `<ProtectedRoute>` if needed

2. **Adding new API calls:**
   - Add function in `src/features/*/api.ts`
   - Create hook in `src/shared/hooks/useApi.ts`
   - Use in components with proper error handling

3. **Reusable components:**
   - Place in `src/shared/components/`
   - Export from `index.ts`
   - Use across pages

4. **Custom hooks:**
   - Place in `src/shared/hooks/`
   - Export from `index.ts`
   - Prefix with `use`

## License

MIT

## Support

For issues or questions, open an issue in the repository.
