import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { authService } from '../services/authService'

export default function ProtectedRoute() {
  const location = useLocation()
  return authService.getSession() ? <Outlet /> : <Navigate to="/login" replace state={{ from: location.pathname }} />
}
