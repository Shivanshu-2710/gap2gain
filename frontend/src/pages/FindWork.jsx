import { useState } from 'react'
import { api } from '../api'
import { useApi } from '../hooks'

export default function FindWork() {
  const matches = useApi('/matches?include_ineligible=true')
  const usage = useApi('/usage')
  const [notice, setNotice] = useState('')

  async function apply(jobId) {
    try {
      const r = await api('/applications', { method: 'POST', body: { job_id: jobId } })
      setNotice(r.status === 'already_applied' ? 'You already applied to this job.' : r.note)
    } catch (e) { setNotice(e.message) }
    usage.reload()
  }

  return (
    <>
      <h2>Find Work</h2>
      {usage.data && <p>Auto-applies left today: <strong>{usage.data.remaining ?? 'unlimited'}</strong></p>}
      {notice && <p className="notice">{notice}</p>}
      {matches.loading && <p>Loading…</p>}
      {matches.error && <p className="err">{matches.error}</p>}
      {matches.data?.matches.map((m) => (
        <div className="card" key={m.job_id}>
          <h3>{m.title} <span className="score">{m.score}</span></h3>
          <p>{m.source} · {m.duration_minutes} min · {m.remote ? 'Remote' : 'On-site'}
            {m.pay_amount != null && ` · ${m.pay_amount}${m.pay_verified ? ' (verified)' : ' (unverified)'}`}</p>
          {m.flagged && <p className="err">⚠ Flagged: {m.flag_reason}</p>}
          <ul>{m.reasons.map((r) => <li key={r}>{r}</li>)}</ul>
          {m.blocking.map((b) => <p className="err" key={b}>{b}</p>)}
          {m.external_url && <a href={m.external_url} target="_blank" rel="noreferrer">View listing</a>}{' '}
          <button disabled={!m.eligible} onClick={() => apply(m.job_id)}>Queue application</button>
        </div>
      ))}
    </>
  )
}
