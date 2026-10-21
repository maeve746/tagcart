import { useEffect, useState } from 'react'
import { listingsService } from '../services/listingsService'

export function useListings() {
  const [listings, setListings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    listingsService.getAll()
      .then((data) => active && setListings(data))
      .catch(() => active && setError('We couldn’t load your listings. Please try again.'))
      .finally(() => active && setLoading(false))
    return () => { active = false }
  }, [])

  return { listings, loading, error }
}
