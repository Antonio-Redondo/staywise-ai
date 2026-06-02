import React from 'react'

export default function IntentCard({ intent }: any) {
  if (!intent) return null
  return (
    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
      {intent.lifestyle_tags && intent.lifestyle_tags.map((t: string) => (
        <span key={t} style={{ background: '#eef', padding: '4px 8px', borderRadius: 999 }}>{t}</span>
      ))}
      {intent.budget_min && <span style={{ padding: '4px 8px' }}>${intent.budget_min}</span>}
      {intent.budget_max && <span style={{ padding: '4px 8px' }}>${intent.budget_max}</span>}
    </div>
  )
}
