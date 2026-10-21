import type { ReactNode } from 'react'
import { CheckCircleOutlined } from '@ant-design/icons'

type ActionBarProps = {
  selectedCount?: number
  title?: string
  description?: string
  children: ReactNode
}

export default function ActionBar({ selectedCount, title, description, children }: ActionBarProps) {
  const heading = title || (typeof selectedCount === 'number' ? `Đã chọn ${selectedCount} mục` : 'Thao tác nhanh')
  return <section className="feature-action-bar">
    <div className="feature-action-copy">
      <span className="feature-action-icon"><CheckCircleOutlined /></span>
      <div>
        <strong>{heading}</strong>
        {description && <span>{description}</span>}
      </div>
    </div>
    <div className="feature-action-controls">{children}</div>
  </section>
}
