"use client"

import React, { useState } from 'react'

type RefineChatProps = {
  onRefine: (message: string) => void
}

const REFINEMENT_OPTIONS = [
  { label: 'Cheaper', message: 'Show me cheaper options' },
  { label: 'More transit', message: 'Show me homes closer to transit' },
  { label: 'Quieter', message: 'Show me quieter neighborhoods' },
  { label: 'More expensive', message: 'Show me more expensive listings' },
  { label: 'Bigger', message: 'Show me larger homes' },
]

export default function RefineChat({ onRefine }: RefineChatProps) {
  const [message, setMessage] = useState('')

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!message.trim()) return
    onRefine(message.trim())
    setMessage('')
  }

  return (
    <section style={{ marginTop: 24, padding: 16, border: '1px solid #ddd', borderRadius: 8, background: '#f9f9fc' }}>
      <h3>Refine your search</h3>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 12 }}>
        {REFINEMENT_OPTIONS.map((option) => (
          <button
            key={option.label}
            type="button"
            onClick={() => onRefine(option.message)}
            style={{ padding: '8px 12px', borderRadius: 999, border: '1px solid #ccc', background: '#fff', cursor: 'pointer' }}
          >
            {option.label}
          </button>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <label htmlFor="refine-message">Add a custom refinement</label>
        <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
          <input
            id="refine-message"
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="e.g. more sunlight, quieter street"
            style={{ flex: 1, padding: 10, borderRadius: 6, border: '1px solid #ccc' }}
          />
          <button type="submit" style={{ padding: '10px 16px', borderRadius: 6, border: 'none', background: '#111', color: '#fff' }}>
            Apply
          </button>
        </div>
      </form>
    </section>
  )
}
