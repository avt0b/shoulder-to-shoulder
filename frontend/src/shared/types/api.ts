// Auth types
export interface LoginRequest {
  team_name: string
  password: string
}

export interface LoginResponse {
  access_token: string
  role: 'team' | 'admin'
}

export interface TeamMe {
  id: string
  name: string
  score: number
  rank: number
}

// Flag types
export interface SubmitFlagRequest {
  flag: string
}

export interface SubmitFlagResponse {
  success: boolean
  message: string
  points?: number
}

export interface TeamTask {
  id: string
  title: string
  description: string | null
  text: string | null
  image_url: string | null
  is_visible: boolean
  points: number
  solved: boolean
  solved_at: string | null
  created_at: string
}

// Submission types
export interface Submission {
  id: string
  flag: string
  correct: boolean
  created_at: string
}

// Scoreboard types
export interface ScoreboardEntry {
  rank: number
  team_name: string
  score: number
}

// Admin types
export interface AdminFlagCreateRequest {
  title: string
  flag: string
  description?: string | null
  text?: string | null
  image_url?: string | null
  points: number
  is_visible?: boolean
}

export interface AdminFlagUpdateRequest {
  title?: string
  flag?: string
  description?: string | null
  text?: string | null
  image_url?: string | null
  points?: number
  is_visible?: boolean
}

export interface AdminFlagVisibilityRequest {
  is_visible: boolean
}

export interface AdminTeamCreateRequest {
  team_name: string
  password: string
}

export interface AdminFlag {
  id: string
  title: string
  flag: string
  description: string | null
  text: string | null
  image_url: string | null
  points: number
  is_visible: boolean
  created_at: string
  solves: number
}

export interface AdminTeam {
  id: string
  name: string
  score: number
  rank: number
  is_banned: boolean
  ban_reason: string | null
  banned_at: string | null
  created_at: string
  submissions_count: number
  solves_count: number
}

export interface AdminAnalytics {
  teams_count: number
  banned_teams_count: number
  flags_count: number
  submissions_count: number
  correct_submissions_count: number
  wrong_submissions_count: number
  total_score: number
}

export interface AdminSubmission {
  id: string
  team_id: string
  team_name: string
  flag_id: string | null
  flag: string
  correct: boolean
  created_at: string
}

// Error types
export interface ApiError {
  message: string
  status: number
}

// Auth store types
export interface AuthStore {
  token: string | null
  setToken: (token: string | null) => void
  login: (token: string) => void
  logout: () => void
  isAuthed: () => boolean
}
