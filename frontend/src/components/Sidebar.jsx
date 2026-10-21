import { BookOpen, History, LayoutDashboard, ListChecks, Settings } from 'lucide-react'
import { Link, NavLink } from 'react-router-dom'
import Brand from './Brand'

const links = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Listings', to: '/listings', icon: ListChecks },
  { label: 'History', to: '/history', icon: History },
  { label: 'Seller Guides', to: '/seller-guides', icon: BookOpen },
  { label: 'Settings', to: '/settings', icon: Settings },
]

export default function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-[244px] flex-col overflow-hidden border-r border-white/5 bg-gradient-to-b from-[#102d1e] via-[#123823] to-[#0e291b] px-4 py-6 shadow-[10px_0_40px_rgba(16,43,29,.08)] md:flex">
      <div aria-hidden="true" className="absolute -left-16 top-32 size-48 rounded-full bg-[#75b98a]/10 blur-3xl" />
      <div className="relative px-3"><Brand inverted /></div>
      <nav className="mt-10 space-y-1" aria-label="Main navigation">
        {links.map(({ label, to, icon: Icon }) => (
          <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `group relative flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium ${isActive ? 'bg-white/[.11] text-white shadow-[inset_0_1px_0_rgba(255,255,255,.08)]' : 'text-[#a9c0b0] hover:bg-white/[.06] hover:text-white'}`}>
            {({ isActive }) => <><span className={`absolute left-0 h-5 w-0.5 rounded-full bg-[#96d2a6] transition-opacity ${isActive ? 'opacity-100' : 'opacity-0'}`} /><Icon size={18} strokeWidth={1.9} className="transition-transform group-hover:scale-110" />{label}</>}
          </NavLink>
        ))}
      </nav>
      <div className="relative mt-auto overflow-hidden rounded-2xl border border-white/10 bg-white/[.07] p-4 shadow-inner backdrop-blur-sm">
        <div className="absolute -right-5 -top-5 size-16 rounded-full bg-[#ef8d55]/20 blur-xl" />
        <p className="relative text-xs font-semibold text-white">Need a hand?</p>
        <p className="relative mt-1 text-xs leading-5 text-[#a9c0b0]">Explore the seller guide and master your listing workflow.</p>
        <Link to="/seller-guides" className="relative mt-3 inline-flex text-xs font-semibold text-[#a9dfb7] hover:text-white">View seller guides →</Link>
      </div>
    </aside>
  )
}
