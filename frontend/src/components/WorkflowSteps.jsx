import { Check } from 'lucide-react'

const steps = ['Upload', 'Analyze', 'Review', 'Approve & export']
export default function WorkflowSteps({ current }) {
  return <div className="mb-6 overflow-x-auto"><div className="flex min-w-[520px] items-center rounded-2xl border border-[#e3e7e3] bg-white px-4 py-3">{steps.map((step, index) => <div key={step} className="flex flex-1 items-center last:flex-none"><span className={`grid size-7 shrink-0 place-items-center rounded-full text-[11px] font-bold ${index < current ? 'bg-[#4b8960] text-white' : index === current ? 'bg-[#173f2a] text-white ring-4 ring-[#dce9df]' : 'bg-[#eef1ee] text-[#8b938d]'}`}>{index < current ? <Check size={13} /> : index + 1}</span><span className={`ml-2 whitespace-nowrap text-[11px] font-semibold ${index <= current ? 'text-[#314139]' : 'text-[#9aa19c]'}`}>{step}</span>{index < steps.length - 1 && <span className={`mx-3 h-px flex-1 ${index < current ? 'bg-[#71a17f]' : 'bg-[#e1e5e1]'}`} />}</div>)}</div></div>
}
