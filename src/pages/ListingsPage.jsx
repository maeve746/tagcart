import { Plus } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import ListingTable from '../components/ListingTable'
import SearchFilters from '../components/SearchFilters'
import { useListings } from '../hooks/useListings'

export default function ListingsPage() {
  const [params] = useSearchParams()
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState(params.get('status') || 'All')
  const { listings, loading, error } = useListings()
  const filtered = useMemo(() => listings.filter((item) => { const term = query.toLowerCase(); return (status === 'All' || item.status === status) && (!term || `${item.name} ${item.id} ${item.category}`.toLowerCase().includes(term)) }), [listings, query, status])

  return <div><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><h2 className="text-2xl font-semibold tracking-[-0.03em] text-[#19251d]">Product listings</h2><p className="mt-1 text-sm text-[#7b847e]">Manage every product from draft to export.</p></div><Link to="/listings/new" className="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-[#173f2a] px-4 text-sm font-semibold text-white"><Plus size={17} /> New listing</Link></div><div className="mt-6 rounded-2xl border border-[#e3e6e2] bg-white shadow-[0_3px_16px_rgba(28,44,33,.035)]"><div className="border-b border-[#e8ebe7] p-4 sm:p-5"><SearchFilters query={query} setQuery={setQuery} status={status} setStatus={setStatus} /><p className="mt-3 text-[11px] text-[#8a928d]">{loading ? 'Loading listings…' : `${filtered.length} of ${listings.length} listings`}</p></div>{error ? <p className="p-6 text-sm text-red-600">{error}</p> : <ListingTable listings={filtered} loading={loading} filtered={query || status !== 'All'} />}</div></div>
}
