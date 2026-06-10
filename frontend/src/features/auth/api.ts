import { request } from '@/shared/services/api'
import {
  LoginRequest,
  LoginResponse,
  TeamMe,
  SubmitFlagRequest,
  SubmitFlagResponse,
  TeamTask,
  Submission,
  ScoreboardEntry,
  AdminAnalytics,
  AdminFlag,
  AdminFlagCreateRequest,
  AdminFlagUpdateRequest,
  AdminFlagVisibilityRequest,
  AdminTeamCreateRequest,
  AdminSubmission,
  AdminTeam,
} from '@/shared/types'

// Auth API
export const authApi = {
  login: (data: LoginRequest) =>
    request.post<LoginResponse>('/api/auth/login', data),
}

// Team API
export const teamApi = {
  getMe: () =>
    request.get<TeamMe>('/api/team/me'),
}

// Flags API
export const flagsApi = {
  getTasks: () =>
    request.get<TeamTask[]>('/api/flags/tasks'),

  submit: (data: SubmitFlagRequest) =>
    request.post<SubmitFlagResponse>('/api/flags/submit', data),

  getSubmissions: () =>
    request.get<Submission[]>('/api/submissions'),
}

// Scoreboard API
export const scoreboardApi = {
  get: () =>
    request.get<ScoreboardEntry[]>('/api/scoreboard'),
}

const adminConfig = (token: string) => ({
  headers: {
    Authorization: `Bearer ${token}`,
  },
})

export const adminApi = {
  getAnalytics: (token: string) =>
    request.get<AdminAnalytics>('/api/admin/analytics', adminConfig(token)),

  getFlags: (token: string) =>
    request.get<AdminFlag[]>('/api/admin/flags', adminConfig(token)),

  createFlag: (token: string, data: AdminFlagCreateRequest) =>
    request.post<AdminFlag>('/api/admin/flags', data, adminConfig(token)),

  updateFlag: (token: string, flagId: string, data: AdminFlagUpdateRequest) =>
    request.patch<AdminFlag>(`/api/admin/flags/${flagId}`, data, adminConfig(token)),

  setFlagsVisibility: (token: string, data: AdminFlagVisibilityRequest) =>
    request.post<AdminFlag[]>('/api/admin/flags/visibility', data, adminConfig(token)),

  uploadTaskImage: (token: string, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post<{ image_url: string }>('/api/admin/uploads', formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  deleteFlag: (token: string, flagId: string) =>
    request.delete<void>(`/api/admin/flags/${flagId}`, adminConfig(token)),

  getTeams: (token: string) =>
    request.get<AdminTeam[]>('/api/admin/teams', adminConfig(token)),

  createTeam: (token: string, data: AdminTeamCreateRequest) =>
    request.post<AdminTeam>('/api/admin/teams', data, adminConfig(token)),

  banTeam: (token: string, teamId: string, reason: string | null) =>
    request.post<AdminTeam>(`/api/admin/teams/${teamId}/ban`, { reason }, adminConfig(token)),

  unbanTeam: (token: string, teamId: string) =>
    request.post<AdminTeam>(`/api/admin/teams/${teamId}/unban`, undefined, adminConfig(token)),

  getSubmissions: (token: string) =>
    request.get<AdminSubmission[]>('/api/admin/submissions', adminConfig(token)),
}
