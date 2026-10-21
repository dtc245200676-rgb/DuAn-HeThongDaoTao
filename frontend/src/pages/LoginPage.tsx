import { BookOutlined, LockOutlined, MailOutlined, SafetyCertificateOutlined, TeamOutlined } from '@ant-design/icons'
import { Alert, Button, Card, Form, Input, Typography, message } from 'antd'
import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { apiErrorMessage } from '../api/client'
import { useAuth } from '../auth/AuthContext'

export default function LoginPage() {
  const { login, user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const notice = (location.state as { notice?: string } | null)?.notice || sessionStorage.getItem('auth_notice')

  useEffect(() => {
    if (user) navigate(user.roles.includes('system_admin') ? '/admin/users' : '/dashboard', { replace: true })
  }, [user, navigate])

  useEffect(() => () => sessionStorage.removeItem('auth_notice'), [])

  const onFinish = async (values: { email: string; password: string }) => {
    setSubmitting(true)
    setError('')
    try {
      const cleanEmail = values.email.replace(/[\u200B-\u200D\uFEFF]/g, '').trim().toLowerCase()
      const result = await login(cleanEmail, values.password)
      message.success(result.message || 'Đăng nhập thành công')
      if (result.must_change_password) navigate('/change-password', { replace: true })
      else navigate(result.roles.includes('system_admin') ? '/admin/users' : '/dashboard', { replace: true })
    } catch (err) {
      setError(apiErrorMessage(err, 'Không thể đăng nhập.'))
    } finally {
      setSubmitting(false)
    }
  }

  return <div className="auth-page auth-login-page">
    <section className="auth-visual" aria-label="Giới thiệu hệ thống">
      <div className="auth-visual-top">
        <div className="auth-brand"><div className="brand-mark">CG</div><div className="auth-brand-copy"><strong>CodeGym Education</strong><span>Training Management Platform</span></div></div>
      </div>
      <div className="auth-visual-content">
        <h1>Quản lý đào tạo<br />trên một nền tảng.</h1>
        <p>Tổ chức tuyển sinh, học viên, lớp học, lịch đào tạo, chuyên cần và bài tập trong một trải nghiệm nhất quán, rõ ràng và an toàn.</p>
        <div className="auth-feature-list">
          <div className="auth-feature"><span className="auth-feature-icon"><TeamOutlined /></span>Quản lý người học & phân quyền</div>
          <div className="auth-feature"><span className="auth-feature-icon"><BookOutlined /></span>Chương trình, lớp học & lịch học</div>
          <div className="auth-feature"><span className="auth-feature-icon"><SafetyCertificateOutlined /></span>Bảo mật theo vai trò thực tế</div>
          <div className="auth-feature"><span className="auth-feature-icon"><BookOutlined /></span>Chuyên cần & bài tập tập trung</div>
        </div>
      </div>
      <div className="auth-visual-footer">Hệ thống quản lý đào tạo · Giao diện quản trị tập trung</div>
    </section>

    <section className="auth-form-side">
      <Card className="auth-card">
        <div className="auth-heading">
          <div className="auth-mobile-brand"><div className="brand-mark">CG</div><strong>CodeGym Education</strong></div>
          <Typography.Title level={2}>Chào mừng trở lại</Typography.Title>
          <Typography.Text type="secondary">Đăng nhập để tiếp tục vào hệ thống quản lý đào tạo.</Typography.Text>
        </div>
        {notice && <Alert type="info" showIcon message={notice} style={{ marginBottom: 18 }} />}
        {error && <Alert type="error" showIcon message={error} style={{ marginBottom: 18 }} />}
        <Form layout="vertical" onFinish={onFinish} size="large" requiredMark="optional">
          <Form.Item
            name="email"
            label="Email"
            normalize={(value) => value?.replace(/[\u200B-\u200D\uFEFF]/g, '').trim().toLowerCase()}
            rules={[{ required: true, message: 'Vui lòng nhập email' }, { type: 'email', message: 'Email không hợp lệ' }]}
          >
            <Input prefix={<MailOutlined />} placeholder="name@example.com" autoComplete="email" />
          </Form.Item>
          <Form.Item name="password" label="Mật khẩu" rules={[{ required: true, message: 'Vui lòng nhập mật khẩu' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="Nhập mật khẩu" autoComplete="current-password" />
          </Form.Item>
          <Button type="primary" htmlType="submit" loading={submitting} block>Đăng nhập</Button>
        </Form>
        <div className="auth-footer"><Link to="/forgot-password">Quên mật khẩu?</Link></div>
      </Card>
    </section>
  </div>
}
