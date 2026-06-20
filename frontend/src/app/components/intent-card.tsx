import React from 'react'

export default function IntentCard({ intent }: any) {
  if (!intent) return null

  const fmt = (n: number) => `$${n.toLocaleString()}`
  const beds =
    intent.bedrooms_min != null
      ? intent.bedrooms_min === intent.bedrooms_max
        ? `${intent.bedrooms_min} bd`
        : `${intent.bedrooms_min}–${intent.bedrooms_max ?? '+'} bd`
      : null

  return (
    <div className="chips">
      {(intent.lifestyle_tags || []).map((t: string) => (
        <span key={t} className="chip">
          ✦ {t.replace(/_/g, ' ')}
        </span>
      ))}
      {beds && <span className="chip chip--muted">{beds}</span>}
      {(intent.budget_min || intent.budget_max) && (
        <span className="chip chip--budget">
          {intent.budget_min ? fmt(intent.budget_min) : ''}
          {intent.budget_min && intent.budget_max ? ' – ' : ''}
          {intent.budget_max ? fmt(intent.budget_max) : ''}
        </span>
      )}
      {(intent.must_haves || []).map((m: string) => (
        <span key={m} className="chip chip--muted">
          {m.replace(/_/g, ' ')}
        </span>
      ))}
    </div>
  )
}
