# Testing Guide

## Unit Testing Setup

### Install Testing Dependencies

```bash
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event
npm install -D @vitest/ui vitest jsdom
```

### Create vite.config.test.ts

```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

### Create src/test/setup.ts

```typescript
import '@testing-library/jest-dom'
```

### Run Tests

```bash
npm run test
npm run test:ui
```

## Manual Testing Checklist

### Login Page
- [ ] Navigate to /login
- [ ] Form renders with Team Name and Password inputs
- [ ] Submit with empty fields shows validation
- [ ] Submit with valid credentials redirects to dashboard
- [ ] Invalid credentials shows error alert
- [ ] Loading state shows while submitting
- [ ] Error message displays on failure

### Dashboard Page
- [ ] Page requires authentication (redirects to login if not)
- [ ] Team card displays: name, score, rank
- [ ] Flag input field is present
- [ ] Submit button is disabled when input empty
- [ ] Submitting flag shows loading state
- [ ] Correct flag shows green success alert with points
- [ ] Wrong flag shows red error alert
- [ ] Alert disappears after 5 seconds
- [ ] Recent submissions list loads
- [ ] Each submission shows flag, status, timestamp

### Scoreboard Page
- [ ] Page requires authentication
- [ ] Table displays with: Rank, Team, Score columns
- [ ] Teams sorted by score descending
- [ ] Top 3 teams show medal icons (🥇🥈🥉)
- [ ] Auto-refreshes every 15 seconds
- [ ] Refresh happens silently without jarring updates

### Navigation
- [ ] Header visible on dashboard and scoreboard
- [ ] Team name displayed in header (when available)
- [ ] Theme toggle button works (dark/light)
- [ ] Logout button logs out and redirects to login
- [ ] Dark mode persists across page refresh
- [ ] Unauthenticated users can't access protected pages

### Theme
- [ ] Initial theme matches system preference
- [ ] Clicking toggle switches theme
- [ ] All components styled properly in both themes
- [ ] Dark text visible in light theme
- [ ] Light text visible in dark theme
- [ ] Theme persists after page refresh

### Error Handling
- [ ] 401 response logs out user
- [ ] API errors display user-friendly messages
- [ ] Network errors handled gracefully
- [ ] Skeletons show while loading
- [ ] Empty states show when no data

### Responsive Design
- [ ] On mobile (375px): layout stacks vertically
- [ ] On tablet (768px): layout adjusts appropriately
- [ ] On desktop (1920px): full width layout
- [ ] Text readable on all sizes
- [ ] Buttons convenient to tap/click
- [ ] Forms don't have overflow

### Performance
- [ ] Page loads in < 3 seconds
- [ ] Theme toggle instant
- [ ] Logout instant
- [ ] Queries cached appropriately
- [ ] No console errors/warnings

## Testing Different Scenarios

### Successful Login Flow
1. Go to /login
2. Enter valid team name and password
3. Click Login
4. Should redirect to /dashboard
5. Team info should display
6. Check localStorage for token

### Failed Login Flow
1. Go to /login
2. Enter invalid credentials
3. Click Login
4. Should show error message
5. Should stay on /login
6. Should not have token in localStorage

### Successful Flag Submission
1. From dashboard, enter valid flag format
2. Click Submit
3. Should show green success alert
4. Should show point reward
5. Flag should appear in recent submissions
6. Alert should disappear after 5 seconds

### Failed Flag Submission
1. From dashboard, enter wrong flag
2. Click Submit
3. Should show red error alert
4. Should show error message
5. Flag should appear in recent submissions as wrong
6. No points awarded

### Session Timeout (401 Error)
1. Submit flag with valid token
2. (Simulate token expiration on backend)
3. Next API call should get 401
4. User should be logged out
5. Should redirect to /login
6. localStorage token should be cleared

### Dark Mode Testing
1. Start app in light mode
2. Click theme toggle
3. Entire app should switch to dark
4. Check all colors are appropriate
5. Refresh page
6. Dark mode should persist

### Scoreboard Auto-Refresh
1. Open scoreboard
2. Note timestamp of first load
3. Wait 15 seconds
4. Data should refresh silently
5. Rankings should update

## Browser Compatibility

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Chrome
- [ ] Mobile Safari

## Screen Size Testing

- [ ] iPhone SE (375x667)
- [ ] iPad (768x1024)
- [ ] Desktop (1920x1080)
- [ ] Ultra-wide (2560x1440)

## Network Conditions

### Fast 3G
```bash
# In browser DevTools > Network > throttling
- Latency: 400ms
- Download: 1.6Mbps
- Upload: 750kbps
```
- App should be usable
- Loading states should be visible

### Slow 4G
```bash
- Latency: 20ms
- Download: 4Mbps
- Upload: 3Mbps
```
- App should load reasonably fast
- No timeout errors

### Offline
Disconnect network
- [ ] Cached queries still work
- [ ] No console errors
- [ ] Failed requests show error states
- [ ] Reconnect shows data updates

## API Testing

### Mock Backend Responses

```typescript
// Example with MSW (Mock Service Worker)
import { setupServer } from 'msw/node'
import { http, HttpResponse } from 'msw'

const server = setupServer(
  http.post('/api/auth/login', () => {
    return HttpResponse.json({
      access_token: 'fake-token',
    })
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

## Accessibility Testing

- [ ] Keyboard navigation works (Tab, Enter)
- [ ] Focus states visible
- [ ] Button labels clear
- [ ] Input labels present
- [ ] Form accessible without mouse
- [ ] Colors have sufficient contrast
- [ ] Text resizable
- [ ] Screen reader compatible (optional)

## Security Testing

- [ ] Token not visible in Network tab as plain text
- [ ] Authorization header sent on API calls
- [ ] Logout clears token
- [ ] No secrets in code
- [ ] No sensitive data in URLs
- [ ] HTTPS enforced in production

## Performance Testing

### Lighthouse Audit
```bash
# In Chrome DevTools > Lighthouse
- Performance: > 90
- Accessibility: > 90
- Best Practices: > 90
- SEO: > 90
```

### Bundle Size
```bash
npm run build
du -sh dist/
# Should be < 200KB uncompressed
# Should be < 70KB gzipped
```

### Page Load Metrics
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Cumulative Layout Shift (CLS): < 0.1
- Time to Interactive (TTI): < 3.5s

## Error Scenario Testing

### Network Errors
1. Disable network in DevTools
2. Try to submit flag
3. Should show error alert
4. Error message should be helpful
5. Reconnect should allow retry

### Invalid Response
1. Mock API to return invalid JSON
2. Should handle gracefully
3. No crash
4. Error shown to user

### Timeout
1. Mock slow API response (>30s)
2. Request should timeout
3. Error shown to user
4. UI remains responsive

### Missing Token
1. Clear localStorage
2. Navigate to /dashboard
3. Should redirect to /login

### Expired Token
1. Have old/expired token in localStorage
2. Make API call
3. Should get 401
4. Should logout
5. Should redirect to /login

## End-to-End Session

1. Start fresh (clear localStorage)
2. Go to /login
3. Login with valid credentials
4. Verify on dashboard
5. Submit correct flag
6. Check success alert
7. Go to scoreboard
8. Verify data loads
9. Toggle theme
10. Logout
11. Verify redirected to login
12. Try to access /dashboard
13. Should redirect to login

## Automated Testing Example

```typescript
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from '@/shared/lib/queryClient'
import { LoginPage } from '@/pages'

describe('LoginPage', () => {
  const renderPage = () => {
    render(
      <QueryClientProvider client={queryClient}>
        <LoginPage />
      </QueryClientProvider>
    )
  }

  test('renders login form', () => {
    renderPage()
    expect(screen.getByLabelText(/team name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
  })

  test('submits form with valid data', async () => {
    renderPage()
    const user = userEvent.setup()

    await user.type(screen.getByLabelText(/team name/i), 'test_team')
    await user.type(screen.getByLabelText(/password/i), 'password')
    await user.click(screen.getByRole('button', { name: /login/i }))

    await waitFor(() => {
      expect(screen.getByText(/logging in/i)).toBeInTheDocument()
    })
  })
})
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test & Build

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run type-check
      - run: npm run lint
      - run: npm run build
```

## Test Results Template

```
✅ Login Page
  ✓ Form renders
  ✓ Valid login redirects
  ✓ Invalid login shows error

✅ Dashboard Page
  ✓ Team info displays
  ✓ Flag submission works
  ✓ Success alert shows

✅ Scoreboard Page
  ✓ Table renders
  ✓ Auto-refresh works

✅ Theme Toggle
  ✓ Switches modes
  ✓ Persists

✅ Error Handling
  ✓ 401 logs out

✅ Responsive Design
  ✓ Mobile view
  ✓ Tablet view
  ✓ Desktop view

All tests passed! ✨
```
