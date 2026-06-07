import { AxiosError } from 'axios'

export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    if (error.response?.data?.message) {
      return error.response.data.message
    }
    if (error.response?.data?.detail) {
      return error.response.data.detail
    }
    if (error.response?.status) {
      return `Error: ${error.response.status}`
    }
  }

  if (error instanceof Error) {
    return error.message
  }

  return 'An unknown error occurred'
}

export function isAxiosError(error: unknown): error is AxiosError {
  return error instanceof AxiosError
}
