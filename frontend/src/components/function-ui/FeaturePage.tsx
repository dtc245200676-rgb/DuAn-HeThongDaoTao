import type { ReactNode } from 'react'
import { Typography } from 'antd'
import { useAuth } from '../../auth/AuthContext'

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

export type FeatureTone = 'blue' | 'violet' | 'cyan' | 'green' | 'amber'

type FeaturePageProps = {
  eyebrow: string
  title: string
  description: string
  icon?: ReactNode
  tone?: FeatureTone
  actions?: ReactNode
  children: ReactNode
  className?: string
}

export default function FeaturePage({
  eyebrow,
  title,
  description,
  icon,
  tone = 'blue',
  actions,
  children,
  className = '',
}: FeaturePageProps) {
  const { user } = useAuth()
  const role = user?.roles?.[0]
  const roleLabel = role ? roleLabels[role] || role : 'Người dùng'

  return <main className={`feature-page feature-tone-${tone} ${className}`.trim()}>
    <section className="feature-hero">
      <div className="feature-hero-main">
        {icon && <div className="feature-hero-icon" aria-hidden="true">{icon}</div>}
        <div className="feature-hero-copy">
          <span className="feature-eyebrow">{eyebrow}</span>
          <Typography.Title level={1}>{title}</Typography.Title>
          <Typography.Paragraph>{description}</Typography.Paragraph>
        </div>
      </div>
      <div className="feature-hero-side">
        {actions && <div className="feature-hero-actions">{actions}</div>}
        <div className="feature-role-card">
          <span>Đang truy cập với vai trò</span>
          <strong>{roleLabel}</strong>
        </div>
      </div>
    </section>
    <div className="feature-page-body">{children}</div>
  </main>
}
