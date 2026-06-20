import React from 'react'

export default function NeighborhoodMap({ neighborhoods }: { neighborhoods?: any[] }) {
  if (!neighborhoods || neighborhoods.length === 0) {
    return <div className="empty">No neighborhoods scored yet.</div>
  }

  return (
    <ul className="hoods">
      {neighborhoods.map((n) => {
        const score = typeof n.score === 'number' ? n.score : 0
        const pct = Math.round(score <= 1 ? score * 100 : score)
        return (
          <li className="hood" key={n.name}>
            <div className="hood__top">
              <span className="hood__name">{n.name}</span>
              <span className="hood__score">{pct}</span>
            </div>
            <div className="hood__bar">
              <div className="hood__fill" style={{ width: `${Math.min(100, pct)}%` }} />
            </div>
            {n.walk_score != null && (
              <div style={{ marginTop: 8, fontSize: 12, color: 'var(--text-muted)', fontWeight: 600 }}>
                Walk score {n.walk_score}
              </div>
            )}
          </li>
        )
      })}
    </ul>
  )
}
