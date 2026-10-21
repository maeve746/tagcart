import { Check, ChevronRight, Clock3, FilePenLine, LoaderCircle, Plus, Send, Sparkles } from 'lucide-react'
import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import ListingTable from '../components/ListingTable'
import StatusCard from '../components/StatusCard'
import { WORKFLOW_STATUSES } from '../data/mockListings'
import { useListings } from '../hooks/useListings'

const icons = [FilePenLine, LoaderCircle, Clock3, Check, Send]

export default function DashboardPage() {
  const { listings, loading, error } = useListings()
  const counts = useMemo(() => Object.fromEntries(WORKFLOW_STATUSES.map((status) => [status, listings.filter((item) => item.status === status).length])), [listings])

  return <div><section className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end"><div><p className="text-xs font-semibold uppercase tracking-[0.13em] text-[#75907d]">Wednesday, October 21</p><h2 className="mt-2 text-[26px] font-semibold tracking-[-0.035em] text-[#19251d] sm:text-[30px]">Good morning, Monu</h2><p className="mt-1.5 text-sm text-[#7b847e]">Here’s what’s happening with your product listings.</p></div><Link to="/listings/new" className="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-[#173f2a] px-4 text-sm font-semibold text-white shadow-[0_8px_18px_rgba(23,63,42,.18)] transition hover:bg-[#215238]"><Plus size={17} /> New listing</Link></section>
  <section className="mt-7 grid grid-cols-2 gap-3 lg:grid-cols-5">{WORKFLOW_STATUSES.map((label, index) => <StatusCard key={label} label={label} count={loading ? 0 : counts[label]} icon={icons[index]} />)}</section>
  <section className="mt-6 grid gap-5 xl:grid-cols-[minmax(0,1fr)_280px]"><div className="overflow-hidden rounded-2xl border border-[#e3e6e2] bg-white shadow-[0_3px_16px_rgba(28,44,33,.035)]"><div className="flex items-center justify-between border-b border-[#e8ebe7] px-5 py-4"><div><h3 className="text-sm font-semibold text-[#263129]">Recent listings</h3><p className="mt-0.5 text-[11px] text-[#919892]">Your latest product activity</p></div><Link to="/listings" className="flex items-center gap-1 text-xs font-semibold text-[#3f7552] hover:text-[#173f2a]">View all <ChevronRight size={14} /></Link></div>{error ? <p className="p-6 text-sm text-red-600">{error}</p> : <ListingTable listings={listings.slice(0, 5)} loading={loading} />}</div>
  <aside className="rounded-2xl bg-[#173f2a] p-5 text-white shadow-[0_10px_28px_rgba(23,63,42,.17)]"><div className="flex items-center justify-between"><span className="grid size-9 place-items-center rounded-xl bg-white/10"><Sparkles size={17} /></span><span className="rounded-full bg-white/10 px-2.5 py-1 text-[10px] font-semibold tracking-wide text-[#d4e7d9]">QUICK TIP</span></div><h3 className="mt-7 text-lg font-semibold tracking-[-0.02em]">Keep your catalog moving</h3><p className="mt-2 text-xs leading-5 text-[#bed1c3]">Two listings are ready for your review. Approve them to prepare your next export.</p><Link to="/listings?status=Review" className="mt-5 inline-flex items-center gap-1.5 text-xs font-semibold text-white">Review listings <ChevronRight size={14} /></Link><div className="mt-7 border-t border-white/10 pt-4"><div className="flex justify-between text-[11px]"><span className="text-[#bed1c3]">Catalog completion</span><span className="font-semibold">76%</span></div><div className="mt-2 h-1.5 rounded-full bg-white/10"><div className="h-full w-3/4 rounded-full bg-[#9dccaa]" /></div></div></aside></section></div>
}
