import { Route, Routes } from 'react-router-dom'
import AppShell from './components/AppShell'
import DashboardPage from './pages/DashboardPage'
import ListingDetailsPage from './pages/ListingDetailsPage'
import ListingsPage from './pages/ListingsPage'
import NewListingPage from './pages/NewListingPage'
import NotFoundPage from './pages/NotFoundPage'
import PlaceholderPage from './pages/PlaceholderPage'

export default function App() {
  return <Routes><Route element={<AppShell />}><Route path="/" element={<DashboardPage />} /><Route path="/listings" element={<ListingsPage />} /><Route path="/listings/new" element={<NewListingPage />} /><Route path="/listings/:id" element={<ListingDetailsPage />} /><Route path="/history" element={<PlaceholderPage type="History" />} /><Route path="/settings" element={<PlaceholderPage type="Settings" />} /><Route path="*" element={<NotFoundPage />} /></Route></Routes>
}
