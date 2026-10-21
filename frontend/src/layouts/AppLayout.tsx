import {
  AppstoreOutlined,
  BookOutlined,
  CalendarOutlined,
  DashboardOutlined,
  FileDoneOutlined,
  FileTextOutlined,
  KeyOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuOutlined,
  MenuUnfoldOutlined,
  PhoneOutlined,
  SafetyCertificateOutlined,
  ScheduleOutlined,
  TeamOutlined,
  UserOutlined,
  UploadOutlined,
} from '@ant-design/icons'
import { Breadcrumb, Button, Drawer, Dropdown, Grid, Layout, Menu, Typography } from 'antd'
import type { MenuProps } from 'antd'
import type { ReactNode } from 'react'
import { useMemo, useState } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import FeaturePage from '../components/function-ui/FeaturePage'
import UserAvatar from '../features/profile/UserAvatar'

const { Header, Sider, Content } = Layout

const roleLabels: Record<string, string> = {
  system_admin: 'Quản trị hệ thống',
  training_manager: 'Quản lý đào tạo',
  teacher: 'Giảng viên',
  teaching_assistant: 'Trợ giảng',
  accountant: 'Kế toán',
  academic_affairs: 'Giáo vụ',
  admissions: 'Tuyển sinh',
  student_services: 'Công tác sinh viên',
  student: 'Học viên',
}

const routeLabels: Record<string, { title: string; group: string }> = {
  '/dashboard': { title: 'Tổng quan', group: 'Trang chủ' },
  '/profile': { title: 'Hồ sơ cá nhân', group: 'Tài khoản' },
  '/change-password': { title: 'Đổi mật khẩu', group: 'Tài khoản' },
  '/admin/users': { title: 'Quản lý người dùng', group: 'Quản trị' },
  '/admin/import-users': { title: 'Nhập dữ liệu người dùng', group: 'Quản trị' },
  '/admin/roles': { title: 'Vai trò & phân quyền', group: 'Quản trị' },
  '/training': { title: 'Danh mục đào tạo', group: 'Đào tạo' },
  '/training/students': { title: 'Hồ sơ học viên', group: 'Đào tạo' },
  '/training/classes': { title: 'Quản lý lớp học', group: 'Đào tạo' },
  '/training/enrollments': { title: 'Ghi danh học viên', group: 'Đào tạo' },
  '/training/class-overview': { title: 'Danh sách lớp', group: 'Đào tạo' },
  '/training/class-staff': { title: 'Phân công giảng dạy', group: 'Đào tạo' },
  '/training/rooms': { title: 'Phòng học', group: 'Đào tạo' },
  '/admissions/leads': { title: 'Quản lý lead', group: 'Tuyển sinh' },
  '/admissions/lead-assignment': { title: 'Phân công lead', group: 'Tuyển sinh' },
  '/admissions/funnel': { title: 'Phễu tuyển sinh', group: 'Tuyển sinh' },
  '/admissions/care': { title: 'Chăm sóc lead', group: 'Tuyển sinh' },
  '/admissions/convert': { title: 'Chuyển lead thành học viên', group: 'Tuyển sinh' },
  '/training/timetable-generate': { title: 'Sinh thời khóa biểu', group: 'Lịch & chuyên cần' },
  '/training/holidays': { title: 'Ngày nghỉ lễ', group: 'Lịch & chuyên cần' },
  '/training/schedule-conflicts': { title: 'Kiểm tra xung đột lịch', group: 'Lịch & chuyên cần' },
  '/training/schedule-changes': { title: 'Điều chỉnh buổi học', group: 'Lịch & chuyên cần' },
  '/training/calendar': { title: 'Lịch đào tạo', group: 'Lịch & chuyên cần' },
  '/my-schedule': { title: 'Lịch học của tôi', group: 'Lịch & chuyên cần' },
  '/training/student-status': { title: 'Trạng thái học viên', group: 'Lịch & chuyên cần' },
  '/training/attendance': { title: 'Điểm danh', group: 'Lịch & chuyên cần' },
  '/absence-requests': { title: 'Xin phép vắng', group: 'Lịch & chuyên cần' },
}


type FeatureRouteMeta = {
  eyebrow: string
  title: string
  description: string
  tone: 'blue' | 'violet' | 'cyan' | 'green' | 'amber'
  icon: ReactNode
  className: string
}

const featureRouteMeta: Record<string, FeatureRouteMeta> = {
  '/admin/roles': { eyebrow: 'Quản trị', title: 'Vai trò & phân quyền', description: 'Thiết lập quyền truy cập theo vai trò và bảo đảm mỗi nhóm người dùng chỉ thấy đúng chức năng được phép.', tone: 'violet', icon: <SafetyCertificateOutlined />, className: 'feature-route-roles' },
  '/training': { eyebrow: 'Đào tạo', title: 'Danh mục đào tạo', description: 'Quản lý chương trình, môn học, lộ trình và cấu trúc buổi học trong một không gian thống nhất.', tone: 'blue', icon: <BookOutlined />, className: 'feature-route-training' },
  '/training/students': { eyebrow: 'Đào tạo', title: 'Hồ sơ học viên', description: 'Tra cứu hồ sơ, lớp đang học và lịch sử đào tạo của từng học viên.', tone: 'blue', icon: <TeamOutlined />, className: 'feature-route-students' },
  '/training/enrollments': { eyebrow: 'Đào tạo', title: 'Ghi danh học viên', description: 'Thêm học viên vào lớp, theo dõi sĩ số và kiểm soát các điều kiện ghi danh.', tone: 'blue', icon: <TeamOutlined />, className: 'feature-route-enrollments' },
  '/training/class-overview': { eyebrow: 'Đào tạo', title: 'Danh sách lớp', description: 'Theo dõi trạng thái, sĩ số và tiến độ học tập của toàn bộ lớp đào tạo.', tone: 'blue', icon: <AppstoreOutlined />, className: 'feature-route-class-overview' },
  '/training/class-staff': { eyebrow: 'Đào tạo', title: 'Phân công giảng dạy', description: 'Phân công giảng viên chính và trợ giảng cho từng môn trong từng lớp.', tone: 'blue', icon: <TeamOutlined />, className: 'feature-route-class-staff' },
  '/training/rooms': { eyebrow: 'Đào tạo', title: 'Phòng học', description: 'Quản lý phòng trực tiếp, phòng trực tuyến và phân bổ phòng phù hợp cho lớp học.', tone: 'blue', icon: <BookOutlined />, className: 'feature-route-rooms' },
  '/admissions/leads': { eyebrow: 'Tuyển sinh', title: 'Quản lý lead', description: 'Tạo, cập nhật và theo dõi thông tin khách hàng tiềm năng trong toàn bộ quá trình tuyển sinh.', tone: 'cyan', icon: <PhoneOutlined />, className: 'feature-route-leads' },
  '/admissions/funnel': { eyebrow: 'Tuyển sinh', title: 'Phễu tuyển sinh', description: 'Theo dõi lead theo từng giai đoạn và di chuyển trạng thái trực quan trong quy trình tuyển sinh.', tone: 'cyan', icon: <AppstoreOutlined />, className: 'feature-route-funnel' },
  '/admissions/care': { eyebrow: 'Tuyển sinh', title: 'Chăm sóc lead', description: 'Ghi nhận cuộc gọi, tin nhắn, cuộc gặp và nhắc lịch chăm sóc để không bỏ sót khách hàng.', tone: 'cyan', icon: <PhoneOutlined />, className: 'feature-route-care' },
  '/admissions/convert': { eyebrow: 'Tuyển sinh', title: 'Lead → học viên', description: 'Chuyển đổi lead đã hoàn tất tư vấn thành hồ sơ học viên và tài khoản sử dụng hệ thống.', tone: 'cyan', icon: <UserOutlined />, className: 'feature-route-convert' },
  '/training/timetable-generate': { eyebrow: 'Lịch & chuyên cần', title: 'Sinh thời khóa biểu', description: 'Tạo lịch học tự động theo lớp, ngày học, khung giờ và kiểm tra xung đột trước khi lưu.', tone: 'amber', icon: <ScheduleOutlined />, className: 'feature-route-timetable' },
  '/training/holidays': { eyebrow: 'Lịch & chuyên cần', title: 'Ngày nghỉ lễ', description: 'Quản lý ngày nghỉ để hệ thống tự động bỏ qua khi sinh thời khóa biểu.', tone: 'amber', icon: <CalendarOutlined />, className: 'feature-route-holidays' },
  '/training/schedule-conflicts': { eyebrow: 'Lịch & chuyên cần', title: 'Kiểm tra xung đột lịch', description: 'Kiểm tra nhanh trùng phòng và trùng giảng viên trước khi xác nhận lịch học.', tone: 'amber', icon: <ScheduleOutlined />, className: 'feature-route-conflicts' },
  '/training/schedule-changes': { eyebrow: 'Lịch & chuyên cần', title: 'Điều chỉnh buổi học', description: 'Dời, sửa hoặc hủy buổi học và lưu lại toàn bộ lý do thay đổi.', tone: 'amber', icon: <CalendarOutlined />, className: 'feature-route-schedule-changes' },
  '/training/calendar': { eyebrow: 'Lịch & chuyên cần', title: 'Lịch đào tạo', description: 'Quan sát thời khóa biểu theo tuần hoặc tháng với thông tin lớp, môn, giảng viên và phòng.', tone: 'amber', icon: <CalendarOutlined />, className: 'feature-route-calendar' },
  '/my-schedule': { eyebrow: 'Lịch & chuyên cần', title: 'Lịch học của tôi', description: 'Theo dõi buổi học kế tiếp và toàn bộ lịch học trong tuần của học viên.', tone: 'amber', icon: <CalendarOutlined />, className: 'feature-route-my-schedule' },
  '/training/student-status': { eyebrow: 'Lịch & chuyên cần', title: 'Trạng thái học viên', description: 'Ghi nhận bảo lưu, chuyển lớp, thôi học và theo dõi lịch sử thay đổi theo ngày hiệu lực.', tone: 'amber', icon: <TeamOutlined />, className: 'feature-route-student-status' },
  '/training/attendance': { eyebrow: 'Lịch & chuyên cần', title: 'Điểm danh', description: 'Điểm danh theo buổi học với trạng thái rõ ràng và thao tác nhanh cho giảng viên.', tone: 'amber', icon: <FileDoneOutlined />, className: 'feature-route-attendance' },
  '/absence-requests': { eyebrow: 'Lịch & chuyên cần', title: 'Xin phép vắng', description: 'Học viên gửi đơn xin phép và giảng viên xử lý kết quả ngay trong cùng một luồng.', tone: 'amber', icon: <FileTextOutlined />, className: 'feature-route-absence' },
}

const pagesWithOwnFeatureHero = new Set([
  '/admin/users',
  '/admin/import-users',
  '/admissions/lead-assignment',
  '/training/classes',
])

export default function AppLayout() {
  const { user, logout, hasPermission } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const screens = Grid.useBreakpoint()
  const mobile = !screens.md
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(false)

  const menuItems = useMemo<MenuProps['items']>(() => {
    const groups: MenuProps['items'] = []
    const pushGroup = (key: string, label: string, children: MenuProps['items']) => {
      const visible = (children || []).filter(Boolean) as NonNullable<MenuProps['items']>
      if (visible.length) groups.push({ key, type: 'group', label, children: visible })
    }

    pushGroup('home', 'TỔNG QUAN', [
      hasPermission('dashboard.view') ? { key: '/dashboard', icon: <DashboardOutlined />, label: 'Tổng quan' } : null,
      { key: '/profile', icon: <UserOutlined />, label: 'Hồ sơ cá nhân' },
    ])

    pushGroup('admin', 'QUẢN TRỊ', [
      hasPermission('users.view') ? { key: '/admin/users', icon: <TeamOutlined />, label: 'Người dùng' } : null,
      hasPermission('users.import') ? { key: '/admin/import-users', icon: <UploadOutlined />, label: 'Nhập Excel' } : null,
      hasPermission('roles.view') ? { key: '/admin/roles', icon: <SafetyCertificateOutlined />, label: 'Vai trò & quyền' } : null,
    ])

    pushGroup('admissions', 'TUYỂN SINH', [
      hasPermission('leads.view') ? { key: '/admissions/leads', icon: <PhoneOutlined />, label: 'Quản lý lead' } : null,
      hasPermission('leads.view') ? { key: '/admissions/lead-assignment', icon: <TeamOutlined />, label: 'Phân công lead' } : null,
      hasPermission('leads.view') ? { key: '/admissions/funnel', icon: <AppstoreOutlined />, label: 'Phễu tuyển sinh' } : null,
      hasPermission('leads.view') ? { key: '/admissions/care', icon: <PhoneOutlined />, label: 'Chăm sóc lead' } : null,
      hasPermission('leads.view') ? { key: '/admissions/convert', icon: <UserOutlined />, label: 'Lead → học viên' } : null,
    ])

    pushGroup('training', 'ĐÀO TẠO', [
      hasPermission('training.view') ? { key: '/training', icon: <BookOutlined />, label: 'Danh mục đào tạo' } : null,
      hasPermission('training.view') ? { key: '/training/students', icon: <TeamOutlined />, label: 'Hồ sơ học viên' } : null,
      hasPermission('training.view') ? { key: '/training/classes', icon: <BookOutlined />, label: 'Lớp học' } : null,
      hasPermission('training.view') ? { key: '/training/enrollments', icon: <TeamOutlined />, label: 'Ghi danh' } : null,
      hasPermission('training.view') ? { key: '/training/class-overview', icon: <AppstoreOutlined />, label: 'Danh sách lớp' } : null,
      hasPermission('training.view') ? { key: '/training/class-staff', icon: <TeamOutlined />, label: 'Phân công giảng dạy' } : null,
      hasPermission('training.view') ? { key: '/training/rooms', icon: <BookOutlined />, label: 'Phòng học' } : null,
    ])

    pushGroup('schedule', 'LỊCH & CHUYÊN CẦN', [
      hasPermission('training.view') ? { key: '/training/timetable-generate', icon: <ScheduleOutlined />, label: 'Sinh thời khóa biểu' } : null,
      hasPermission('training.view') ? { key: '/training/holidays', icon: <CalendarOutlined />, label: 'Ngày nghỉ lễ' } : null,
      hasPermission('training.view') ? { key: '/training/schedule-conflicts', icon: <ScheduleOutlined />, label: 'Xung đột lịch' } : null,
      hasPermission('training.view') ? { key: '/training/schedule-changes', icon: <CalendarOutlined />, label: 'Điều chỉnh buổi học' } : null,
      hasPermission('training.view') ? { key: '/training/calendar', icon: <CalendarOutlined />, label: 'Lịch đào tạo' } : null,
      hasPermission('training.view') ? { key: '/my-schedule', icon: <CalendarOutlined />, label: 'Lịch học của tôi' } : null,
      hasPermission('training.view') ? { key: '/training/student-status', icon: <TeamOutlined />, label: 'Trạng thái học viên' } : null,
      hasPermission('attendance.view') ? { key: '/training/attendance', icon: <FileDoneOutlined />, label: 'Điểm danh' } : null,
      hasPermission('training.view') ? { key: '/absence-requests', icon: <FileTextOutlined />, label: 'Xin phép vắng' } : null,
    ])

    pushGroup('assessment', 'BÀI TẬP & ĐÁNH GIÁ', [
    ])

    pushGroup('account', 'TÀI KHOẢN', [
      { key: '/change-password', icon: <KeyOutlined />, label: 'Đổi mật khẩu' },
    ])

    return groups
  }, [hasPermission])

  const current = routeLabels[location.pathname] || { title: 'Hệ thống quản lý đào tạo', group: 'CodeGym' }
  const featureMeta = featureRouteMeta[location.pathname]
  const role = user?.roles?.[0]
  const roleLabel = role ? roleLabels[role] || role : 'Người dùng'

  const menu = <Menu
    className="app-menu"
    mode="inline"
    theme="dark"
    inlineCollapsed={!mobile && collapsed}
    selectedKeys={[location.pathname]}
    items={menuItems}
    onClick={({ key }) => { navigate(key); setDrawerOpen(false) }}
  />

  const handleLogout = async () => {
    await logout()
    navigate('/login', { replace: true, state: { notice: 'Bạn đã đăng xuất an toàn.' } })
  }

  const accountItems: MenuProps['items'] = [
    { key: 'profile', icon: <UserOutlined />, label: 'Hồ sơ cá nhân' },
    { key: 'password', icon: <KeyOutlined />, label: 'Đổi mật khẩu' },
    { type: 'divider' },
    { key: 'logout', icon: <LogoutOutlined />, label: 'Đăng xuất', danger: true },
  ]

  const onAccountClick: MenuProps['onClick'] = async ({ key }) => {
    if (key === 'profile') navigate('/profile')
    if (key === 'password') navigate('/change-password')
    if (key === 'logout') await handleLogout()
  }

  return <Layout className="app-shell">
    {!mobile && <Sider
      width={284}
      collapsedWidth={88}
      collapsed={collapsed}
      trigger={null}
      theme="dark"
      className="app-sider"
    >
      <div className={`brand-block ${collapsed ? 'is-collapsed' : ''}`}>
        <div className="brand-mark">CG</div>
        {!collapsed && <div className="brand-copy"><strong>CodeGym</strong><small>University Management</small></div>}
      </div>
      <div className="app-menu-scroll">{menu}</div>
      <div className="sider-footer">
        <Button type="text" className="sider-collapse" icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />} onClick={() => setCollapsed(v => !v)}>
          {!collapsed && 'Thu gọn menu'}
        </Button>
      </div>
    </Sider>}

    <Drawer
      title={<div className="drawer-brand"><div className="brand-mark">CG</div><span>Hệ thống đào tạo</span></div>}
      placement="left"
      width={300}
      open={drawerOpen}
      onClose={() => setDrawerOpen(false)}
      className="mobile-nav-drawer"
      styles={{ body: { padding: 0, background: '#0f172a' } }}
    >{menu}</Drawer>

    <Layout className="app-main-layout">
      <Header className="app-header">
        <div className="header-left">
          {mobile && <Button type="text" className="mobile-menu-btn" icon={<MenuOutlined />} onClick={() => setDrawerOpen(true)} />}
          <div className="header-title-block">
            <Breadcrumb items={[{ title: current.group }, { title: current.title }]} />
            <Typography.Text className="header-page-title">{current.title}</Typography.Text>
          </div>
        </div>
        <Dropdown menu={{ items: accountItems, onClick: onAccountClick }} trigger={['click']} placement="bottomRight">
          <button type="button" className="account-trigger" aria-label="Mở menu tài khoản">
            <UserAvatar />
            {!mobile && <div className="account-copy"><strong>{user?.full_name || user?.email}</strong><span>{roleLabel}</span></div>}
          </button>
        </Dropdown>
      </Header>
      <Content className="app-content">
        {featureMeta && !pagesWithOwnFeatureHero.has(location.pathname) ? (
          <FeaturePage
            eyebrow={featureMeta.eyebrow}
            title={featureMeta.title}
            description={featureMeta.description}
            icon={featureMeta.icon}
            tone={featureMeta.tone}
            className={featureMeta.className}
          >
            <div className="feature-auto-shell"><Outlet /></div>
          </FeaturePage>
        ) : <Outlet />}
      </Content>
    </Layout>
  </Layout>
}
