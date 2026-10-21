import { BookOutlined, CalendarOutlined, KeyOutlined, SafetyCertificateOutlined, TeamOutlined, UserOutlined } from '@ant-design/icons'
import { Button, Card, Col, Row, Space, Tag, Typography } from 'antd'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/ui/PageHeader'
import StatCard from '../components/ui/StatCard'
import { useAuth } from '../auth/AuthContext'

const roleLabels: Record<string, string> = {
  system_admin: 'Quản trị hệ thống', training_manager: 'Quản lý đào tạo', teacher: 'Giảng viên', teaching_assistant: 'Trợ giảng',
  accountant: 'Kế toán', academic_affairs: 'Giáo vụ', admissions: 'Tuyển sinh', student_services: 'Công tác sinh viên', student: 'Học viên',
}

export default function DashboardPage() {
  const { user, hasPermission } = useAuth()
  const navigate = useNavigate()
  const quickLinks = [
    { show: hasPermission('users.view'), path: '/admin/users', label: 'Quản lý người dùng', icon: <TeamOutlined /> },
    { show: hasPermission('training.view'), path: '/training/classes', label: 'Quản lý lớp học', icon: <BookOutlined /> },
    { show: hasPermission('leads.view'), path: '/admissions/leads', label: 'Quản lý tuyển sinh', icon: <UserOutlined /> },
    { show: hasPermission('training.view'), path: '/training/calendar', label: 'Lịch đào tạo', icon: <CalendarOutlined /> },
    { show: hasPermission('attendance.view'), path: '/s5/attendance', label: 'Báo cáo chuyên cần', icon: <SafetyCertificateOutlined /> },
    { show: true, path: '/profile', label: 'Hồ sơ cá nhân', icon: <UserOutlined /> },
  ].filter((item) => item.show)

  return <div className="page-wrap">
    <PageHeader title="Tổng quan hệ thống" description="Không gian làm việc được cá nhân hóa theo vai trò và quyền của tài khoản hiện tại." eyebrow="Dashboard" />

    <section className="dashboard-hero">
      <Typography.Title level={2}>Xin chào, {user?.full_name || user?.email}</Typography.Title>
      <Typography.Paragraph type="secondary">Bạn đang đăng nhập với quyền truy cập được cấp bởi hệ thống. Các module trong menu sẽ tự động hiển thị theo đúng vai trò.</Typography.Paragraph>
      <Space wrap>{user?.roles.map((role) => <Tag color="blue" key={role}>{roleLabels[role] || role}</Tag>)}</Space>
    </section>

    <Row gutter={[16, 16]} className="dashboard-grid">
      <Col xs={24} sm={12} xl={8}><StatCard icon={<UserOutlined />} label="Vai trò đang có" value={user?.roles.length || 0} hint="Theo tài khoản hiện tại" tone="blue" /></Col>
      <Col xs={24} sm={12} xl={8}><StatCard icon={<SafetyCertificateOutlined />} label="Quyền được cấp" value={user?.permissions.length || 0} hint="Dùng để kiểm soát truy cập" tone="green" /></Col>
      <Col xs={24} sm={12} xl={8}><StatCard icon={<KeyOutlined />} label="Trạng thái bảo mật" value={user?.must_change_password ? 'Cần đổi mật khẩu' : 'Bình thường'} hint="Dựa trên trạng thái tài khoản" tone={user?.must_change_password ? 'amber' : 'violet'} /></Col>
    </Row>

    <Row gutter={[16, 16]} style={{ marginTop: 18 }}>
      <Col xs={24} lg={12}>
        <Card title="Truy cập nhanh">
          <div className="quick-link-grid">
            {quickLinks.map((item) => <button key={item.path} type="button" className="quick-link" onClick={() => navigate(item.path)}><span className="quick-link-icon">{item.icon}</span><span>{item.label}</span></button>)}
          </div>
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="Quyền truy cập hiện tại" extra={<Button type="link" onClick={() => navigate('/profile')}>Xem hồ sơ</Button>}>
          <div className="permission-cloud"><Space wrap>{user?.permissions.map((permission) => <Tag key={permission}>{permission}</Tag>)}</Space></div>
        </Card>
      </Col>
    </Row>
  </div>
}
