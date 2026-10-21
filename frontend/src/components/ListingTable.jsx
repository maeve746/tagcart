import { ArrowUpRight, MoreHorizontal, PackageOpen } from 'lucide-react'
import { Link } from 'react-router-dom'
import { formatDate } from '../utils/formatters'
import StatusBadge from './StatusBadge'

export function TableSkeleton() {
  return <div className="divide-y divide-[#edf0ec]">{Array.from({ length: 5 }).map((_, index) => <div key={index} className="flex animate-pulse items-center gap-4 px-5 py-4"><div className="size-9 rounded-lg bg-[#eef0ed]" /><div className="h-3 flex-1 rounded bg-[#eef0ed]" /><div className="hidden h-3 w-24 rounded bg-[#eef0ed] sm:block" /><div className="h-6 w-20 rounded-full bg-[#eef0ed]" /></div>)}</div>
}

export function EmptyState({ filtered = false }) {
  return <div className="flex flex-col items-center px-6 py-14 text-center"><span className="grid size-12 place-items-center rounded-2xl bg-[#eef3ee] text-[#557360]"><PackageOpen size={22} /></span><h3 className="mt-4 text-sm font-semibold text-[#263129]">{filtered ? 'No matching listings' : 'No listings yet'}</h3><p className="mt-1 max-w-xs text-xs leading-5 text-[#858d87]">{filtered ? 'Try a different search term or status filter.' : 'Create your first listing to start preparing product content.'}</p></div>
}

export default function ListingTable({ listings, loading, filtered = false }) {
  if (loading) return <TableSkeleton />
  if (!listings.length) return <EmptyState filtered={filtered} />

  return (
    <div className="overflow-x-auto scrollbar-subtle">
      <table className="w-full min-w-[720px] text-left">
        <thead><tr className="border-b border-[#e8ebe7] text-[10px] font-semibold uppercase tracking-[0.11em] text-[#969d98]"><th className="px-5 py-3.5">Product</th><th className="px-4 py-3.5">Category</th><th className="px-4 py-3.5">Status</th><th className="px-4 py-3.5">Created</th><th className="px-5 py-3.5 text-right">Action</th></tr></thead>
        <tbody className="divide-y divide-[#edf0ec]">{listings.map((listing, index) => <tr key={listing.id} className="group transition duration-200 hover:bg-[#f7fbf8]"><td className="px-5 py-3.5"><Link to={`/listings/${listing.id}`} className="flex items-center gap-3"><span className={`grid size-10 shrink-0 place-items-center rounded-xl text-[10px] font-bold shadow-inner ring-1 ring-black/[.03] transition-transform group-hover:scale-105 ${['bg-[#e3f0e6] text-[#477158]','bg-[#f5eadf] text-[#8a6846]','bg-[#e6eef3] text-[#4f7182]'][index % 3]}`}>{listing.name.split(' ').slice(0,2).map(w=>w[0]).join('')}</span><span><span className="block text-sm font-semibold text-[#29342d] transition-colors group-hover:text-[#245f3d]">{listing.name}</span><span className="mt-0.5 block text-[11px] text-[#969d98]">{listing.id}</span></span></Link></td><td className="px-4 py-3.5 text-xs text-[#68716b]">{listing.category}</td><td className="px-4 py-3.5"><StatusBadge status={listing.status} /></td><td className="px-4 py-3.5 text-xs text-[#68716b]">{formatDate(listing.createdAt, true)}</td><td className="px-5 py-3.5 text-right"><Link to={`/listings/${listing.id}`} aria-label={`Open ${listing.name}`} className="inline-flex rounded-lg p-2 text-[#8b938d] hover:bg-[#e6f1e8] hover:text-[#265e3d]"><ArrowUpRight size={17} /></Link><button aria-label="More actions" className="inline-flex rounded-lg p-2 text-[#a0a6a1] hover:bg-[#eef0ed] hover:text-[#526158]"><MoreHorizontal size={17} /></button></td></tr>)}</tbody>
      </table>
    </div>
  )
}
