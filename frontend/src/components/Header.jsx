import { Bell, ChevronDown, Menu, Plus, Search, X } from 'lucide-react'
import { useState } from 'react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import Brand from './Brand'
import { authService } from '../services/authService'

const titles = { '/': 'Dashboard', '/listings': 'Listings', '/history': 'History', '/settings': 'Settings', '/seller-guides': 'Seller Guides', '/listings/new': 'New listing' }
const mobileLinks = [['Dashboard', '/'], ['Listings', '/listings'], ['History', '/history'], ['Seller Guides', '/seller-guides'], ['Settings', '/settings']]

export default function Header() {
  const [open, setOpen] = useState(false)
  const [accountOpen, setAccountOpen] = useState(false)
  const { pathname } = useLocation()
  const session = authService.getSession()
  const title = titles[pathname] || (pathname.includes('/analysis') ? 'AI analysis' : pathname.includes('/preview') ? 'Listing preview' : pathname.startsWith('/history/') ? 'Version history' : pathname.startsWith('/listings/') ? 'Listing details' : 'Dashboard')
  const initials = session?.name?.split(' ').map((item) => item[0]).join('').slice(0, 2).toUpperCase() || 'MP'
  const logout = () => { authService.logout(); window.location.assign('/login') }

  return (
    <>
      <header className="sticky top-0 z-20 flex h-[76px] items-center justify-between border-b border-white/70 bg-[#f5f8f5]/80 px-4 shadow-[0_1px_0_rgba(23,63,42,.04)] backdrop-blur-2xl sm:px-7 lg:px-10">
        <div className="flex items-center gap-3">
          <button onClick={() => setOpen(true)} className="rounded-lg p-2 text-[#4a554e] hover:bg-[#ecefec] md:hidden" aria-label="Open menu"><Menu size={21} /></button>
          <div><h1 className="text-lg font-semibold tracking-[-0.025em] text-[#17271d]">{title}</h1><p className="hidden text-[10px] font-medium text-[#8b978f] sm:block">Seller workspace</p></div>
        </div>
        <div className="flex items-center gap-2 sm:gap-3">
          <Link to="/listings" className="btn-secondary hidden items-center gap-2 rounded-xl border border-[#dce4dd] bg-white/85 px-3.5 py-2.5 text-sm text-[#718078] shadow-sm sm:flex"><Search size={16} /> Search</Link>
          <button className="btn-secondary relative rounded-xl border border-[#dce4dd] bg-white/85 p-2.5 text-[#4b574f] shadow-sm" aria-label="Notifications"><Bell size={18} /><span className="absolute right-2 top-2 size-1.5 rounded-full bg-[#ef8d55] ring-2 ring-white" /></button>
          <div className="relative"><button onClick={() => setAccountOpen(!accountOpen)} className="btn-secondary flex items-center gap-2 rounded-xl border border-[#dce4dd] bg-white/85 p-1.5 pr-2 shadow-sm" aria-label="Open account menu">
            <span className="grid size-8 place-items-center rounded-lg bg-gradient-to-br from-[#cfe8d6] to-[#e8f4eb] text-xs font-bold text-[#295b3c] shadow-inner">{initials}</span>
            <span className="hidden text-left lg:block"><span className="block max-w-28 truncate text-xs font-semibold capitalize text-[#28332c]">{session?.name || 'Seller'}</span><span className="block text-[10px] text-[#8a928d]">Demo account</span></span>
            <ChevronDown className="hidden text-[#8a928d] lg:block" size={14} />
          </button>{accountOpen && <div className="page-enter absolute right-0 top-12 w-52 rounded-2xl border border-[#dce4dd] bg-white/95 p-2 shadow-[0_18px_50px_rgba(16,43,29,.16)] backdrop-blur-xl"><p className="truncate border-b border-[#eef1ee] px-2 py-2.5 text-[10px] text-[#858e88]">{session?.email}</p><Link onClick={() => setAccountOpen(false)} to="/settings" className="mt-1 block rounded-lg px-2 py-2 text-xs font-medium text-[#4e5952] hover:bg-[#f0f5f1]">Settings</Link><button onClick={logout} className="w-full rounded-lg px-2 py-2 text-left text-xs font-medium text-[#a45143] hover:bg-[#fff1ee]">Sign out</button></div>}</div>
        </div>
      </header>
      {open && <div className="fixed inset-0 z-50 md:hidden"><button className="absolute inset-0 bg-[#101b14]/45 backdrop-blur-sm" onClick={() => setOpen(false)} aria-label="Close menu" /><aside className="page-enter relative h-full w-[290px] bg-[#fbfdfb] p-5 shadow-2xl"><div className="flex items-center justify-between"><Brand /><button onClick={() => setOpen(false)} className="rounded-lg p-2 text-[#657069] hover:bg-[#edf2ee]"><X size={20} /></button></div><nav className="mt-9 space-y-1">{mobileLinks.map(([label, to]) => <NavLink key={to} to={to} end={to === '/'} onClick={() => setOpen(false)} className={({ isActive }) => `block rounded-xl px-4 py-3 text-sm font-medium ${isActive ? 'bg-[#e4f1e8] text-[#173f2a] shadow-sm' : 'text-[#657069] hover:bg-[#f0f4f1]'}`}>{label}</NavLink>)}</nav><Link onClick={() => setOpen(false)} to="/listings/new" className="btn-primary mt-6 flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold"><Plus size={17} /> New listing</Link></aside></div>}
    </>
  )
}
