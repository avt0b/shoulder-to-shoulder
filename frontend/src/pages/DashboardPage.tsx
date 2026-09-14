import { useState } from 'react'
import { Layout } from '@/shared/components'
import { useTeam, useSubmitFlag, useSubmissions, useTasks } from '@/shared/hooks'
import { API_URL } from '@/shared/services/api'
import { Button, Input, Card, CardHeader, CardTitle, CardDescription, CardContent, Alert, AlertDescription, AlertIcon, Skeleton } from '@/shared/ui'
import { CheckCircle, Flag, Loader2, X } from 'lucide-react'
import { TeamTask } from '@/shared/types'

function resolveAssetUrl(url: string | null) {
  if (!url) return null
  return url.startsWith('/uploads/') ? `${API_URL}${url}` : url
}

export function DashboardPage() {
  const { data: team, isLoading: teamLoading, refetch: refetchTeam } = useTeam()
  const { data: tasks, isLoading: tasksLoading, refetch: refetchTasks } = useTasks()
  const { data: submissions, isLoading: submissionsLoading, refetch: refetchSubmissions } = useSubmissions()
  const { mutate: submitFlag, isPending: isSubmitting, error } = useSubmitFlag()

  const [flagInputs, setFlagInputs] = useState<Record<string, string>>({})
  const [selectedTask, setSelectedTask] = useState<TeamTask | null>(null)
  const [lastResult, setLastResult] = useState<{ success: boolean; message: string; points?: number } | null>(null)

  const handleSubmitFlag = (e: React.FormEvent, taskId: string) => {
    e.preventDefault()
    const flag = flagInputs[taskId]?.trim() || ''
    if (!flag) {
      return
    }

    submitFlag(
      { flag },
      {
        onSuccess: (response) => {
          setLastResult(response.data)
          setFlagInputs((prev) => ({ ...prev, [taskId]: '' }))
          setSelectedTask(null)
          void refetchTasks()
          void refetchTeam()
          void refetchSubmissions()
          setTimeout(() => setLastResult(null), 5000) // Clear alert after 5 seconds
        },
        onError: (err: any) => {
          setLastResult({
            success: false,
            message: err.response?.data?.message || 'Failed to submit flag',
          })
          setTimeout(() => setLastResult(null), 5000)
        },
      }
    )
  }

  const solvedCount = tasks?.filter((t) => t.solved).length ?? 0

  return (
    <Layout>
      <div className="space-y-6">
        {/* Team summary */}
        {teamLoading ? (
          <Skeleton className="h-24 w-full" />
        ) : team ? (
          <Card>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="eyebrow">Team</p>
                <p className="text-xl font-semibold tracking-tight text-neutral-900 dark:text-white">
                  {team.name}
                </p>
              </div>
            </div>
            <dl className="grid grid-cols-3 divide-x divide-neutral-200 dark:divide-neutral-800">
              <Stat label="Score" value={team.score} accent="indigo" />
              <Stat label="Rank" value={`#${team.rank}`} accent="default" className="pl-4" />
              <Stat
                label="Solved"
                value={tasks ? `${solvedCount}/${tasks.length}` : String(solvedCount)}
                accent="emerald"
                className="pl-4"
              />
            </dl>
          </Card>
        ) : null}

        {/* Result / error banners */}
        {lastResult && (
          <Alert variant={lastResult.success ? 'success' : 'destructive'}>
            <AlertIcon variant={lastResult.success ? 'success' : 'destructive'} />
            <AlertDescription>
              <p className="font-semibold">{lastResult.message}</p>
              {lastResult.points && <p className="text-sm">+{lastResult.points} points</p>}
            </AlertDescription>
          </Alert>
        )}
        {error && (
          <Alert variant="destructive">
            <AlertIcon variant="destructive" />
            <AlertDescription>
              {error instanceof Error ? error.message : 'An error occurred'}
            </AlertDescription>
          </Alert>
        )}

        {/* Tasks */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Flag className="h-4 w-4 text-neutral-400" />
              Tasks
            </CardTitle>
            <CardDescription>Open a task, read the brief, and submit its flag</CardDescription>
          </CardHeader>
          <CardContent>
            {tasksLoading ? (
              <div className="grid gap-4 md:grid-cols-2">
                <Skeleton className="h-44 w-full" />
                <Skeleton className="h-44 w-full" />
              </div>
            ) : tasks && tasks.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2">
                {tasks.map((task, index) => (
                  <button
                    key={task.id}
                    type="button"
                    onClick={() => setSelectedTask(task)}
                    className="group flex min-h-[13rem] flex-col justify-between rounded-xl border border-neutral-200 bg-white p-4 text-left transition hover:border-neutral-300 hover:shadow-sm dark:border-neutral-800 dark:bg-neutral-950 dark:hover:border-neutral-700"
                  >
                    <div className="space-y-3">
                      {task.image_url && (
                        <div className="aspect-video overflow-hidden rounded-lg bg-neutral-100 dark:bg-neutral-800">
                          <img src={resolveAssetUrl(task.image_url) || ''} alt="" className="h-full w-full object-cover" />
                        </div>
                      )}
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <p className="eyebrow">Task {index + 1}</p>
                          <p className="truncate text-base font-semibold text-neutral-900 dark:text-white">
                            {task.title}
                          </p>
                        </div>
                        {task.solved ? (
                          <span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
                            <CheckCircle className="h-3 w-3" />
                            Solved
                          </span>
                        ) : (
                          <span className="shrink-0 rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-medium text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300">
                            {task.points} pts
                          </span>
                        )}
                      </div>
                      <p className="line-clamp-3 whitespace-pre-wrap text-sm leading-6 text-neutral-600 dark:text-neutral-400">
                        {task.description || 'No description yet'}
                      </p>
                    </div>

                    <span className="mt-4 text-sm font-medium text-neutral-900 group-hover:underline dark:text-white">
                      Open task →
                    </span>
                  </button>
                ))}
              </div>
            ) : (
              <p className="py-8 text-center text-sm text-neutral-500 dark:text-neutral-400">
                No tasks yet
              </p>
            )}
          </CardContent>
        </Card>

        {/* Task modal */}
        {selectedTask && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-neutral-950/60 p-4 backdrop-blur-sm"
            onClick={() => setSelectedTask(null)}
          >
            <div
              className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl border border-neutral-200 bg-white shadow-2xl dark:border-neutral-800 dark:bg-neutral-900"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-start justify-between gap-4 border-b border-neutral-200 p-5 dark:border-neutral-800">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="rounded-full bg-neutral-100 px-2.5 py-1 text-xs font-medium text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300">
                      {selectedTask.points} pts
                    </span>
                    {selectedTask.solved && (
                      <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-600 dark:text-emerald-400">
                        <CheckCircle className="h-3.5 w-3.5" />
                        Solved
                      </span>
                    )}
                  </div>
                  <h2 className="mt-2 text-xl font-semibold tracking-tight text-neutral-900 dark:text-white">
                    {selectedTask.title}
                  </h2>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedTask(null)}
                  className="rounded-lg p-2 text-neutral-500 transition-colors hover:bg-neutral-100 dark:text-neutral-400 dark:hover:bg-neutral-800"
                  aria-label="Close task"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              {selectedTask.image_url && (
                <div className="bg-neutral-100 dark:bg-neutral-950">
                  <img
                    src={resolveAssetUrl(selectedTask.image_url) || ''}
                    alt=""
                    className="mx-auto max-h-[60vh] w-full object-contain"
                  />
                </div>
              )}

              <div className="space-y-5 p-5">
                <p className="whitespace-pre-wrap text-sm leading-6 text-neutral-700 dark:text-neutral-300">
                  {selectedTask.text || selectedTask.description || 'No task text yet'}
                </p>

                <form
                  onSubmit={(event) => handleSubmitFlag(event, selectedTask.id)}
                  className="flex flex-col gap-2 sm:flex-row"
                >
                  <Input
                    type="text"
                    placeholder="CTF{flag}"
                    className="font-mono"
                    value={flagInputs[selectedTask.id] || ''}
                    onChange={(event) =>
                      setFlagInputs((prev) => ({
                        ...prev,
                        [selectedTask.id]: event.target.value,
                      }))
                    }
                    disabled={isSubmitting || selectedTask.solved}
                    required
                  />
                  <Button
                    type="submit"
                    className="sm:w-32"
                    disabled={isSubmitting || selectedTask.solved || !flagInputs[selectedTask.id]?.trim()}
                  >
                    {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Submit flag'}
                  </Button>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Recent submissions */}
        <Card>
          <CardHeader>
            <CardTitle>Recent submissions</CardTitle>
            <CardDescription>Your last flag attempts</CardDescription>
          </CardHeader>
          <CardContent>
            {submissionsLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
            ) : submissions && submissions.length > 0 ? (
              <div className="space-y-2">
                {submissions.map((submission) => (
                  <div
                    key={submission.id}
                    className="flex items-center justify-between gap-3 rounded-xl border border-neutral-200 px-4 py-3 dark:border-neutral-800"
                  >
                    <div className="min-w-0">
                      <p className="truncate font-mono text-sm text-neutral-700 dark:text-neutral-300">
                        {submission.flag}
                      </p>
                      <p className="text-xs text-neutral-500 dark:text-neutral-400">
                        {new Date(submission.created_at).toLocaleString()}
                      </p>
                    </div>
                    {submission.correct ? (
                      <span className="shrink-0 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300">
                        Correct
                      </span>
                    ) : (
                      <span className="shrink-0 rounded-full bg-rose-50 px-2.5 py-1 text-xs font-medium text-rose-700 dark:bg-rose-950/60 dark:text-rose-300">
                        Wrong
                      </span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="py-8 text-center text-sm text-neutral-500 dark:text-neutral-400">
                No submissions yet
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </Layout>
  )
}

function Stat({
  label,
  value,
  accent = 'default',
  className,
}: {
  label: string
  value: string | number
  accent?: 'default' | 'indigo' | 'emerald'
  className?: string
}) {
  const accentClass =
    accent === 'indigo'
      ? 'text-indigo-600 dark:text-indigo-400'
      : accent === 'emerald'
        ? 'text-emerald-600 dark:text-emerald-400'
        : 'text-neutral-900 dark:text-white'

  return (
    <div className={className}>
      <p className="eyebrow">{label}</p>
      <p className={`text-2xl font-semibold tabular-nums ${accentClass}`}>{value}</p>
    </div>
  )
}
