import { Avatar } from 'antd'
import { useAuth } from '../../auth/AuthContext'
const API_BASE=import.meta.env.VITE_API_BASE_URL||'http://127.0.0.1:8000'
export default function UserAvatar(){const {user}=useAuth();return <Avatar src={user?.avatar_thumbnail_url?`${API_BASE}${user.avatar_thumbnail_url}`:undefined}>{(user?.full_name||user?.email||'U').charAt(0).toUpperCase()}</Avatar>}
