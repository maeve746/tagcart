import { Tags } from 'lucide-react'

export default function Brand({ compact = false, inverted = false }) {
  return (
    <div className="flex items-center gap-3">
      <span className="grid size-10 shrink-0 place-items-center rounded-[14px] bg-gradient-to-br from-[#6fb181] to-[#d3edda] text-[#123c25] shadow-[0_10px_25px_rgba(7,27,17,.22)] ring-1 ring-white/20"><Tags size={19} strokeWidth={2.3} /></span>
      {!compact && <span className={`text-[20px] font-bold tracking-[-0.045em] ${inverted ? 'text-white' : 'text-[#16251b]'}`}>Tag<span className={inverted ? 'text-[#9ed3aa]' : 'text-[#34714a]'}>Cart</span></span>}
    </div>
  )
}
