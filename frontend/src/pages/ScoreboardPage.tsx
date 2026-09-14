import { Layout } from '@/shared/components'
import { useScoreboard } from '@/shared/hooks'
import { Card, Table, TableHeader, TableBody, TableHead, TableRow, TableCell, Skeleton } from '@/shared/ui'

const medals: Record<number, string> = { 1: '🥇', 2: '🥈', 3: '🥉' }

export function ScoreboardPage() {
  const { data: scoreboard, isLoading } = useScoreboard()

  return (
    <Layout>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-neutral-900 dark:text-white">
          Scoreboard
        </h1>
        <p className="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
          Current standings · auto-refreshes every 15 seconds
        </p>
      </div>

      <Card className="p-0">
        {isLoading ? (
          <div className="space-y-2 p-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-11 w-full" />
            ))}
          </div>
        ) : scoreboard && scoreboard.length > 0 ? (
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent dark:hover:bg-transparent">
                <TableHead className="w-20 pl-6">Rank</TableHead>
                <TableHead>Team</TableHead>
                <TableHead className="pr-6 text-right">Score</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {scoreboard.map((entry) => (
                <TableRow key={entry.team_name}>
                  <TableCell className="pl-6 font-semibold tabular-nums">
                    {medals[entry.rank] ?? (
                      <span className="text-neutral-400 dark:text-neutral-500">
                        {entry.rank}
                      </span>
                    )}
                  </TableCell>
                  <TableCell className="font-medium">{entry.team_name}</TableCell>
                  <TableCell className="pr-6 text-right font-semibold tabular-nums text-indigo-600 dark:text-indigo-400">
                    {entry.score}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <p className="p-10 text-center text-sm text-neutral-500 dark:text-neutral-400">
            No scoreboard data available
          </p>
        )}
      </Card>
    </Layout>
  )
}
