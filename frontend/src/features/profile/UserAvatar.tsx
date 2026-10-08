import { Avatar } from 'antd'
import { useAuth } from '../../auth/AuthContext'
export default function UserAvatar(){const {user}=useAuth();return <Avatar>{(user?.full_name||user?.email||'U').charAt(0).toUpperCase()}</Avatar>}
