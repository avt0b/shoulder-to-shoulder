import { useEffect, useState } from 'react'
import { BarChart3, Ban, KeyRound, Plus, Shield, Trash2, Undo2 } from 'lucide-react'
import { adminApi } from '@/features/auth/api'
import {
  AdminAnalytics,
  AdminFlag,
  AdminSubmission,
  AdminTeam,
} from '@/shared/types'
import {
  Alert,
  AlertDescription,
  AlertIcon,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/shared/ui'

const ADMIN_TOKEN_STORAGE_KEY = 'admin-token'

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message
  }
  return 'Request failed'
}

export function AdminPage() {
  const [adminToken, setAdminToken] = useState(
    () => localStorage.getItem(ADMIN_TOKEN_STORAGE_KEY) || ''
  )
  const [analytics, setAnalytics] = useState<AdminAnalytics | null>(null)
  const [flags, setFlags] = useState<AdminFlag[]>([])
  const [teams, setTeams] = useState<AdminTeam[]>([])
  const [submissions, setSubmissions] = useState<AdminSubmission[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [flagForm, setFlagForm] = useState({
    flag: '',
    description: '',
    points: 100,
  })

  const loadAdminData = async (token = adminToken) => {
    if (!token.trim()) {
      return
    }

    setIsLoading(true)
    setMessage(null)

    try {
      const [analyticsResponse, flagsResponse, teamsResponse, submissionsResponse] = await Promise.all([
        adminApi.getAnalytics(token),
        adminApi.getFlags(token),
        adminApi.getTeams(token),
        adminApi.getSubmissions(token),
      ])

      setAnalytics(analyticsResponse.data)
      setFlags(flagsResponse.data)
      setTeams(teamsResponse.data)
      setSubmissions(submissionsResponse.data)
      localStorage.setItem(ADMIN_TOKEN_STORAGE_KEY, token)
    } catch (error) {
      setMessage({ type: 'error', text: getErrorMessage(error) })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (adminToken) {
      void loadAdminData(adminToken)
    }
  }, [])

  const handleTokenSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    void loadAdminData()
  }

  const handleCreateFlag = async (event: React.FormEvent) => {
    event.preventDefault()

    try {
      await adminApi.createFlag(adminToken, {
        flag: flagForm.flag,
        description: flagForm.description || null,
        points: Number(flagForm.points),
      })
      setFlagForm({ flag: '', description: '', points: 100 })
      setMessage({ type: 'success', text: 'Task created' })
      await loadAdminData()
    } catch (error) {
      setMessage({ type: 'error', text: getErrorMessage(error) })
    }
  }

  const handleDeleteFlag = async (flagId: string) => {
    try {
      await adminApi.deleteFlag(adminToken, flagId)
      setMessage({ type: 'success', text: 'Task deleted' })
      await loadAdminData()
    } catch (error) {
      setMessage({ type: 'error', text: getErrorMessage(error) })
    }
  }

  const handleBanTeam = async (team: AdminTeam) => {
    const reason = window.prompt(`Ban reason for ${team.name}`, team.ban_reason || '')
    if (reason === null) {
      return
    }

    try {
      await adminApi.banTeam(adminToken, team.id, reason || null)
      setMessage({ type: 'success', text: `${team.name} banned` })
      await loadAdminData()
    } catch (error) {
      setMessage({ type: 'error', text: getErrorMessage(error) })
    }
  }

  const handleUnbanTeam = async (team: AdminTeam) => {
    try {
      await adminApi.unbanTeam(adminToken, team.id)
      setMessage({ type: 'success', text: `${team.name} unbanned` })
      await loadAdminData()
    } catch (error) {
      setMessage({ type: 'error', text: getErrorMessage(error) })
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <header className="border-b border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900">
        <div className="container py-4">
          <div className="flex items-center gap-3">
            <Shield className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Admin Panel</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">Tasks, teams, bans, and live platform metrics</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container space-y-6 py-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <KeyRound className="h-5 w-5" />
              Admin Access
            </CardTitle>
            <CardDescription>Token is sent as X-Admin-Token</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleTokenSubmit} className="flex flex-col gap-3 sm:flex-row">
              <Input
                type="password"
                value={adminToken}
                onChange={(event) => setAdminToken(event.target.value)}
                placeholder="Admin token"
                className="flex-1"
              />
              <Button type="submit" disabled={isLoading || !adminToken.trim()}>
                Load Admin Data
              </Button>
            </form>
            {message && (
              <div className="mt-4">
                <Alert variant={message.type === 'success' ? 'success' : 'destructive'}>
                  <AlertIcon variant={message.type === 'success' ? 'success' : 'destructive'} />
                  <AlertDescription>{message.text}</AlertDescription>
                </Alert>
              </div>
            )}
          </CardContent>
        </Card>

        {isLoading && !analytics ? (
          <Skeleton className="h-40 w-full" />
        ) : (
          analytics && (
            <section className="grid gap-4 md:grid-cols-4">
              <MetricCard label="Teams" value={analytics.teams_count} />
              <MetricCard label="Banned" value={analytics.banned_teams_count} />
              <MetricCard label="Tasks" value={analytics.flags_count} />
              <MetricCard label="Submissions" value={analytics.submissions_count} />
              <MetricCard label="Correct" value={analytics.correct_submissions_count} />
              <MetricCard label="Wrong" value={analytics.wrong_submissions_count} />
              <MetricCard label="Total score" value={analytics.total_score} />
            </section>
          )
        )}

        <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                Add Task
              </CardTitle>
              <CardDescription>Flag key, description, and points</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateFlag} className="space-y-3">
                <Input
                  value={flagForm.flag}
                  onChange={(event) => setFlagForm((prev) => ({ ...prev, flag: event.target.value }))}
                  placeholder="CTF{flag_key}"
                  required
                />
                <textarea
                  value={flagForm.description}
                  onChange={(event) => setFlagForm((prev) => ({ ...prev, description: event.target.value }))}
                  placeholder="Task description"
                  className="min-h-28 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-900 dark:text-white"
                />
                <Input
                  type="number"
                  min={1}
                  value={flagForm.points}
                  onChange={(event) => setFlagForm((prev) => ({ ...prev, points: Number(event.target.value) }))}
                  required
                />
                <Button type="submit" disabled={!adminToken.trim() || !flagForm.flag.trim()}>
                  Create Task
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Tasks</CardTitle>
              <CardDescription>Existing flag keys and solve counts</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Flag</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead className="text-right">Points</TableHead>
                      <TableHead className="text-right">Solves</TableHead>
                      <TableHead className="w-16" />
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {flags.map((flag) => (
                      <TableRow key={flag.id}>
                        <TableCell className="font-mono text-xs">{flag.flag}</TableCell>
                        <TableCell>{flag.description || 'No description'}</TableCell>
                        <TableCell className="text-right">{flag.points}</TableCell>
                        <TableCell className="text-right">{flag.solves}</TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => void handleDeleteFlag(flag.id)}
                            aria-label="Delete task"
                          >
                            <Trash2 className="h-4 w-4 text-red-600" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Teams</CardTitle>
            <CardDescription>Scores, solves, attempts, and ban controls</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Team</TableHead>
                    <TableHead className="text-right">Rank</TableHead>
                    <TableHead className="text-right">Score</TableHead>
                    <TableHead className="text-right">Solves</TableHead>
                    <TableHead className="text-right">Attempts</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-28" />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {teams.map((team) => (
                    <TableRow key={team.id}>
                      <TableCell className="font-medium">{team.name}</TableCell>
                      <TableCell className="text-right">#{team.rank}</TableCell>
                      <TableCell className="text-right">{team.score}</TableCell>
                      <TableCell className="text-right">{team.solves_count}</TableCell>
                      <TableCell className="text-right">{team.submissions_count}</TableCell>
                      <TableCell>
                        {team.is_banned ? (
                          <span className="text-sm font-semibold text-red-600">{team.ban_reason || 'Banned'}</span>
                        ) : (
                          <span className="text-sm font-semibold text-green-600">Active</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {team.is_banned ? (
                          <Button variant="outline" size="sm" onClick={() => void handleUnbanTeam(team)}>
                            <Undo2 className="mr-2 h-4 w-4" />
                            Unban
                          </Button>
                        ) : (
                          <Button variant="destructive" size="sm" onClick={() => void handleBanTeam(team)}>
                            <Ban className="mr-2 h-4 w-4" />
                            Ban
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Submissions</CardTitle>
            <CardDescription>Last 100 attempts across all teams</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Team</TableHead>
                    <TableHead>Flag</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Time</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {submissions.map((submission) => (
                    <TableRow key={submission.id}>
                      <TableCell className="font-medium">{submission.team_name}</TableCell>
                      <TableCell className="font-mono text-xs">{submission.flag}</TableCell>
                      <TableCell>
                        {submission.correct ? (
                          <span className="text-sm font-semibold text-green-600">Correct</span>
                        ) : (
                          <span className="text-sm font-semibold text-red-600">Wrong</span>
                        )}
                      </TableCell>
                      <TableCell>{new Date(submission.created_at).toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: number }) {
  return (
    <Card>
      <CardContent className="flex items-center gap-3 p-4">
        <BarChart3 className="h-5 w-5 text-blue-600 dark:text-blue-400" />
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
        </div>
      </CardContent>
    </Card>
  )
}
