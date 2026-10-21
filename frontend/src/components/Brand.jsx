import { Tags } from 'lucide-react'

export default function Brand({ compact = false }) {
  return (
    <div className="flex items-center gap-3">
      <span className="grid size-9 shrink-0 place-items-center rounded-xl bg-[#173f2a] text-white shadow-[0_8px_20px_rgba(23,63,42,.2)]"><Tags size={18} strokeWidth={2.2} /></span>
      {!compact && <span className="text-[19px] font-bold tracking-[-0.04em] text-[#16251b]">TagCart</span>}
    </div>
  )
}
