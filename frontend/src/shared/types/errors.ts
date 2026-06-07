import { AxiosError } from 'axios'

export type QueryErrorType = AxiosError<{
  message: string
  detail?: string
}>
