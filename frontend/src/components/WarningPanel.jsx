import { AlertTriangle } from 'lucide-react'

export default function WarningPanel({ warnings, title = 'Validation warnings' }) {
  if (!warnings?.length) return null
  return <div className="rounded-2xl border border-[#f0d8b9] bg-[#fff9ef] p-4"><div className="flex gap-3"><AlertTriangle className="mt-0.5 shrink-0 text-[#bd732b]" size={17} /><div><h3 className="text-xs font-semibold text-[#784d22]">{title}</h3><ul className="mt-2 space-y-1.5">{warnings.map((warning) => <li key={warning} className="text-xs leading-5 text-[#936838]">• {warning}</li>)}</ul></div></div></div>
}
