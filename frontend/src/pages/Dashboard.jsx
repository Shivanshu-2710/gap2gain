import { useApi } from '../hooks'

export default function Dashboard() {
  const avail = useApi('/availability')
  const matches = useApi('/matches')
  const apps = useApi('/applications')
  const usage = useApi('/usage')
  const hours = avail.data ? (avail.data.total_free_minutes / 60).toFixed(1) : '…'

  return (
    <>
      <h2>Dashboard</h2>
      <div className="grid">
        <div className="card"><h3>{hours} h</h3><p>Free per week</p></div>
        <div className="card"><h3>{matches.data?.matches.length ?? '…'}</h3><p>Matched jobs</p></div>
        <div className="card"><h3>{apps.data?.applications.length ?? '…'}</h3><p>Applications</p></div>
        <div className="card">
          <h3>{usage.data ? (usage.data.remaining ?? '∞') : '…'}</h3><p>Auto-applies left today</p>
        </div>
      </div>
      {/* "Earnings reported" needs an earnings table; add it after the MVP. */}
    </>
  )
}
