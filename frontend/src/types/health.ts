export type DependencyState = 'ok' | 'unavailable'

export interface HealthResponse {
  status: 'ok' | 'degraded'
  timestamp: string
  dependencies: Record<string, { status: DependencyState; detail: string | null }>
}
