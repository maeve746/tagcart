import { Clock3, Settings } from 'lucide-react'

export default function PlaceholderPage({ type }) {
  const isHistory = type === 'History'; const Icon = isHistory ? Clock3 : Settings
  return <div><h2 className="text-2xl font-semibold tracking-[-0.03em] text-[#19251d]">{type}</h2><p className="mt-1 text-sm text-[#7b847e]">{isHistory ? 'Track listing activity and exports.' : 'Manage your seller preferences and integrations.'}</p><div className="mt-6 flex min-h-[360px] flex-col items-center justify-center rounded-2xl border border-[#e3e6e2] bg-white p-8 text-center"><span className="grid size-12 place-items-center rounded-2xl bg-[#e9f1ea] text-[#477457]"><Icon size={21} /></span><h3 className="mt-4 text-sm font-semibold text-[#2e3931]">{type} is ready for integration</h3><p className="mt-1 max-w-sm text-xs leading-5 text-[#858e88]">This frontend state is intentionally empty until the FastAPI endpoints are connected.</p></div></div>
}
