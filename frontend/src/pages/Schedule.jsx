import { useEffect, useState } from 'react'
import { api, DAYS } from '../api'
import { useApi } from '../hooks'

const TYPES = ['class', 'work', 'commute', 'sleep', 'personal', 'unavailable']

export default function Schedule() {
  const routine = useApi('/routine')
  const avail = useApi('/availability')
  const [blocks, setBlocks] = useState([])
  const [form, setForm] = useState({ weekday: 0, start_time: '09:00', end_time: '15:00', block_type: 'class' })
  const [msg, setMsg] = useState('')

  useEffect(() => {
    if (routine.data) setBlocks(routine.data.blocks.map((b) => ({
      weekday: b.weekday, start_time: b.start_time.slice(0, 5), end_time: b.end_time.slice(0, 5), block_type: b.block_type,
    })))
  }, [routine.data])

  async function save() {
    try {
      await api('/routine', { method: 'PUT', body: { blocks } })
      setMsg('Saved'); avail.reload()
    } catch (e) { setMsg(e.message) }
  }

  return (
    <>
      <h2>My Schedule</h2>
      <div className="row">
        <select value={form.weekday} onChange={(e) => setForm({ ...form, weekday: +e.target.value })}>
          {DAYS.map((d, i) => <option key={d} value={i}>{d}</option>)}
        </select>
        <input type="time" value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value })} />
        <input type="time" value={form.end_time} onChange={(e) => setForm({ ...form, end_time: e.target.value })} />
        <select value={form.block_type} onChange={(e) => setForm({ ...form, block_type: e.target.value })}>
          {TYPES.map((t) => <option key={t}>{t}</option>)}
        </select>
        <button onClick={() => setBlocks([...blocks, form])}>Add</button>
        <button onClick={save}>Save routine</button>
        <span>{msg}</span>
      </div>
      <ul>
        {blocks.map((b, i) => (
          <li key={i}>{DAYS[b.weekday]} {b.start_time}–{b.end_time} · {b.block_type}{' '}
            <button className="link" onClick={() => setBlocks(blocks.filter((_, j) => j !== i))}>remove</button></li>
        ))}
      </ul>
      <h3>Your free blocks</h3>
      {avail.data && DAYS.map((d, i) => (
        <p key={d}><strong>{d}:</strong>{' '}
          {avail.data.weekly[i].length
            ? avail.data.weekly[i].map((f) => `${f.start}–${f.end}`).join(', ')
            : 'no usable gap'}</p>
      ))}
    </>
  )
}
