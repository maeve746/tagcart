import { Route, Routes } from 'react-router-dom'
import AppShell from './components/AppShell'
import ProtectedRoute from './components/ProtectedRoute'
import AnalysisPage from './pages/AnalysisPage'
import AuthPage from './pages/AuthPage'
import DashboardPage from './pages/DashboardPage'
import HistoryPage from './pages/HistoryPage'
import ListingDetailsPage from './pages/ListingDetailsPage'
import ListingPreviewPage from './pages/ListingPreviewPage'
import ListingsPage from './pages/ListingsPage'
import NewListingPage from './pages/NewListingPage'
import NotFoundPage from './pages/NotFoundPage'
import SettingsPage from './pages/SettingsPage'
import VersionViewerPage from './pages/VersionViewerPage'

export default function App() {
  return <Routes>
    <Route path="/login" element={<AuthPage mode="login" />} />
    <Route path="/register" element={<AuthPage mode="register" />} />
    <Route element={<ProtectedRoute />}>
      <Route element={<AppShell />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/listings" element={<ListingsPage />} />
        <Route path="/listings/new" element={<NewListingPage />} />
        <Route path="/listings/:id" element={<ListingDetailsPage />} />
        <Route path="/listings/:id/analysis" element={<AnalysisPage />} />
        <Route path="/listings/:id/preview" element={<ListingPreviewPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/history/:id" element={<VersionViewerPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Route>
  </Routes>
}
