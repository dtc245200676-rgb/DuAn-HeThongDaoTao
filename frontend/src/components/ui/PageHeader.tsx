import type { ReactNode } from 'react'
import { Typography } from 'antd'

interface PageHeaderProps {
  title: string
  description?: string
  eyebrow?: string
  actions?: ReactNode
}

export default function PageHeader({ title, description, eyebrow, actions }: PageHeaderProps) {
  return <div className="ui-page-header">
    <div className="ui-page-heading">
      {eyebrow && <span className="ui-eyebrow">{eyebrow}</span>}
      <Typography.Title level={2}>{title}</Typography.Title>
      {description && <Typography.Paragraph type="secondary">{description}</Typography.Paragraph>}
    </div>
    {actions && <div className="ui-page-actions">{actions}</div>}
  </div>
}
