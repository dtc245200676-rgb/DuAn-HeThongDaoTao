import type { ReactNode } from 'react'
import { Typography } from 'antd'

export default function FormSection({ title, description, children }: { title: string; description?: string; children: ReactNode }) {
  return <section className="ui-form-section">
    <div className="ui-form-section-head">
      <Typography.Title level={5}>{title}</Typography.Title>
      {description && <Typography.Text type="secondary">{description}</Typography.Text>}
    </div>
    <div>{children}</div>
  </section>
}
