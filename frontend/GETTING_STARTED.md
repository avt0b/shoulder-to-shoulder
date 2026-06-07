# CTF Platform Frontend - Getting Started

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit as needed (optional, defaults work for local dev)
# VITE_API_URL=http://localhost:8000
```

### 3. Start Development Server
```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## Backend Setup

Make sure the backend is running on `http://localhost:8000`:

```bash
# In another terminal, from backend directory
cd backend
uvicorn app.main:app --reload
```

## Frontend Only Development

If backend is not available locally:

1. Update `.env`:
```env
VITE_API_URL=http://your-backend-url:8000
```

2. Restart dev server:
```bash
npm run dev
```

## Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Type check
npm run type-check

# Lint code
npm run lint
```

## Browser

The app will be available at:
- Development: `http://localhost:5173`
- Production: Build output in `dist/` directory

## Testing Login

Use any credentials during development:
- Team Name: `test_team`
- Password: `password123`

(Actual credentials are validated by backend)

## Troubleshooting

### Port 5173 already in use
```bash
# Use custom port
npm run dev -- --port 3000
```

### API connection refused
- Check backend is running on `http://localhost:8000`
- Update `VITE_API_URL` in `.env`

### Stuck on login
- Check browser console for errors (F12)
- Check network tab to see API calls
- Ensure backend is responding to `/api/auth/login`

## File Structure Quick Reference

```
src/
├── app/              # App wrapper and routing
├── pages/            # Page components (Login, Dashboard, Scoreboard)
├── features/         # Feature modules (auth, team, flags, scoreboard)
├── shared/
│   ├── components/   # Reusable UI components
│   ├── ui/          # shadcn/ui base components
│   ├── hooks/       # Custom React hooks
│   ├── types/       # TypeScript types
│   ├── services/    # API services (Axios)
│   ├── stores/      # Zustand stores
│   └── lib/         # Utils and helpers
└── index.css        # Global TailwindCSS
```

## Next Steps

1. Customize colors in `tailwind.config.ts`
2. Add more features in `src/features/`
3. Create additional pages in `src/pages/`
4. Add more UI components in `src/shared/ui/`

## Production Build

```bash
# Build
npm run build

# Preview before deploy
npm run preview

# Deploy dist/ folder to your hosting
```

## Need Help?

Check the main README.md for full documentation.
