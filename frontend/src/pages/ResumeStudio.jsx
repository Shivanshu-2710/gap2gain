import { useState } from 'react'
import { api } from '../api'
import { useApi } from '../hooks'

export default function ResumeStudio() {
  const matches = useApi('/matches')
  const [jobId, setJobId] = useState('')
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [err, setErr] = useState(null)
  const [busy, setBusy] = useState(false)

  async function tailor() {
    setBusy(true); setErr(null)
    try {
      setResult(await api('/resumes/tailor', { method: 'POST', body: { job_id: jobId, resume_text: text || null } }))
    } catch (e) { setErr(e) }
    setBusy(false)
  }

  async function upgrade() {
    await api('/subscription/demo-upgrade', { method: 'POST' })
    setErr(null)
  }

  return (
    <>
      <h2>Resume Studio <small>(Premium)</small></h2>
      <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
        <option value="">Choose a job…</option>
        {matches.data?.matches.map((m) => <option key={m.job_id} value={m.job_id}>{m.title}</option>)}
      </select>
      <textarea rows={8} placeholder="Paste your resume (leave empty to reuse your saved one)" value={text}
        onChange={(e) => setText(e.target.value)} />
      <button disabled={!jobId || busy} onClick={tailor}>{busy ? 'Tailoring…' : 'Tailor resume'}</button>
      {err && (
        <p className="err">{err.message}{' '}
          {err.code === 'premium_required' && <button onClick={upgrade}>Simulate upgrade (demo)</button>}</p>
      )}
      {result && (
        <>
          {result.warnings.map((w) => <p className="notice" key={w}>⚠ {w}</p>)}
          <p>Method: {result.method}. Review every change before using this resume.</p>
          <ul>{result.changes_summary.map((c) => <li key={c}>{c}</li>)}</ul>
          <div className="split">
            <div><h3>Original</h3><pre>{result.original_text}</pre></div>
            <div><h3>Tailored draft</h3><pre>{result.tailored_text}</pre></div>
          </div>
        </>
      )}
    </>
  )
}
