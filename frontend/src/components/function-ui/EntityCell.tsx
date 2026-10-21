import { Avatar } from 'antd'

type EntityCellProps = {
  title?: string | null
  subtitle?: string | null
}

function initials(value?: string | null) {
  const parts = (value || '?').trim().split(/\s+/).filter(Boolean)
  if (!parts.length) return '?'
  return parts.slice(-2).map(part => part[0]?.toUpperCase()).join('')
}

export default function EntityCell({ title, subtitle }: EntityCellProps) {
  return <div className="feature-entity-cell">
    <Avatar className="feature-entity-avatar">{initials(title)}</Avatar>
    <div className="feature-entity-copy">
      <strong>{title || 'Chưa cập nhật'}</strong>
      {subtitle && <span>{subtitle}</span>}
    </div>
  </div>
}
