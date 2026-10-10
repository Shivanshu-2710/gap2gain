import { useCallback, useEffect, useState } from 'react'
import { api } from './api'

// Small fetch helper: { data, error, loading, reload }
export function useApi(path) {
  const [state, setState] = useState({ data: null, error: '', loading: true })
  const load = useCallback(() => {
    setState((s) => ({ ...s, loading: true }))
    api(path).then((data) => setState({ data, error: '', loading: false }))
      .catch((e) => setState({ data: null, error: e.message, loading: false }))
  }, [path])
  useEffect(load, [load])
  return { ...state, reload: load }
}
