import { useMutation, useQuery } from '@tanstack/react-query'
import {
  LoginRequest,
  ScoreboardEntry,
  Submission,
  SubmitFlagRequest,
  TeamTask,
  TeamMe,
  QueryErrorType,
} from '@/shared/types'
import { authApi, teamApi, flagsApi, scoreboardApi } from '@/features/auth/api'

// Auth hooks
export const useLogin = () => {
  return useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
  })
}

// Team hooks
export const useTeam = () => {
  return useQuery<TeamMe, QueryErrorType>({
    queryKey: ['team', 'me'],
    queryFn: async () => {
      const response = await teamApi.getMe()
      return response.data
    },
  })
}

// Flags hooks
export const useSubmitFlag = () => {
  return useMutation({
    mutationFn: (data: SubmitFlagRequest) => flagsApi.submit(data),
  })
}

export const useTasks = () => {
  return useQuery<TeamTask[], QueryErrorType>({
    queryKey: ['flags', 'tasks'],
    queryFn: async () => {
      const response = await flagsApi.getTasks()
      return response.data
    },
  })
}

export const useSubmissions = () => {
  return useQuery<Submission[], QueryErrorType>({
    queryKey: ['submissions'],
    queryFn: async () => {
      const response = await flagsApi.getSubmissions()
      return response.data
    },
  })
}

// Scoreboard hooks
export const useScoreboard = () => {
  return useQuery<ScoreboardEntry[], QueryErrorType>({
    queryKey: ['scoreboard'],
    queryFn: async () => {
      const response = await scoreboardApi.get()
      return response.data
    },
    refetchInterval: 15 * 1000, // 15 секунд
  })
}
