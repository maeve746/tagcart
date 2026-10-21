import { Link } from 'react-router-dom'
export default function NotFoundPage() { return <div className="py-20 text-center"><p className="text-5xl font-semibold text-[#c8d6ca]">404</p><h2 className="mt-4 text-lg font-semibold text-[#27332b]">Page not found</h2><Link to="/" className="mt-4 inline-block text-sm font-semibold text-[#34714a]">Return to dashboard</Link></div> }
