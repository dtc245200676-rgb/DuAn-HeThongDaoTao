import { Button, Result } from 'antd'
import { useNavigate } from 'react-router-dom'

export default function NotFoundPage() {
  const navigate = useNavigate()
  return <div className="page-center"><Result status="404" title="Không tìm thấy trang" subTitle="Đường dẫn bạn mở không tồn tại hoặc đã thay đổi." extra={<Button type="primary" onClick={() => navigate('/dashboard')}>Về trang tổng quan</Button>} /></div>
}
