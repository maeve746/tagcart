import { Check, Clock3, FilePenLine, LoaderCircle, Send } from 'lucide-react'

const styles = {
  Draft: ['bg-[#f0f1ef] text-[#646b66]', FilePenLine],
  Processing: ['bg-[#fff1df] text-[#a76223]', LoaderCircle],
  Review: ['bg-[#e9effa] text-[#426ca5]', Clock3],
  Approved: ['bg-[#e6f2e8] text-[#327149]', Check],
  Exported: ['bg-[#eee9f7] text-[#745a9d]', Send],
}

export default function StatusBadge({ status }) {
  const [className, Icon] = styles[status] || styles.Draft
  return <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${className}`}><Icon size={12.5} strokeWidth={2.2} />{status}</span>
}
