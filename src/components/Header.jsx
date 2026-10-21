import { Bell, ChevronDown, Menu, Plus, Search, X } from 'lucide-react'
import { useState } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import Brand from './Brand'

const titles = { '/': 'Dashboard', '/listings': 'Listings', '/history': 'History', '/settings': 'Settings', '/listings/new': 'New listing' }
const mobileLinks = [['Dashboard', '/'], ['Listings', '/listings'], ['History', '/history'], ['Settings', '/settings']]

export default function Header() {
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()
  const title = titles[pathname] || (pathname.startsWith('/listings/') ? 'Listing details' : 'Dashboard')

  return (
    <>
      <header className="sticky top-0 z-20 flex h-[72px] items-center justify-between border-b border-[#e8eae7] bg-[#f7f8f6]/90 px-4 backdrop-blur-xl sm:px-7 lg:px-9">
        <div className="flex items-center gap-3">
          <button onClick={() => setOpen(true)} className="rounded-lg p-2 text-[#4a554e] hover:bg-[#ecefec] md:hidden" aria-label="Open menu"><Menu size={21} /></button>
          <h1 className="text-lg font-semibold tracking-[-0.02em] text-[#1d2921]">{title}</h1>
        </div>
        <div className="flex items-center gap-2 sm:gap-3">
          <Link to="/listings" className="hidden items-center gap-2 rounded-xl border border-[#e0e3df] bg-white px-3 py-2 text-sm text-[#7a837d] shadow-sm transition focus-within:border-[#8cac97] sm:flex"><Search size={16} /> Search</Link>
          <button className="relative rounded-xl border border-[#e0e3df] bg-white p-2.5 text-[#4b574f] shadow-sm hover:bg-[#f9faf8]" aria-label="Notifications"><Bell size={18} /><span className="absolute right-2 top-2 size-1.5 rounded-full bg-[#e4864f] ring-2 ring-white" /></button>
          <button className="flex items-center gap-2 rounded-xl border border-[#e0e3df] bg-white p-1.5 pr-2 shadow-sm hover:bg-[#f9faf8]" aria-label="Open account menu">
            <span className="grid size-8 place-items-center rounded-lg bg-[#dceadf] text-xs font-bold text-[#295b3c]">MP</span>
            <span className="hidden text-left lg:block"><span className="block text-xs font-semibold text-[#28332c]">Monu P.</span><span className="block text-[10px] text-[#8a928d]">Seller account</span></span>
            <ChevronDown className="hidden text-[#8a928d] lg:block" size={14} />
          </button>
        </div>
      </header>
      {open && <div className="fixed inset-0 z-50 md:hidden"><button className="absolute inset-0 bg-[#101b14]/35 backdrop-blur-sm" onClick={() => setOpen(false)} aria-label="Close menu" /><aside className="relative h-full w-[280px] bg-[#fbfcfa] p-5 shadow-2xl"><div className="flex items-center justify-between"><Brand /><button onClick={() => setOpen(false)} className="rounded-lg p-2 text-[#657069]"><X size={20} /></button></div><nav className="mt-9 space-y-1">{mobileLinks.map(([label, to]) => <NavLink key={to} to={to} end={to === '/'} onClick={() => setOpen(false)} className={({ isActive }) => `block rounded-xl px-4 py-3 text-sm font-medium ${isActive ? 'bg-[#e8f2ea] text-[#173f2a]' : 'text-[#657069]'}`}>{label}</NavLink>)}</nav><Link onClick={() => setOpen(false)} to="/listings/new" className="mt-6 flex items-center justify-center gap-2 rounded-xl bg-[#173f2a] px-4 py-3 text-sm font-semibold text-white"><Plus size={17} /> New listing</Link></aside></div>}
    </>
  )
}
