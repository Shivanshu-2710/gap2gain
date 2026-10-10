import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(import.meta.env.VITE_SUPABASE_URL, import.meta.env.VITE_SUPABASE_ANON_KEY)
const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

export async function api(path, { method = 'GET', body } = {}) {
  const { data } = await supabase.auth.getSession()
  const res = await fetch(BASE + path, {
    method,
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${data.session?.access_token}` },
    body: body ? JSON.stringify(body) : undefined,
  })
  const json = await res.json().catch(() => ({}))
  if (!res.ok) {
    const d = json.detail
    const err = new Error(typeof d === 'string' ? d : d?.message ?? res.statusText)
    err.status = res.status
    err.code = d?.code
    throw err
  }
  return json
}

export const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
