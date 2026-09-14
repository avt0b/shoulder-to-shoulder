import { useEffect, useState } from 'react'
import { Ban, Copy, Edit3, Eye, EyeOff, Image as ImageIcon, Plus, RefreshCw, Shield, Trash2, Undo2, Upload, X } from 'lucide-react'
import { adminApi } from '@/features/auth/api'
import { authStore } from '@/shared/stores/authStore'
import { API_URL } from '@/shared/services/api'
import { Layout } from '@/shared/components'
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

const textareaClass =
  'min-h-24 w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-900 transition-colors placeholder:text-neutral-400 hover:border-neutral-300 focus:border-neutral-400 focus:outline-none dark:border-neutral-800 dark:bg-neutral-950 dark:text-neutral-100 dark:placeholder:text-neutral-500 dark:hover:border-neutral-700 dark:focus:border-neutral-600'

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
    if (typeof window !== 'undefined') {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
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
      setMessage({ type: 'success', text: 'Image uploaded to the server' })
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

  const handleDeleteFlag = async (flag: AdminFlag) => {
    if (typeof window !== 'undefined' && !window.confirm(`Delete task "${flag.title}"? This cannot be undone.`)) {
      return
    }

    try {
      await adminApi.deleteFlag(adminToken, flag.id)
      if (editingFlagId === flag.id) {
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
    <Layout nav={false} home="/admin">
      <div className="space-y-6">
        {/* Page title + toolbar */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-neutral-900 text-white dark:bg-white dark:text-neutral-900">
              <Shield className="h-5 w-5" />
            </span>
            <div>
              <h1 className="text-2xl font-semibold tracking-tight text-neutral-900 dark:text-white">
                Admin Panel
              </h1>
              <p className="text-sm text-neutral-500 dark:text-neutral-400">
                Tasks, teams, bans, and live platform metrics
              </p>
            </div>
          </div>
          <Button variant="outline" onClick={() => void loadAdminData()} disabled={isLoading || !adminToken.trim()}>
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {message && (
          <Alert variant={message.type === 'success' ? 'success' : 'destructive'}>
            <AlertIcon variant={message.type === 'success' ? 'success' : 'destructive'} />
            <AlertDescription>{message.text}</AlertDescription>
          </Alert>
        )}

        {/* Metrics */}
        {isLoading && !analytics ? (
          <Skeleton className="h-24 w-full" />
        ) : (
          analytics && (
            <section className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7">
              <MetricCard label="Teams" value={analytics.teams_count} />
              <MetricCard label="Banned" value={analytics.banned_teams_count} accent="rose" />
              <MetricCard label="Tasks" value={analytics.flags_count} />
              <MetricCard label="Submissions" value={analytics.submissions_count} />
              <MetricCard label="Correct" value={analytics.correct_submissions_count} accent="emerald" />
              <MetricCard label="Wrong" value={analytics.wrong_submissions_count} accent="rose" />
              <MetricCard label="Total score" value={analytics.total_score} accent="indigo" />
            </section>
          )
        )}

        {/* Forms */}
        <div className="grid gap-6 xl:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-4 w-4 text-neutral-400" />
                Register team
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
                  Register team
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-4 w-4 text-neutral-400" />
                {editingFlagId ? 'Edit task' : 'Add task'}
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

                {/* Image: uploaded to and served from the platform server */}
                <div className="space-y-2">
                  <label className="flex cursor-pointer items-center justify-center gap-2 rounded-lg border border-dashed border-neutral-300 px-3 py-3 text-sm text-neutral-600 transition-colors hover:border-neutral-400 hover:bg-neutral-50 dark:border-neutral-700 dark:text-neutral-300 dark:hover:border-neutral-600 dark:hover:bg-neutral-800">
                    <Upload className="h-4 w-4" />
                    Upload image
                    <input type="file" accept="image/*" className="hidden" onChange={(event) => void handleImageUpload(event)} />
                  </label>
                  {flagForm.image_url && (
                    <div className="flex items-center gap-3 rounded-lg border border-neutral-200 p-2 dark:border-neutral-800">
                      <img
                        src={resolveAssetUrl(flagForm.image_url) || ''}
                        alt=""
                        className="h-12 w-12 rounded-md object-cover"
                      />
                      <span className="min-w-0 flex-1 truncate font-mono text-xs text-neutral-500 dark:text-neutral-400">
                        {flagForm.image_url}
                      </span>
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => setFlagForm((prev) => ({ ...prev, image_url: '' }))}
                        aria-label="Remove image"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                  <p className="text-xs text-neutral-400 dark:text-neutral-500">
                    Stored on the platform server under <span className="font-mono">/uploads</span>.
                  </p>
                </div>

                <Input
                  value={flagForm.flag}
                  onChange={(event) => setFlagForm((prev) => ({ ...prev, flag: event.target.value }))}
                  placeholder="CTF{flag_key}"
                  className="font-mono"
                  required
                />
                <textarea
                  value={flagForm.description}
                  onChange={(event) => setFlagForm((prev) => ({ ...prev, description: event.target.value }))}
                  placeholder="Short teaser shown on the task card"
                  className={textareaClass}
                />
                <textarea
                  value={flagForm.text}
                  onChange={(event) => setFlagForm((prev) => ({ ...prev, text: event.target.value }))}
                  placeholder="Full task text, story, and hints shown in the popup"
                  className={`${textareaClass} min-h-36`}
                />
                <div className="flex items-center gap-3">
                  <label className="flex-1">
                    <span className="mb-1 block text-xs font-medium text-neutral-500 dark:text-neutral-400">Points</span>
                    <Input
                      type="number"
                      min={1}
                      value={flagForm.points}
                      onChange={(event) => setFlagForm((prev) => ({ ...prev, points: Number(event.target.value) }))}
                      required
                    />
                  </label>
                  <label className="flex items-center gap-2 pt-5 text-sm font-medium text-neutral-700 dark:text-neutral-200">
                    <input
                      type="checkbox"
                      checked={flagForm.is_visible}
                      onChange={(event) => setFlagForm((prev) => ({ ...prev, is_visible: event.target.checked }))}
                      className="h-4 w-4 rounded border-neutral-300 text-neutral-900 focus:ring-neutral-400 dark:border-neutral-700 dark:bg-neutral-950"
                    />
                    Visible to teams
                  </label>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button type="submit" disabled={!adminToken.trim() || !flagForm.title.trim() || !flagForm.flag.trim()}>
                    {editingFlagId ? 'Save task' : 'Create task'}
                  </Button>
                  {editingFlagId && (
                    <Button type="button" variant="outline" onClick={cancelEditFlag}>
                      <X className="h-4 w-4" />
                      Cancel
                    </Button>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Tasks table */}
        <Card>
          <CardHeader className="gap-4 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
            <div>
              <CardTitle>Tasks</CardTitle>
              <CardDescription>Flag keys, visibility, and solve counts</CardDescription>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button type="button" variant="outline" size="sm" onClick={() => void handleSetTasksVisibility(true)} disabled={!adminToken.trim()}>
                <Eye className="h-4 w-4" />
                Show all
              </Button>
              <Button type="button" variant="outline" size="sm" onClick={() => void handleSetTasksVisibility(false)} disabled={!adminToken.trim()}>
                <EyeOff className="h-4 w-4" />
                Hide all
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent dark:hover:bg-transparent">
                  <TableHead>Task</TableHead>
                  <TableHead>Image</TableHead>
                  <TableHead>Flag</TableHead>
                  <TableHead>Visibility</TableHead>
                  <TableHead className="text-right">Points</TableHead>
                  <TableHead className="text-right">Solves</TableHead>
                  <TableHead className="w-24" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {flags.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="py-8 text-center text-sm text-neutral-500 dark:text-neutral-400">
                      No tasks yet
                    </TableCell>
                  </TableRow>
                ) : (
                  flags.map((flag) => (
                    <TableRow key={flag.id}>
                      <TableCell>
                        <div className="font-medium">{flag.title}</div>
                        <div className="max-w-xs truncate text-xs text-neutral-500 dark:text-neutral-400">
                          {flag.description || 'No teaser'}
                        </div>
                      </TableCell>
                      <TableCell>
                        {flag.image_url ? (
                          <a className="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 hover:underline dark:text-indigo-400" href={resolveAssetUrl(flag.image_url) || '#'} target="_blank" rel="noreferrer">
                            <ImageIcon className="h-3.5 w-3.5" />
                            View
                          </a>
                        ) : (
                          <span className="text-xs text-neutral-400">—</span>
                        )}
                      </TableCell>
                      <TableCell className="font-mono text-xs">{flag.flag}</TableCell>
                      <TableCell>
                        <StatusPill tone={flag.is_visible ? 'emerald' : 'neutral'}>
                          {flag.is_visible ? 'Visible' : 'Hidden'}
                        </StatusPill>
                      </TableCell>
                      <TableCell className="text-right tabular-nums">{flag.points}</TableCell>
                      <TableCell className="text-right tabular-nums">{flag.solves}</TableCell>
                      <TableCell>
                        <div className="flex justify-end gap-1">
                          <Button variant="ghost" size="icon" onClick={() => startEditFlag(flag)} aria-label="Edit task">
                            <Edit3 className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon" onClick={() => void handleDeleteFlag(flag)} aria-label="Delete task">
                            <Trash2 className="h-4 w-4 text-rose-600 dark:text-rose-400" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Teams table */}
        <Card>
          <CardHeader>
            <CardTitle>Teams</CardTitle>
            <CardDescription>Scores, solves, attempts, and ban controls</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent dark:hover:bg-transparent">
                  <TableHead>Team</TableHead>
                  <TableHead className="text-right">Rank</TableHead>
                  <TableHead className="text-right">Score</TableHead>
                  <TableHead className="text-right">Solves</TableHead>
                  <TableHead className="text-right">Attempts</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-24" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {teams.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="py-8 text-center text-sm text-neutral-500 dark:text-neutral-400">
                      No teams yet
                    </TableCell>
                  </TableRow>
                ) : (
                  teams.map((team) => (
                    <TableRow key={team.id}>
                      <TableCell className="font-medium">{team.name}</TableCell>
                      <TableCell className="text-right tabular-nums">#{team.rank}</TableCell>
                      <TableCell className="text-right tabular-nums">{team.score}</TableCell>
                      <TableCell className="text-right tabular-nums">{team.solves_count}</TableCell>
                      <TableCell className="text-right tabular-nums">{team.submissions_count}</TableCell>
                      <TableCell>
                        {team.is_banned ? (
                          <StatusPill tone="rose">{team.ban_reason || 'Banned'}</StatusPill>
                        ) : (
                          <StatusPill tone="emerald">Active</StatusPill>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex justify-end">
                          {team.is_banned ? (
                            <Button variant="outline" size="sm" onClick={() => void handleUnbanTeam(team)}>
                              <Undo2 className="h-4 w-4" />
                              Unban
                            </Button>
                          ) : (
                            <Button variant="destructive" size="sm" onClick={() => void handleBanTeam(team)}>
                              <Ban className="h-4 w-4" />
                              Ban
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Recent submissions */}
        <Card>
          <CardHeader>
            <CardTitle>Recent submissions</CardTitle>
            <CardDescription>Last 100 attempts across all teams</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent dark:hover:bg-transparent">
                  <TableHead>Team</TableHead>
                  <TableHead>Flag</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {submissions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} className="py-8 text-center text-sm text-neutral-500 dark:text-neutral-400">
                      No submissions yet
                    </TableCell>
                  </TableRow>
                ) : (
                  submissions.map((submission) => (
                    <TableRow key={submission.id}>
                      <TableCell className="font-medium">{submission.team_name}</TableCell>
                      <TableCell className="font-mono text-xs">{submission.flag}</TableCell>
                      <TableCell>
                        <StatusPill tone={submission.correct ? 'emerald' : 'rose'}>
                          {submission.correct ? 'Correct' : 'Wrong'}
                        </StatusPill>
                      </TableCell>
                      <TableCell className="text-right text-xs text-neutral-500 dark:text-neutral-400">
                        {new Date(submission.created_at).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </Layout>
  )
}

function MetricCard({
  label,
  value,
  accent = 'default',
}: {
  label: string
  value: number
  accent?: 'default' | 'indigo' | 'emerald' | 'rose'
}) {
  const accentClass =
    accent === 'indigo'
      ? 'text-indigo-600 dark:text-indigo-400'
      : accent === 'emerald'
        ? 'text-emerald-600 dark:text-emerald-400'
        : accent === 'rose'
          ? 'text-rose-600 dark:text-rose-400'
          : 'text-neutral-900 dark:text-white'

  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-900">
      <p className="eyebrow">{label}</p>
      <p className={`mt-1 text-2xl font-semibold tabular-nums ${accentClass}`}>{value}</p>
    </div>
  )
}

function StatusPill({
  children,
  tone = 'neutral',
}: {
  children: React.ReactNode
  tone?: 'neutral' | 'emerald' | 'rose'
}) {
  const tones = {
    neutral: 'bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300',
    emerald: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300',
    rose: 'bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300',
  }
  return (
    <span className={`inline-flex max-w-[12rem] items-center truncate rounded-full px-2.5 py-1 text-xs font-medium ${tones[tone]}`}>
      {children}
    </span>
  )
}
