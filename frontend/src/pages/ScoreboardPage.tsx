import { Header } from '@/shared/components'
import { useScoreboard } from '@/shared/hooks'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Table, TableHeader, TableBody, TableHead, TableRow, TableCell, Skeleton } from '@/shared/ui'
import { Trophy } from 'lucide-react'

export function ScoreboardPage() {
  const { data: scoreboard, isLoading } = useScoreboard()

  return (
    <>
      <Header />
      <div className="page-container py-8">
        <div className="container">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="h-6 w-6 text-yellow-500" />
                Scoreboard
              </CardTitle>
              <CardDescription>
                Current standings (auto-refreshes every 15 seconds)
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-2">
                  <Skeleton className="h-12 w-full" />
                  <Skeleton className="h-12 w-full" />
                  <Skeleton className="h-12 w-full" />
                  <Skeleton className="h-12 w-full" />
                  <Skeleton className="h-12 w-full" />
                </div>
              ) : scoreboard && scoreboard.length > 0 ? (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-20">Rank</TableHead>
                        <TableHead>Team</TableHead>
                        <TableHead className="text-right">Score</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {scoreboard.map((entry) => (
                        <TableRow key={entry.team_name}>
                          <TableCell className="font-bold">
                            <div className="flex items-center gap-2">
                              {entry.rank === 1 && <span>🥇</span>}
                              {entry.rank === 2 && <span>🥈</span>}
                              {entry.rank === 3 && <span>🥉</span>}
                              {entry.rank > 3 && <span>#{entry.rank}</span>}
                            </div>
                          </TableCell>
                          <TableCell className="font-medium">
                            {entry.team_name}
                          </TableCell>
                          <TableCell className="text-right font-bold text-blue-600 dark:text-blue-400">
                            {entry.score}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <p className="text-center text-gray-500 dark:text-gray-400">
                  No scoreboard data available
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  )
}
