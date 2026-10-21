import { Outlet } from 'react-router-dom'
import Header from './Header'
import Sidebar from './Sidebar'

export default function AppShell() {
  return <div className="relative min-h-screen overflow-x-hidden bg-[#f5f8f5]"><div aria-hidden="true" className="pointer-events-none fixed -right-40 top-16 size-[430px] rounded-full bg-[#dff2e5]/45 blur-3xl" /><div aria-hidden="true" className="pointer-events-none fixed bottom-0 left-[28%] size-72 rounded-full bg-[#f8e6d9]/30 blur-3xl" /><Sidebar /><div className="relative md:pl-[244px]"><Header /><main className="mx-auto max-w-[1450px] px-4 py-6 sm:px-7 lg:px-10 lg:py-9"><div className="page-enter"><Outlet /></div></main></div></div>
}
