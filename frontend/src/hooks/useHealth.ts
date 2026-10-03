import { useEffect, useState } from 'react'
import { fetchHealth } from '../services/api'
import type { HealthResponse } from '../types/health'

export function useHealth() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    fetchHealth(controller.signal).then(setHealth).catch((reason: Error) => setError(reason.message))
    return () => controller.abort()
  }, [])

  return { health, error }
}
