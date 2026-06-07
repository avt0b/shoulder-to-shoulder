# Development Guide

## Code Examples

### 1. Creating a Custom Hook

```typescript
// src/shared/hooks/useCustom.ts
import { useQuery } from '@tanstack/react-query'
import { myApi } from '@/features/my/api'

export const useCustomData = (id: string) => {
  return useQuery({
    queryKey: ['customData', id],
    queryFn: async () => {
      const response = await myApi.getCustomData(id)
      return response.data
    },
    enabled: !!id,
  })
}
```

### 2. Using a Hook in a Component

```typescript
import { useCustomData } from '@/shared/hooks'
import { Skeleton } from '@/shared/ui'

export function MyComponent({ id }: { id: string }) {
  const { data, isLoading, error } = useCustomData(id)

  if (isLoading) {
    return <Skeleton className="h-32 w-full" />
  }

  if (error) {
    return <div>Error loading data</div>
  }

  return <div>{data?.name}</div>
}
```

### 3. Creating an API Module

```typescript
// src/features/my/api.ts
import { request } from '@/shared/services/api'
import { MyData, MyRequest } from '@/shared/types'

export const myApi = {
  // GET request
  getData: () =>
    request.get<MyData>('/api/my'),

  // POST request
  createData: (data: MyRequest) =>
    request.post<MyData>('/api/my', data),

  // PUT request
  updateData: (id: string, data: MyRequest) =>
    request.put<MyData>(`/api/my/${id}`, data),

  // DELETE request
  deleteData: (id: string) =>
    request.delete(`/api/my/${id}`),
}
```

### 4. Using Mutations

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { myApi } from '@/features/my/api'

export const useCreateData = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: MyRequest) => myApi.createData(data),
    onSuccess: () => {
      // Invalidate cache to refetch
      queryClient.invalidateQueries({ queryKey: ['myData'] })
    },
  })
}
```

Using in component:

```typescript
function CreateForm() {
  const { mutate, isPending } = useCreateData()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutate(formData, {
      onSuccess: () => {
        console.log('Created successfully')
      },
      onError: (error) => {
        console.error('Error:', error)
      },
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <Button disabled={isPending}>
        {isPending ? 'Creating...' : 'Create'}
      </Button>
    </form>
  )
}
```

### 5. Using the Auth Store

```typescript
import { authStore } from '@/shared/stores/authStore'

function MyComponent() {
  const token = authStore((state) => state.token)
  const logout = authStore((state) => state.logout)
  const isAuthed = authStore((state) => state.isAuthed())

  return (
    <div>
      {isAuthed ? (
        <button onClick={() => logout()}>Logout</button>
      ) : (
        <span>Not authenticated</span>
      )}
    </div>
  )
}
```

### 6. Using Theme Hook

```typescript
import { useTheme } from '@/shared/hooks'

function ThemeToggle() {
  const { isDark, toggleTheme } = useTheme()

  return (
    <button onClick={toggleTheme}>
      {isDark ? 'Light' : 'Dark'} Mode
    </button>
  )
}
```

### 7. Protected Component

```typescript
import { ProtectedRoute } from '@/shared/components'
import { adminPage } from './AdminPage'

export function AdminRoute() {
  return (
    <ProtectedRoute>
      <AdminPage />
    </ProtectedRoute>
  )
}
```

### 8. Using UI Components

```typescript
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Alert,
  AlertDescription,
  AlertIcon,
} from '@/shared/ui'

export function FormCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Form Title</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="space-y-4">
          <Input
            type="email"
            placeholder="Enter email"
            required
          />
          <Input
            type="password"
            placeholder="Enter password"
            required
          />
          <Button className="w-full">Submit</Button>
        </form>

        <Alert variant="destructive" className="mt-4">
          <AlertIcon variant="destructive" />
          <AlertDescription>
            Error message here
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  )
}
```

### 9. Table Example

```typescript
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/shared/ui'

export function DataTable({ data }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((item) => (
          <TableRow key={item.id}>
            <TableCell>{item.name}</TableCell>
            <TableCell>{item.email}</TableCell>
            <TableCell>{item.status}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
```

### 10. Error Handling

```typescript
import { getErrorMessage, isAxiosError } from '@/shared/lib'

async function fetchData() {
  try {
    const response = await api.getData()
    return response.data
  } catch (error) {
    const message = getErrorMessage(error)
    console.error(message)

    if (isAxiosError(error)) {
      console.log('Status:', error.response?.status)
    }
  }
}
```

## Common Patterns

### Loading States

```typescript
if (isLoading) {
  return <Skeleton className="h-32 w-full" />
}
```

### Error Handling

```typescript
{error && (
  <Alert variant="destructive">
    <AlertIcon variant="destructive" />
    <AlertDescription>
      {getErrorMessage(error)}
    </AlertDescription>
  </Alert>
)}
```

### Empty States

```typescript
{data && data.length === 0 ? (
  <p className="text-center text-gray-500">
    No data available
  </p>
) : (
  <ComponentWithData data={data} />
)}
```

### Conditional Rendering

```typescript
{isAuthed ? (
  <ProtectedContent />
) : (
  <AuthPrompt />
)}
```

### Form Validation

```typescript
const [errors, setErrors] = useState<FormErrors>({})

const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault()
  const newErrors = validateForm(formData)
  
  if (Object.keys(newErrors).length > 0) {
    setErrors(newErrors)
    return
  }
  
  submitForm(formData)
}
```

## Debugging Tips

### 1. React DevTools
- Install React DevTools browser extension
- Inspect component hierarchy and props

### 2. Network Tab (Browser DevTools)
- Check API requests and responses
- Verify headers and tokens

### 3. Console Logging
```typescript
console.log('Data:', data)
console.table(items) // Better for arrays
```

### 4. Query DevTools
Add to your app (dev only):
```typescript
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

<QueryClientProvider client={queryClient}>
  <App />
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

### 5. TypeScript Errors
Run `npm run type-check` to catch type errors

## Performance Tips

1. **Memoize components:**
   ```typescript
   const MemoComponent = React.memo(MyComponent)
   ```

2. **Lazy load routes:**
   Already done in router configuration

3. **Optimize queries:**
   - Set appropriate `staleTime`
   - Use `enabled` to prevent unnecessary queries
   - Leverage `queryKey` for proper caching

4. **Use proper dependencies:**
   - Add all dependencies to hooks
   - ESLint will warn about missing ones

## Testing Components

```typescript
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from '@/shared/lib/queryClient'

const renderWithProviders = (component) => {
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  )
}

// Usage
test('renders data', async () => {
  renderWithProviders(<MyComponent />)
  
  await waitFor(() => {
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })
})
```

## Troubleshooting

### Issue: Components not updating
- Check if `useQuery` is properly set up
- Verify `queryKey` uniqueness
- Check for missing dependencies in hooks

### Issue: Token not sent in requests
- Check localStorage for token
- Verify interceptor is configured
- Check Authorization header format

### Issue: Infinite loading
- Check network tab for failed requests
- Verify API endpoint is correct
- Check for proper error handling

### Issue: State not persisting
- Check localStorage implementation
- Verify Zustand middleware setup
- Clear browser storage if needed
