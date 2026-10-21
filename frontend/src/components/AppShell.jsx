import { Outlet } from 'react-router-dom'
import Header from './Header'
import Sidebar from './Sidebar'

export default function AppShell() {
  return <div className="min-h-screen bg-[#f7f8f6]"><Sidebar /><div className="md:pl-[232px]"><Header /><main className="mx-auto max-w-[1450px] px-4 py-6 sm:px-7 lg:px-9 lg:py-8"><Outlet /></main></div></div>
}
