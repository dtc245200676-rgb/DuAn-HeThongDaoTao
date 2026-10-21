import { BookOutlined,DashboardOutlined,KeyOutlined,LogoutOutlined,MenuOutlined,PhoneOutlined,SafetyCertificateOutlined,TeamOutlined,UserOutlined,UploadOutlined } from '@ant-design/icons'
import { Button,Drawer,Grid,Layout,Menu,Space,Tag,Typography } from 'antd'
import { useMemo,useState } from 'react'
import { Outlet,useLocation,useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import UserAvatar from '../features/profile/UserAvatar'
const {Header,Sider,Content}=Layout
const roleLabels:Record<string,string>={system_admin:'Quản trị hệ thống',training_manager:'Quản lý đào tạo',teacher:'Giảng viên',teaching_assistant:'Trợ giảng',accountant:'Kế toán',academic_affairs:'Giáo vụ',admissions:'Tuyển sinh',student_services:'Công tác sinh viên',student:'Học viên'}
export default function AppLayout(){
 const {user,logout,hasPermission}=useAuth();const navigate=useNavigate();const location=useLocation();const screens=Grid.useBreakpoint();const mobile=!screens.md;const [drawerOpen,setDrawerOpen]=useState(false)
 const items=useMemo(()=>[
  hasPermission('dashboard.view')?{key:'/dashboard',icon:<DashboardOutlined/>,label:'Tổng quan'}:null,
  {key:'/profile',icon:<UserOutlined/>,label:'Hồ sơ cá nhân'},
  hasPermission('users.view')?{key:'/admin/users',icon:<TeamOutlined/>,label:'Người dùng'}:null,
  hasPermission('users.import')?{key:'/admin/import-users',icon:<UploadOutlined/>,label:'Nhập Excel'}:null,
  hasPermission('roles.view')?{key:'/admin/roles',icon:<SafetyCertificateOutlined/>,label:'Vai trò & quyền'}:null,
  hasPermission('training.view')?{key:'/training',icon:<BookOutlined/>,label:'Danh mục đào tạo'}:null,
  hasPermission('leads.view')?{key:'/admissions/leads',icon:<PhoneOutlined/>,label:'Quản lý lead'}:null,
  hasPermission('leads.view')?{key:'/admissions/lead-assignment',icon:<PhoneOutlined/>,label:'Phân công & lọc lead'}:null,
  hasPermission('leads.view')?{key:'/admissions/funnel',icon:<PhoneOutlined/>,label:'S3 · Phễu lead'}:null,
  hasPermission('leads.view')?{key:'/admissions/care',icon:<PhoneOutlined/>,label:'S3 · Chăm sóc lead'}:null,
  hasPermission('leads.view')?{key:'/admissions/convert',icon:<PhoneOutlined/>,label:'S3 · Lead → Học viên'}:null,
  hasPermission('training.view')?{key:'/training/students',icon:<TeamOutlined/>,label:'S3 · Hồ sơ học viên'}:null,
  hasPermission('training.view')?{key:'/training/classes',icon:<BookOutlined/>,label:'S3 · Mở lớp'}:null,
  hasPermission('training.view')?{key:'/training/enrollments',icon:<TeamOutlined/>,label:'S3 · Ghi danh'}:null,
  hasPermission('training.view')?{key:'/training/class-overview',icon:<BookOutlined/>,label:'S3 · Danh sách lớp'}:null,
  hasPermission('training.view')?{key:'/training/class-staff',icon:<TeamOutlined/>,label:'S3 · Phân công GV/TG'}:null,
  hasPermission('training.view')?{key:'/training/rooms',icon:<BookOutlined/>,label:'S3 · Phòng học'}:null,
  hasPermission('training.view')?{key:'/training/timetable-generate',icon:<BookOutlined/>,label:'S4 · Sinh thời khóa biểu'}:null,
  hasPermission('training.view')?{key:'/training/holidays',icon:<BookOutlined/>,label:'S4 · Ngày nghỉ lễ'}:null,
  hasPermission('training.view')?{key:'/training/schedule-conflicts',icon:<BookOutlined/>,label:'S4 · Xung đột lịch'}:null,
  hasPermission('training.view')?{key:'/training/schedule-changes',icon:<BookOutlined/>,label:'S4 · Sửa buổi học'}:null,
  hasPermission('training.view')?{key:'/training/calendar',icon:<BookOutlined/>,label:'S4 · Lịch đào tạo'}:null,
  hasPermission('training.view')?{key:'/my-schedule',icon:<BookOutlined/>,label:'S4 · Lịch học của tôi'}:null,
  hasPermission('training.view')?{key:'/training/student-status',icon:<TeamOutlined/>,label:'S4 · Trạng thái học viên'}:null,
  hasPermission('attendance.view')?{key:'/training/attendance',icon:<TeamOutlined/>,label:'S4 · Điểm danh'}:null,
  hasPermission('training.view')?{key:'/absence-requests',icon:<BookOutlined/>,label:'S4 · Xin phép vắng'}:null,
  {key:'/change-password',icon:<KeyOutlined/>,label:'Đổi mật khẩu'}
 ].filter(Boolean) as {key:string;icon:React.ReactNode;label:string}[],[hasPermission])
 const menu=<Menu mode="inline" selectedKeys={[location.pathname]} items={items} onClick={({key})=>{navigate(key);setDrawerOpen(false)}}/>
 const handleLogout=async()=>{await logout();navigate('/login',{replace:true,state:{notice:'Bạn đã đăng xuất an toàn.'}})}
 return <Layout className="app-shell">{!mobile&&<Sider width={260} theme="light" className="app-sider"><div className="brand-block"><div className="brand-mark">CG</div><div><strong>CodeGym</strong><small>Hệ thống đào tạo</small></div></div>{menu}</Sider>}<Drawer title="Điều hướng" placement="left" width={320} open={drawerOpen} onClose={()=>setDrawerOpen(false)}>{menu}</Drawer><Layout><Header className="app-header"><Space>{mobile&&<Button type="text" icon={<MenuOutlined/>} onClick={()=>setDrawerOpen(true)}/>}<Typography.Text strong>Hệ thống quản lý đào tạo</Typography.Text></Space><Space wrap><UserAvatar/><div className="header-user"><strong>{user?.full_name||user?.email}</strong><Space size={4} wrap>{user?.roles.map(role=><Tag key={role}>{roleLabels[role]||role}</Tag>)}</Space></div><Button icon={<LogoutOutlined/>} onClick={handleLogout}>Đăng xuất</Button></Space></Header><Content className="app-content"><Outlet/></Content></Layout></Layout>
}
