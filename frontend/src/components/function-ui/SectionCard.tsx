import type { ReactNode } from 'react'

type SectionCardProps = {
  title: string
  subtitle?: string
  extra?: ReactNode
  children: ReactNode
  className?: string
}

export default function SectionCard({ title, subtitle, extra, children, className = '' }: SectionCardProps) {
  return <section className={`feature-section-card ${className}`.trim()}>
    <div className="feature-section-head">
      <div>
        <h2>{title}</h2>
        {subtitle && <p>{subtitle}</p>}
      </div>
      {extra && <div className="feature-section-extra">{extra}</div>}
    </div>
    <div className="feature-section-body">{children}</div>
  </section>
}
