import { ArrowUpRight } from 'lucide-react'

export default function StatusCard({ label, count, icon: Icon }) {
  return (
    <div className="ui-surface group relative overflow-hidden rounded-2xl p-4 transition duration-300 hover:-translate-y-1 hover:border-[#c9d9cd] hover:shadow-[0_18px_38px_rgba(28,65,40,.11)] sm:p-5">
      <span className="absolute -right-8 -top-8 size-20 rounded-full bg-[#dff2e5]/50 opacity-0 blur-2xl transition-opacity duration-300 group-hover:opacity-100" />
      <div className="relative flex items-start justify-between"><span className="grid size-11 place-items-center rounded-[14px] bg-gradient-to-br from-[#dceee1] to-[#f5faf6] text-[#2e7048] shadow-[inset_0_1px_0_rgba(255,255,255,.9),0_5px_14px_rgba(47,113,75,.1)] ring-1 ring-[#cee3d4]"><Icon size={20} strokeWidth={1.9} /></span><ArrowUpRight size={16} className="text-[#c5cac6] transition group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-[#477858]" /></div>
      <p className="relative mt-5 text-[30px] font-semibold leading-none tracking-[-0.05em] text-[#18231c]">{String(count).padStart(2, '0')}</p>
      <p className="relative mt-2 flex items-center gap-2 text-xs font-semibold text-[#77837b]"><span className="size-1.5 rounded-full bg-[#75a984]" />{label}</p>
    </div>
  )
}
