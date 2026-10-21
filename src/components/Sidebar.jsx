import { History, LayoutDashboard, ListChecks, Settings } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import Brand from './Brand'

const links = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Listings', to: '/listings', icon: ListChecks },
  { label: 'History', to: '/history', icon: History },
  { label: 'Settings', to: '/settings', icon: Settings },
]

export default function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-[232px] flex-col border-r border-[#e5e8e4] bg-[#fbfcfa] px-4 py-6 md:flex">
      <div className="px-3"><Brand /></div>
      <nav className="mt-10 space-y-1" aria-label="Main navigation">
        {links.map(({ label, to, icon: Icon }) => (
          <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${isActive ? 'bg-[#e8f2ea] text-[#173f2a]' : 'text-[#67716a] hover:bg-[#f1f3f0] hover:text-[#243029]'}`}>
            <Icon size={18} strokeWidth={1.9} />{label}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto rounded-2xl border border-[#e0e5df] bg-white p-4">
        <p className="text-xs font-semibold text-[#243029]">Need a hand?</p>
        <p className="mt-1 text-xs leading-5 text-[#7b847e]">Visit the seller guide to learn the listing workflow.</p>
        <button className="mt-3 text-xs font-semibold text-[#2c754b] hover:text-[#173f2a]">View seller guide →</button>
      </div>
    </aside>
  )
}
