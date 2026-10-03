import { ServiceStatus } from '../components/ServiceStatus'

export function WelcomePage() {
  return <main className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-16">
    <p className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-600">AI Marketing Analyst</p>
    <h1 className="mt-5 max-w-3xl text-4xl font-semibold tracking-tight text-slate-950 sm:text-6xl">Find out why revenue changed before your team starts the day.</h1>
    <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">The foundation is connected. In the next phase, this workspace will securely model the marketing, CRM, and sales data that powers evidence-backed analysis.</p>
    <div className="mt-10 max-w-2xl"><ServiceStatus /></div>
  </main>
}
