import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/context/AuthContext'
import { ToastProvider } from '@/components/ui/toast'
import Layout from '@/components/layout/Layout'
import Login from '@/pages/auth/Login'
import Dashboard from '@/pages/dashboard/Dashboard'
import StudentsList from '@/pages/students/StudentsList'
import EmployeesList from '@/pages/employees/EmployeesList'
import DepartmentsList from '@/pages/departments/DepartmentsList'
import AttendancePage from '@/pages/attendance/AttendancePage'
import FeesPage from '@/pages/fees/FeesPage'
import ResultsPage from '@/pages/results/ResultsPage'
import ReportsPage from '@/pages/reports/ReportsPage'
import UsersPage from '@/pages/users/UsersPage'
import SettingsPage from '@/pages/settings/SettingsPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  if (isLoading)
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="students" element={<StudentsList />} />
        <Route path="employees" element={<EmployeesList />} />
        <Route path="departments" element={<DepartmentsList />} />
        <Route path="attendance" element={<AttendancePage />} />
        <Route path="fees" element={<FeesPage />} />
        <Route path="results" element={<ResultsPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="users" element={<UsersPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </ToastProvider>
  )
}
