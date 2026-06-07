# Deployment Guide

## Local Development Setup

### Prerequisites
- Node.js >= 18
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Setup environment:**
```bash
cp .env.example .env
```

4. **Update .env if backend is not local:**
```env
VITE_API_URL=http://your-api-url:8000
```

### Running Locally

```bash
npm run dev
```

Access at: http://localhost:5173

## Production Build

### Build

```bash
npm run build
```

Output directory: `dist/`

### Verify Build

```bash
npm run preview
```

This starts a local server to preview the production build.

### Type Checking Before Build

```bash
npm run type-check
```

### Lint Check

```bash
npm run lint
```

## Environment Variables

### Development (.env)
```env
VITE_API_URL=http://localhost:8000
```

### Production (.env.production)
```env
VITE_API_URL=https://api.yourdomain.com
```

Vite automatically uses different env files based on build mode.

## Deployment Platforms

### Vercel

1. **Push to GitHub:**
```bash
git add .
git commit -m "feat: add frontend"
git push origin main
```

2. **Connect Vercel:**
   - Go to https://vercel.com
   - Click "New Project"
   - Import your GitHub repo
   - Select `frontend` as root directory
   - Add environment variables in project settings
   - Deploy

3. **Environment Variables:**
   ```
   VITE_API_URL=https://api.yourdomain.com
   ```

4. **Auto-deployments:**
   - Main branch deploys automatically
   - Preview branches for PRs

### Netlify

1. **Build command:**
```bash
npm run build
```

2. **Publish directory:**
```
dist
```

3. **Environment variables:**
   - Add `VITE_API_URL` in Netlify dashboard

4. **Deploy:**
   - Connect GitHub repository
   - Netlify auto-deploys on push

### Docker

Create `Dockerfile`:
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
EXPOSE 3000

FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist
CMD ["serve", "-s", "dist", "-l", "3000"]
```

Build and run:
```bash
docker build -t ctf-frontend .
docker run -p 3000:3000 -e VITE_API_URL=http://api:8000 ctf-frontend
```

### Traditional Server (nginx)

1. **Build:**
```bash
npm run build
```

2. **Upload `dist/` to server**

3. **nginx configuration:**
```nginx
server {
  listen 80;
  server_name yourdomain.com;
  
  root /var/www/ctf-frontend/dist;
  index index.html;
  
  location / {
    try_files $uri $uri/ /index.html;
  }
  
  location /api {
    proxy_pass http://backend-api:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

4. **Restart nginx:**
```bash
sudo systemctl restart nginx
```

## Performance Optimization

### Pre-deployment Checklist

- [ ] Run type check: `npm run type-check`
- [ ] Run linter: `npm run lint`
- [ ] Build succeeds: `npm run build`
- [ ] No console errors/warnings
- [ ] Test on multiple browsers
- [ ] Test on mobile devices
- [ ] Verify API endpoint is correct
- [ ] Test authentication flow
- [ ] Test all pages and features

### Bundle Analysis

Check build size:
```bash
npm run build
# Check dist/ folder size
du -sh dist/
```

Expected sizes:
- HTML: ~5KB
- JS: ~150KB minified
- CSS: ~20KB minified
- Total (gzipped): ~50-60KB

### Caching Strategy

Set long-term caching in nginx:
```nginx
location ~* \.(js|css|woff|woff2|ttf|svg|eot)$ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}

location /index.html {
  expires 0;
  add_header Cache-Control "no-cache, no-store";
}
```

## Testing Deployment

### Test Login Flow
1. Navigate to https://yourdomain.com/login
2. Enter team credentials
3. Should redirect to /dashboard
4. Page should load team info

### Test Dashboard
1. Verify team card displays
2. Try submitting a flag
3. Check success/error alerts
4. Verify history loads

### Test Scoreboard
1. Navigate to /scoreboard
2. Verify table loads
3. Verify auto-refresh every 15 seconds
4. Check responsive design

### Test Theme Toggle
1. Click theme toggle in header
2. Verify dark mode activates
3. Hard refresh page
4. Theme should persist

### Test Responsive Design
- Desktop (1920x1080)
- Tablet (768x1024)
- Mobile (375x667)

## Monitoring

### Set Up Error Tracking
1. Install Sentry: `npm install @sentry/react`
2. Initialize in `src/main.tsx`
3. Configure error boundaries

### Browser Console
Monitor for:
- JavaScript errors
- Network failures
- Slow queries
- 401/403 errors

### Network Tab
Monitor:
- API response times
- Failed requests
- Header sizes
- Cache hits/misses

## Troubleshooting Deployment

### Issue: Build Fails
```bash
# Clear cache
npm cache clean --force
rm -rf node_modules
npm install
npm run build
```

### Issue: API Calls Fail (CORS)
Ensure backend allows CORS:
```python
# In backend
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Routes Don't Work on Refresh
Configure server to serve index.html for all routes:
```nginx
try_files $uri $uri/ /index.html;
```

### Issue: Env Variables Not Loading
1. Check `.env` file exists
2. Variables must start with `VITE_`
3. Restart dev server after changing env
4. For production: set in platform settings

### Issue: API URL Wrong
```bash
# Check what URL is being used
npm run build
# Look for VITE_API_URL in dist files
grep -r "localhost" dist/ || echo "No localhost found"
```

## Rollback Procedure

### Vercel
1. Go to project deployments
2. Click "Rollback" on previous deployment

### Netlify
1. Go to Deploy settings
2. Click previous build
3. Click "Publish deploy"

### Manual Server
1. Keep previous build backup
2. Switch symlink: `ln -s /var/www/build-v2 /var/www/current`

## Maintenance

### Regular Updates
```bash
# Check for updates
npm outdated

# Update packages
npm update

# Major version updates
npm install react@latest
```

### Clear Cache on Updates
Force browser cache clear:
- Add timestamp to index.html: `?v=20240602`
- Use service workers (advanced)
- Configure cache headers on server

### Monitor Performance
- PageSpeed Insights
- Lighthouse
- WebPageTest
- Datadog/New Relic

## Security Checklist

- [x] API URL uses HTTPS in production
- [x] Token stored securely (localStorage)
- [x] No secrets in code/env
- [x] CORS properly configured
- [x] CSP headers set
- [x] X-Frame-Options set
- [x] X-Content-Type-Options set
- [x] Strict-Transport-Security set

### Recommended Headers (nginx)
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' https: data: 'unsafe-inline'" always;
```

## Performance Metrics

Target metrics:
- First Contentful Paint (FCP): < 1s
- Largest Contentful Paint (LCP): < 2.5s
- Cumulative Layout Shift (CLS): < 0.1
- Time to Interactive (TTI): < 3s

## Backup & Recovery

### Backup Strategy
```bash
# Daily backups
0 0 * * * tar -czf /backups/frontend-$(date +%Y%m%d).tar.gz /var/www/ctf-frontend/dist
```

### Recovery
```bash
tar -xzf /backups/frontend-20240601.tar.gz -C /var/www/
systemctl restart nginx
```

## Conclusion

Deployment checklist:
1. ✅ Environment configured
2. ✅ Build succeeds
3. ✅ Type check passes
4. ✅ Test login flow
5. ✅ Test all features
6. ✅ Monitor performance
7. ✅ Set up error tracking
8. ✅ Configure security headers
9. ✅ Set up backups
10. ✅ Document deployment
