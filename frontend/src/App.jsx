import { useEffect, useState } from 'react'
import { supabase } from './api'
import Dashboard from './pages/Dashboard'
import Schedule from './pages/Schedule'
import FindWork from './pages/FindWork'
import ResumeStudio from './pages/ResumeStudio'
import Applications from './pages/Applications'

const TABS = {
  Dashboard, 'My Schedule': Schedule, 'Find Work': FindWork,
  'Resume Studio': ResumeStudio, 'Applications & Inbox': Applications,
}

export default function App() {
  const [session, setSession] = useState(null)
  const [tab, setTab] = useState('Dashboard')
  const [error, setError] = useState('')

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSession(data.session))
    const { data } = supabase.auth.onAuthStateChange((_e, s) => setSession(s))
    return () => data.subscription.unsubscribe()
  }, [])

  async function tryDemo() {
    setError('')
    const { error } = await supabase.auth.signInWithPassword({
      email: import.meta.env.VITE_DEMO_EMAIL, password: import.meta.env.VITE_DEMO_PASSWORD,
    })
    if (error) setError(error.message)
  }

  if (!session) {
    return (
      <main className="center">
        <h1>Gap2Gain</h1>
        <p>Turn the gaps in your day into income.</p>
        <button onClick={tryDemo}>Try demo</button>
        {error && <p className="err">{error}</p>}
      </main>
    )
  }

  const Page = TABS[tab]
  return (
    <>
      <nav>
        <strong>Gap2Gain</strong>
        {Object.keys(TABS).map((t) => (
          <button key={t} className={t === tab ? 'active' : ''} onClick={() => setTab(t)}>{t}</button>
        ))}
        <button className="link" onClick={() => supabase.auth.signOut()}>Sign out</button>
      </nav>
      <main><Page /></main>
    </>
  )
}
