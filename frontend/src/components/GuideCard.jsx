import { ArrowRight, BadgeCheck, FilePenLine, History, ImagePlus, LayoutDashboard, ListChecks, RefreshCw, ScanSearch, ShieldCheck, Store, UserRoundCheck } from 'lucide-react'

const icons = { BadgeCheck, FilePenLine, History, ImagePlus, LayoutDashboard, ListChecks, RefreshCw, ScanSearch, ShieldCheck, Store, UserRoundCheck }

const tones = {
  available: 'bg-[#e4f2e8] text-[#32714a] ring-[#cee6d5]',
  simulated: 'bg-[#fff1e5] text-[#9a5b2d] ring-[#f3ddc8]',
  planned: 'bg-[#eef0f3] text-[#646d74] ring-[#dfe3e7]',
}

export default function GuideCard({ guide, onOpen }) {
  const Icon = icons[guide.icon] || FilePenLine
  return <article className="ui-surface group flex h-full flex-col rounded-2xl p-5 transition duration-300 hover:-translate-y-1 hover:border-[#c7dacd] hover:shadow-[0_18px_38px_rgba(28,65,40,.1)]">
    <div className="flex items-start justify-between gap-3"><span className="grid size-11 place-items-center rounded-[14px] bg-gradient-to-br from-[#dceee1] to-[#f5faf6] text-[#2e7048] shadow-inner ring-1 ring-[#cee3d4]"><Icon size={20} strokeWidth={1.9} /></span><span className={`rounded-full px-2.5 py-1 text-[9px] font-bold uppercase tracking-[.08em] ring-1 ${tones[guide.availabilityTone]}`}>{guide.availability}</span></div>
    <p className="mt-5 text-[10px] font-bold uppercase tracking-[.12em] text-[#77907f]">{guide.category}</p>
    <h3 className="mt-1.5 text-[16px] font-semibold tracking-[-.02em] text-[#1e2e24]">{guide.title}</h3>
    <p className="mt-2 flex-1 text-xs leading-5 text-[#78847c]">{guide.summary}</p>
    <button type="button" onClick={() => onOpen(guide)} className="group/button mt-5 inline-flex items-center gap-1.5 self-start text-xs font-semibold text-[#34714a] hover:text-[#173f2a]">Read guide <ArrowRight size={14} className="transition-transform group-hover/button:translate-x-1" /></button>
  </article>
}
