import type { ReactNode } from 'react'
import { Card, Typography } from 'antd'

interface StatCardProps {
  icon: ReactNode
  label: string
  value: ReactNode
  hint?: string
  tone?: 'blue' | 'green' | 'amber' | 'violet'
}

export default function StatCard({ icon, label, value, hint, tone = 'blue' }: StatCardProps) {
  return <Card className={`ui-stat-card ui-stat-${tone}`} bordered={false}>
    <div className="ui-stat-icon">{icon}</div>
    <div className="ui-stat-copy">
      <Typography.Text type="secondary">{label}</Typography.Text>
      <strong className="ui-stat-value">{value}</strong>
      {hint && <span className="ui-stat-hint">{hint}</span>}
    </div>
  </Card>
}
