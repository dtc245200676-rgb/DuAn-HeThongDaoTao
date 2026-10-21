import type { ReactNode } from 'react'

type MetricItem = {
  label: string
  value: ReactNode
  hint?: string
}

type MetricStripProps = { items: MetricItem[] }

export default function MetricStrip({ items }: MetricStripProps) {
  return <div className="feature-metric-strip">
    {items.map(item => <div className="feature-metric-item" key={item.label}>
      <span>{item.label}</span>
      <strong>{item.value}</strong>
      {item.hint && <small>{item.hint}</small>}
    </div>)}
  </div>
}
