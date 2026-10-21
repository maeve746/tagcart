import { useEffect, useState } from 'react'
import { listingsService } from '../services/listingsService'

export function useListings() {
  const [listings, setListings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    const load = () => listingsService.getAll()
      .then((data) => { if (active) { setListings(data); setError('') } })
      .catch(() => active && setError('We couldn’t load your listings. Please try again.'))
      .finally(() => active && setLoading(false))
    load()
    const unsubscribe = listingsService.subscribe(load)
    return () => { active = false; unsubscribe() }
  }, [])

  return { listings, loading, error }
}
