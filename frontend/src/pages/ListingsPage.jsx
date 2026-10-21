import { Plus } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import ListingTable from '../components/ListingTable'
import SearchFilters from '../components/SearchFilters'
import { useListings } from '../hooks/useListings'

export default function ListingsPage() {
  const [params, setParams] = useSearchParams()
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState(params.get('status') || 'All')
  const { listings, loading, error } = useListings()
  const filtered = useMemo(() => listings.filter((item) => { const term = query.toLowerCase(); return (status === 'All' || item.status === status) && (!term || `${item.name} ${item.id} ${item.category}`.toLowerCase().includes(term)) }), [listings, query, status])

  const changeStatus = (value) => { setStatus(value); setParams(value === 'All' ? {} : { status: value }) }
  return <div><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><span className="text-[10px] font-bold uppercase tracking-[.14em] text-[#6c8a74]">Catalog manager</span><h2 className="mt-1.5 text-2xl font-semibold tracking-[-0.03em] text-[#19251d]">Product listings</h2><p className="mt-1 text-sm text-[#7b847e]">Manage every product from draft to export.</p></div><Link to="/listings/new" className="btn-primary inline-flex h-11 items-center justify-center gap-2 rounded-xl px-5 text-sm font-semibold"><Plus size={17} /> New listing</Link></div><div className="ui-surface mt-6 overflow-hidden rounded-2xl"><div className="border-b border-[#e8ebe7] p-4 sm:p-5"><SearchFilters query={query} setQuery={setQuery} status={status} setStatus={changeStatus} /><p className="mt-3 text-[11px] font-medium text-[#8a928d]">{loading ? 'Loading listings…' : `${filtered.length} of ${listings.length} listings`}</p></div>{error ? <p className="p-6 text-sm text-red-600">{error}</p> : <ListingTable listings={filtered} loading={loading} filtered={query || status !== 'All'} />}</div></div>
}
