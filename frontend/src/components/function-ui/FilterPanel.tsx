import type { ReactNode } from 'react'
import { FilterOutlined } from '@ant-design/icons'

type FilterPanelProps = {
  title?: string
  description?: string
  actions?: ReactNode
  children: ReactNode
}

export default function FilterPanel({ title = 'Bộ lọc', description, actions, children }: FilterPanelProps) {
  return <section className="feature-filter-panel">
    <div className="feature-panel-head">
      <div className="feature-panel-title-wrap">
        <span className="feature-panel-icon"><FilterOutlined /></span>
        <div>
          <strong>{title}</strong>
          {description && <span>{description}</span>}
        </div>
      </div>
      {actions && <div className="feature-panel-actions">{actions}</div>}
    </div>
    <div className="feature-filter-grid">{children}</div>
  </section>
}
