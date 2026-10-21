import { ArrowUpRight } from 'lucide-react'

const tones = {
  Draft: 'bg-[#f1f2ef] text-[#606861]',
  Processing: 'bg-[#fff0dc] text-[#a56122]',
  Review: 'bg-[#e8eef9] text-[#3f679e]',
  Approved: 'bg-[#e4f1e7] text-[#317047]',
  Exported: 'bg-[#ede8f6] text-[#715797]',
}

export default function StatusCard({ label, count, icon: Icon }) {
  return (
    <div className="group rounded-2xl border border-[#e4e7e3] bg-white p-4 shadow-[0_2px_12px_rgba(28,44,33,.035)] transition hover:-translate-y-0.5 hover:shadow-[0_10px_26px_rgba(28,44,33,.07)] sm:p-5">
      <div className="flex items-start justify-between"><span className={`grid size-9 place-items-center rounded-xl ${tones[label]}`}><Icon size={17} /></span><ArrowUpRight size={16} className="text-[#c5cac6] transition group-hover:text-[#6e7b72]" /></div>
      <p className="mt-4 text-[28px] font-semibold leading-none tracking-[-0.04em] text-[#18231c]">{String(count).padStart(2, '0')}</p>
      <p className="mt-2 text-xs font-medium text-[#7d867f]">{label}</p>
    </div>
  )
}
