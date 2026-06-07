import { useState } from 'react'
import { Header } from '@/shared/components'
import { useTeam, useSubmitFlag, useSubmissions, useTasks } from '@/shared/hooks'
import { Button, Input, Card, CardHeader, CardTitle, CardDescription, CardContent, Alert, AlertDescription, AlertIcon, Skeleton } from '@/shared/ui'
import { CheckCircle, Flag, Loader2, Trophy } from 'lucide-react'

export function DashboardPage() {
  const { data: team, isLoading: teamLoading, refetch: refetchTeam } = useTeam()
  const { data: tasks, isLoading: tasksLoading, refetch: refetchTasks } = useTasks()
  const { data: submissions, isLoading: submissionsLoading, refetch: refetchSubmissions } = useSubmissions()
  const { mutate: submitFlag, isPending: isSubmitting, error } = useSubmitFlag()

  const [flagInputs, setFlagInputs] = useState<Record<string, string>>({})
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

  return (
    <>
      <Header />
      <div className="page-container py-8">
        <div className="container space-y-8">
          {/* Team Card */}
          <div>
            {teamLoading ? (
              <Skeleton className="h-32 w-full" />
            ) : team ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Trophy className="h-6 w-6 text-yellow-500" />
                    Team Info
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Team Name</p>
                      <p className="text-xl font-bold">{team.name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Score</p>
                      <p className="text-xl font-bold text-blue-600 dark:text-blue-400">{team.score}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Rank</p>
                      <p className="text-xl font-bold text-green-600 dark:text-green-400">#{team.rank}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : null}
          </div>

          {/* Task Cards */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Flag className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                Tasks
              </CardTitle>
              <CardDescription>Read the description and submit the flag for each task</CardDescription>
            </CardHeader>
            <CardContent>
              {tasksLoading ? (
                <div className="grid gap-4 md:grid-cols-2">
                  <Skeleton className="h-48 w-full" />
                  <Skeleton className="h-48 w-full" />
                </div>
              ) : tasks && tasks.length > 0 ? (
                <div className="grid gap-4 md:grid-cols-2">
                  {tasks.map((task, index) => (
                    <div
                      key={task.id}
                      className="flex min-h-56 flex-col justify-between rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900"
                    >
                      <div className="space-y-3">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">
                              Task #{index + 1}
                            </p>
                            <p className="text-lg font-bold text-gray-900 dark:text-white">
                              {task.points} points
                            </p>
                          </div>
                          {task.solved && (
                            <span className="inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-800 dark:bg-green-900 dark:text-green-200">
                              <CheckCircle className="mr-1 h-3 w-3" />
                              Solved
                            </span>
                          )}
                        </div>
                        <p className="whitespace-pre-wrap text-sm leading-6 text-gray-700 dark:text-gray-300">
                          {task.description || 'No description yet'}
                        </p>
                      </div>

                      <form
                        onSubmit={(event) => handleSubmitFlag(event, task.id)}
                        className="mt-4 flex flex-col gap-2 sm:flex-row"
                      >
                        <Input
                          type="text"
                          placeholder="CTF{flag}"
                          value={flagInputs[task.id] || ''}
                          onChange={(event) =>
                            setFlagInputs((prev) => ({
                              ...prev,
                              [task.id]: event.target.value,
                            }))
                          }
                          disabled={isSubmitting || task.solved}
                          required
                        />
                        <Button
                          type="submit"
                          disabled={isSubmitting || task.solved || !flagInputs[task.id]?.trim()}
                        >
                          {isSubmitting ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            'Check'
                          )}
                        </Button>
                      </form>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 dark:text-gray-400">
                  No tasks yet
                </p>
              )}

              {/* Alert Messages */}
              {lastResult && (
                <div className="mt-4">
                  <Alert variant={lastResult.success ? 'success' : 'destructive'}>
                    <AlertIcon variant={lastResult.success ? 'success' : 'destructive'} />
                    <AlertDescription>
                      <p className="font-semibold">{lastResult.message}</p>
                      {lastResult.points && (
                        <p className="text-sm">+{lastResult.points} points</p>
                      )}
                    </AlertDescription>
                  </Alert>
                </div>
              )}
              {error && (
                <div className="mt-4">
                  <Alert variant="destructive">
                    <AlertIcon variant="destructive" />
                    <AlertDescription>
                      {error instanceof Error ? error.message : 'An error occurred'}
                    </AlertDescription>
                  </Alert>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Submissions */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Submissions</CardTitle>
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
                      className="flex items-center justify-between rounded-lg border border-gray-200 p-3 dark:border-gray-700"
                    >
                      <div>
                        <p className="font-mono text-sm text-gray-700 dark:text-gray-300">
                          {submission.flag}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {new Date(submission.created_at).toLocaleString()}
                        </p>
                      </div>
                      <div>
                        {submission.correct ? (
                          <span className="inline-block rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-800 dark:bg-green-900 dark:text-green-200">
                            Correct
                          </span>
                        ) : (
                          <span className="inline-block rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-800 dark:bg-red-900 dark:text-red-200">
                            Wrong
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 dark:text-gray-400">
                  No submissions yet
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  )
}
