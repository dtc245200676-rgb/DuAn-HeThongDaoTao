import { Card, Space } from 'antd'
import AvatarSection from '../features/profile/AvatarSection'
import ProfileInfoSection from '../features/profile/ProfileInfoSection'
export default function ProfilePage(){return <Card title="Hồ sơ cá nhân"><Space align="start" size="large" wrap style={{width:'100%'}}><AvatarSection/><div style={{minWidth:280,flex:'1 1 420px',maxWidth:620}}><ProfileInfoSection/></div></Space></Card>}
