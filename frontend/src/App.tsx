import { ConfigProvider } from 'antd'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import './App.css'
import { AuthProvider } from './auth/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import AppLayout from './layouts/AppLayout'
import AccessDeniedPage from './pages/AccessDeniedPage'
import ActivatePage from './pages/ActivatePage'
import AbsenceRequestsPage from './pages/AbsenceRequestsPage'
import AttendancePage from './pages/AttendancePage'
import ChangePasswordPage from './pages/ChangePasswordPage'
import ClassEnrollmentPage from './pages/ClassEnrollmentPage'
import ClassManagementPage from './pages/ClassManagementPage'
import ClassOverviewPage from './pages/ClassOverviewPage'
import ClassStaffPage from './pages/ClassStaffPage'
import ConsultationPage from './pages/ConsultationPage'
import DashboardPage from './pages/DashboardPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import HolidayManagementPage from './pages/HolidayManagementPage'
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
import ScheduleCalendarPage from './pages/ScheduleCalendarPage'
import ScheduleChangesPage from './pages/ScheduleChangesPage'
import ScheduleConflictsPage from './pages/ScheduleConflictsPage'
import StudentRecordsPage from './pages/StudentRecordsPage'
import StudentSchedulePage from './pages/StudentSchedulePage'
import StudentStatusPage from './pages/StudentStatusPage'
import TimetableGeneratePage from './pages/TimetableGeneratePage'
import TrainingManagementPage from './pages/TrainingManagementPage'
import UserManagementPage from './pages/UserManagementPage'

export default function App() {
  return <ConfigProvider theme={{
    token: {
      colorPrimary: '#2563EB',
      colorSuccess: '#10B981',
      colorWarning: '#F59E0B',
      colorError: '#EF4444',
      colorText: '#0F172A',
      colorTextSecondary: '#64748B',
      colorBorder: '#E2E8F0',
      colorBgLayout: '#F8FAFC',
      borderRadius: 10,
      borderRadiusLG: 14,
      controlHeight: 40,
      fontFamily: 'Inter, "Be Vietnam Pro", ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    },
    components: {
      Button: { primaryShadow: '0 5px 12px rgba(37,99,235,.18)' },
      Card: { headerFontSize: 16 },
      Table: { headerBg: '#F8FAFC', headerColor: '#334155' },
      Menu: { darkItemBg: '#0F172A', darkSubMenuItemBg: '#0F172A', darkItemSelectedBg: '#2563EB' },
    },
  }}>
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
          <Route path="/training/timetable-generate" element={<TimetableGeneratePage />} />
          <Route path="/training/holidays" element={<HolidayManagementPage />} />
          <Route path="/training/schedule-conflicts" element={<ScheduleConflictsPage />} />
          <Route path="/training/schedule-changes" element={<ScheduleChangesPage />} />
          <Route path="/training/calendar" element={<ScheduleCalendarPage />} />
          <Route path="/my-schedule" element={<StudentSchedulePage />} />
          <Route path="/training/student-status" element={<StudentStatusPage />} />
          <Route path="/training/attendance" element={<AttendancePage />} />
          <Route path="/absence-requests" element={<AbsenceRequestsPage />} />
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
