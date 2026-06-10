import { useEffect, useState } from 'react'
import { BarChart3, Ban, Copy, Edit3, Eye, EyeOff, Image, KeyRound, Plus, Shield, Trash2, Undo2, Upload, X } from 'lucide-react'
import { adminApi } from '@/features/auth/api'
import { authStore } from '@/shared/stores/authStore'
import { API_URL } from '@/shared/services/api'
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

function getErrorMessage(error: unknown) {
  if (error instanceof Error) {
    return error.message
  }
  return 'Request failed'
}

function resolveAssetUrl(url: string | null) {
  if (!url) return null
  return url.startsWith('/uploads/') ? `${API_URL}${url}` : url
}

const emptyFlagForm = {
  title: '',
  image_url: '',
  flag: '',
  description: '',
  text: '',
  points: 100,
  is_visible: true,
}

export function AdminPage() {
  const adminToken = authStore((state) => state.token) || ''
  const [analytics, setAnalytics] = useState<AdminAnalytics | null>(null)
  const [flags, setFlags] = useState<AdminFlag[]>([])
  const [teams, setTeams] = useState<AdminTeam[]>([])
  const [submissions, setSubmissions] = useState<AdminSubmission[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [editingFlagId, setEditingFlagId] = useState<string | null>(null)
  const [flagForm, setFlagForm] = useState(emptyFlagForm)
  const [teamForm, setTeamForm] = useState({
    team_name: '',
    password: '',
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

  const handleSubmitFlagForm = async (event: React.FormEvent) => {
    event.preventDefault()

    try {
      const payload = {
        title: flagForm.title,
        flag: flagForm.flag,
        description: flagForm.description || null,
        text: flagForm.text || null,
        image_url: flagForm.image_url || null,
        points: Number(flagForm.points),
        is_visible: flagForm.is_visible,
      }

      if (editingFlagId) {
        await adminApi.updateFlag(adminToken, editingFlagId, payload)
        setMessage({ type: 'success', text: 'Task updated' })
      } else {
        await adminApi.createFlag(adminToken, payload)
        setMessage({ type: 'success', text: 'Task created' })
      }

      setEditingFlagId(null)
      setFlagForm(emptyFlagForm)
      await loadAdminData()
    } catch (error) {
      setMessage({ type: 'error', text: getErrorMessage(error) })
    }
  }

  const startEditFlag = (flag: AdminFlag) => {
    setEditingFlagId(flag.id)
    setFlagForm({
      title: flag.title,
      image_url: flag.image_url || '',
      flag: flag.flag,
      description: flag.description || '',
      text: flag.text || '',
      points: flag.points,
      is_visible: flag.is_visible,
    })
  }

  const cancelEditFlag = () => {
    setEditingFlagId(null)
    setFlagForm(emptyFlagForm)
  }

  const handleSetTasksVisibility = async (isVisible: boolean) => {
    try {
      await adminApi.setFlagsVisibility(adminToken, { is_visible: isVisible })
      setMessage({ type: 'success', text: isVisible ? 'Tasks are visible to teams' : 'Tasks are hidden from teams' })
      await loadAdminData()
    } catch (error) {
      setMessage({ type: 'error', text: getErrorMessage(error) })
    }
  }

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      const response = await adminApi.uploadTaskImage(adminToken, file)
      setFlagForm((prev) => ({ ...prev, image_url: response.data.image_url }))
      setMessage({ type: 'success', text: 'Image uploaded' })
    } catch (error) {
      setMessage({ type: 'error', text: getErrorMessage(error) })
    } finally {
      event.target.value = ''
    }
  }

  const generatePassword = () => {
    const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%&'
    const password = Array.from({ length: 14 }, () => alphabet[Math.floor(Math.random() * alphabet.length)]).join('')
    setTeamForm((prev) => ({ ...prev, password }))
  }

  const copyPassword = async () => {
    if (!teamForm.password) return
    await navigator.clipboard.writeText(teamForm.password)
    setMessage({ type: 'success', text: 'Password copied' })
  }

  const handleCreateTeam = async (event: React.FormEvent) => {
    event.preventDefault()

    try {
      await adminApi.createTeam(adminToken, teamForm)
      setTeamForm({ team_name: '', password: '' })
      setMessage({ type: 'success', text: 'Team registered' })
      await loadAdminData()
    } catch (error) {
      setMessage({ type: 'error', text: getErrorMessage(error) })
    }
  }

  const handleDeleteFlag = async (flagId: string) => {
    try {
      await adminApi.deleteFlag(adminToken, flagId)
      if (editingFlagId === flagId) {
        cancelEditFlag()
      }
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
            <CardDescription>Admin is authorized through the regular login form</CardDescription>
          </CardHeader>
          <CardContent>
            <Button type="button" onClick={() => void loadAdminData()} disabled={isLoading || !adminToken.trim()}>
              Load Admin Data
            </Button>
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

        <div className="grid gap-6 xl:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                Register Team
              </CardTitle>
              <CardDescription>Create participant credentials</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateTeam} className="space-y-3">
                <Input
                  value={teamForm.team_name}
                  onChange={(event) => setTeamForm((prev) => ({ ...prev, team_name: event.target.value }))}
                  placeholder="Team login"
                  required
                />
                <div className="flex gap-2">
                  <Input
                    value={teamForm.password}
                    onChange={(event) => setTeamForm((prev) => ({ ...prev, password: event.target.value }))}
                    placeholder="Team password"
                    required
                  />
                  <Button type="button" variant="outline" onClick={generatePassword}>
                    Generate
                  </Button>
                  <Button type="button" variant="ghost" size="icon" onClick={() => void copyPassword()} aria-label="Copy password">
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
                <Button type="submit" disabled={!adminToken.trim() || !teamForm.team_name.trim() || !teamForm.password.trim()}>
                  Register Team
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                {editingFlagId ? 'Edit Task' : 'Add Task'}
              </CardTitle>
              <CardDescription>Image, task text, flag key, points, and visibility</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmitFlagForm} className="space-y-3">
                <Input
                  value={flagForm.title}
                  onChange={(event) => setFlagForm((prev) => ({ ...prev, title: event.target.value }))}
                  placeholder="Task title"
                  required
                />
                <Input
                  value={flagForm.image_url}
                  onChange={(event) => setFlagForm((prev) => ({ ...prev, image_url: event.target.value }))}
                  placeholder="Image URL"
                />
                <label className="flex cursor-pointer items-center justify-center gap-2 rounded-md border border-dashed border-gray-300 px-3 py-3 text-sm text-gray-600 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800">
                  <Upload className="h-4 w-4" />
                  Upload image
                  <input type="file" accept="image/*" className="hidden" onChange={(event) => void handleImageUpload(event)} />
                </label>
                <Input
                  value={flagForm.flag}
                  onChange={(event) => setFlagForm((prev) => ({ ...prev, flag: event.target.value }))}
                  placeholder="CTF{flag_key}"
                  required
                />
                <textarea
                  value={flagForm.description}
                  onChange={(event) => setFlagForm((prev) => ({ ...prev, description: event.target.value }))}
                  placeholder="Short teaser shown on the task card"
                  className="min-h-28 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-900 dark:text-white"
                />
                <textarea
                  value={flagForm.text}
                  onChange={(event) => setFlagForm((prev) => ({ ...prev, text: event.target.value }))}
                  placeholder="Full task text, story, and hints shown in the popup"
                  className="min-h-40 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-900 dark:text-white"
                />
                <Input
                  type="number"
                  min={1}
                  value={flagForm.points}
                  onChange={(event) => setFlagForm((prev) => ({ ...prev, points: Number(event.target.value) }))}
                  required
                />
                <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-200">
                  <input
                    type="checkbox"
                    checked={flagForm.is_visible}
                    onChange={(event) => setFlagForm((prev) => ({ ...prev, is_visible: event.target.checked }))}
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  Visible to teams
                </label>
                <div className="flex flex-wrap gap-2">
                  <Button type="submit" disabled={!adminToken.trim() || !flagForm.title.trim() || !flagForm.flag.trim()}>
                    {editingFlagId ? 'Save Task' : 'Create Task'}
                  </Button>
                  {editingFlagId && (
                    <Button type="button" variant="outline" onClick={cancelEditFlag}>
                      <X className="mr-2 h-4 w-4" />
                      Cancel
                    </Button>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>

          <Card className="xl:col-span-2">
            <CardHeader className="gap-4 md:flex-row md:items-center md:justify-between md:space-y-0">
              <div>
                <CardTitle>Tasks</CardTitle>
                <CardDescription>Existing flag keys, visibility, and solve counts</CardDescription>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => void handleSetTasksVisibility(true)}
                  disabled={!adminToken.trim()}
                >
                  <Eye className="mr-2 h-4 w-4" />
                  Show Tasks
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => void handleSetTasksVisibility(false)}
                  disabled={!adminToken.trim()}
                >
                  <EyeOff className="mr-2 h-4 w-4" />
                  Hide Tasks
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Task</TableHead>
                      <TableHead>Image</TableHead>
                      <TableHead>Flag</TableHead>
                      <TableHead>Visibility</TableHead>
                      <TableHead className="text-right">Points</TableHead>
                      <TableHead className="text-right">Solves</TableHead>
                      <TableHead className="w-28" />
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {flags.map((flag) => (
                      <TableRow key={flag.id}>
                        <TableCell>
                          <div className="font-medium">{flag.title}</div>
                          <div className="max-w-md truncate text-xs text-gray-500 dark:text-gray-400">
                            {flag.description || 'No teaser'}
                          </div>
                        </TableCell>
                        <TableCell>
                          {flag.image_url ? (
                            <a className="inline-flex items-center gap-1 text-xs text-blue-600" href={resolveAssetUrl(flag.image_url) || '#'} target="_blank" rel="noreferrer">
                              <Image className="h-3 w-3" />
                              image
                            </a>
                          ) : (
                            <span className="text-xs text-gray-400">No image</span>
                          )}
                        </TableCell>
                        <TableCell className="font-mono text-xs">{flag.flag}</TableCell>
                        <TableCell>
                          <span className={flag.is_visible ? 'text-sm font-semibold text-green-600' : 'text-sm font-semibold text-gray-500'}>
                            {flag.is_visible ? 'Visible' : 'Hidden'}
                          </span>
                        </TableCell>
                        <TableCell className="text-right">{flag.points}</TableCell>
                        <TableCell className="text-right">{flag.solves}</TableCell>
                        <TableCell>
                          <div className="flex justify-end gap-1">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => startEditFlag(flag)}
                              aria-label="Edit task"
                            >
                              <Edit3 className="h-4 w-4 text-blue-600" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => void handleDeleteFlag(flag.id)}
                              aria-label="Delete task"
                            >
                              <Trash2 className="h-4 w-4 text-red-600" />
                            </Button>
                          </div>
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
