import { Button, Layout, Space, Typography } from 'antd'
import { Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
const {Header,Content}=Layout
export default function AppLayout(){const {user,logout}=useAuth(); const nav=useNavigate(); return <Layout className="app-shell"><Header className="app-header"><Typography.Text strong>Hệ thống quản lý đào tạo</Typography.Text><Space><span>{user?.full_name||user?.email}</span><Button onClick={async()=>{await logout();nav('/login')}}>Đăng xuất</Button></Space></Header><Content className="app-content"><Outlet/></Content></Layout>}
