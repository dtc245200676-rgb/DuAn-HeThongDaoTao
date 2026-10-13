import { ConfigProvider } from 'antd'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import './App.css'
import { AuthProvider } from './auth/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import AppLayout from './layouts/AppLayout'
import AccessDeniedPage from './pages/AccessDeniedPage'
import ActivatePage from './pages/ActivatePage'
import ChangePasswordPage from './pages/ChangePasswordPage'
import ClassEnrollmentPage from './pages/ClassEnrollmentPage'
import ClassManagementPage from './pages/ClassManagementPage'
import ClassOverviewPage from './pages/ClassOverviewPage'
import ClassStaffPage from './pages/ClassStaffPage'
import ConsultationPage from './pages/ConsultationPage'
import DashboardPage from './pages/DashboardPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ImportUsersPage from './pages/ImportUsersPage'
import LeadAssignmentPage from './pages/LeadAssignmentPage'
import LeadCarePage from './pages/LeadCarePage'
import LeadConvertPage from './pages/LeadConvertPage'
import LeadCrudPage from './pages/LeadCrudPage'
import LeadFunnelPage from './pages/LeadFunnelPage'
import LoginPage from './pages/LoginPage'
import NotFoundPage from './pages/NotFoundPage'
import ProfilePage from './pages/ProfilePage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import RoleManagementPage from './pages/RoleManagementPage'
import RoomManagementPage from './pages/RoomManagementPage'
import StudentRecordsPage from './pages/StudentRecordsPage'
import TrainingManagementPage from './pages/TrainingManagementPage'
import UserManagementPage from './pages/UserManagementPage'

export default function App() {
  return <ConfigProvider theme={{ token: { colorPrimary: '#1677ff', borderRadius: 8 } }}>
    <BrowserRouter><AuthProvider><Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route path="/activate" element={<ActivatePage />} />
      <Route path="/consultation" element={<ConsultationPage />} />
      <Route element={<ProtectedRoute />}><Route element={<AppLayout />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/change-password" element={<ChangePasswordPage />} />
        <Route path="/403" element={<AccessDeniedPage />} />
        <Route element={<ProtectedRoute permission="users.view" />}><Route path="/admin/users" element={<UserManagementPage />} /></Route>
        <Route element={<ProtectedRoute permission="users.import" />}><Route path="/admin/import-users" element={<ImportUsersPage />} /></Route>
        <Route element={<ProtectedRoute permission="roles.view" />}><Route path="/admin/roles" element={<RoleManagementPage />} /></Route>
        <Route element={<ProtectedRoute permission="training.view" />}>
          <Route path="/training" element={<TrainingManagementPage />} />
          <Route path="/training/students" element={<StudentRecordsPage />} />
          <Route path="/training/classes" element={<ClassManagementPage />} />
          <Route path="/training/enrollments" element={<ClassEnrollmentPage />} />
          <Route path="/training/class-overview" element={<ClassOverviewPage />} />
          <Route path="/training/class-staff" element={<ClassStaffPage />} />
          <Route path="/training/rooms" element={<RoomManagementPage />} />
        </Route>
        <Route element={<ProtectedRoute permission="leads.view" />}>
          <Route path="/admissions/leads" element={<LeadCrudPage />} />
          <Route path="/admissions/lead-assignment" element={<LeadAssignmentPage />} />
          <Route path="/admissions/funnel" element={<LeadFunnelPage />} />
          <Route path="/admissions/care" element={<LeadCarePage />} />
          <Route path="/admissions/convert" element={<LeadConvertPage />} />
        </Route>
      </Route></Route>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes></AuthProvider></BrowserRouter>
  </ConfigProvider>
}
