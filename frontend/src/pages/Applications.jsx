import { useState } from 'react'
import { api } from '../api'
import { useApi } from '../hooks'

export default function Applications() {
  const apps = useApi('/applications')
  const inbox = useApi('/messages')
  const [digest, setDigest] = useState(null)

  return (
    <>
      <h2>Applications</h2>
      {apps.data?.applications.map((a) => (
        <div className="card" key={a.id}>
          <strong>{a.jobs?.title}</strong> · {a.status}{' '}
          <em>({a.mode === 'queued_in_app' ? 'queued in Gap2Gain, not sent externally' : 'submitted externally'})</em>
        </div>
      ))}
      <h2>Inbox <small>(sample messages)</small></h2>
      {inbox.data?.messages.map((m) => (
        <div className="card" key={m.id}><strong>{m.subject}</strong><br /><small>{m.sender}</small><p>{m.body}</p></div>
      ))}
      <button onClick={async () => setDigest(await api('/digests/preview', { method: 'POST' }))}>Preview digest</button>
      {digest && (
        <div className="card">
          <p>Would be delivered: {new Date(digest.scheduled_for).toLocaleString()} ({digest.scheduling_reason})</p>
          <ul>{digest.items.map((i) => <li key={i.message_id}><strong>{i.subject}</strong>: {i.snippet}</li>)}</ul>
        </div>
      )}
    </>
  )
}
