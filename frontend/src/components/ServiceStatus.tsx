import { useHealth } from '../hooks/useHealth'

export function ServiceStatus() {
  const { health, error } = useHealth()
  const dependencies = health ? Object.entries(health.dependencies) : []
  return <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm" aria-live="polite">
    <div className="flex items-center justify-between"><div><p className="text-sm font-semibold text-slate-900">Foundation status</p><p className="mt-1 text-sm text-slate-500">The application checks the data and job infrastructure before analytics are enabled.</p></div><span className={`rounded-full px-3 py-1 text-xs font-semibold ${health ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'}`}>{health ? 'Connected' : 'Checking'}</span></div>
    {error ? <p className="mt-5 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">{error}. Start the backend, PostgreSQL, and Redis with Docker Compose.</p> : <dl className="mt-5 grid gap-3 sm:grid-cols-2">{dependencies.map(([name, dependency]) => <div key={name} className="flex justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"><dt className="capitalize text-slate-600">{name}</dt><dd className="font-medium text-emerald-700">{dependency.status}</dd></div>)}</dl>}
  </section>
}
