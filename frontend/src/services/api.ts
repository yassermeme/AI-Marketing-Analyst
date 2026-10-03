import type { HealthResponse } from '../types/health'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export async function fetchHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await fetch(`${apiBaseUrl}/health`, { signal })
  const body = await response.json() as HealthResponse | { detail?: HealthResponse }
  if (!response.ok) throw new Error(body.detail?.status === 'degraded' ? 'Some services are unavailable' : 'Could not reach the API')
  return body as HealthResponse
}
