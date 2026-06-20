"use client"

import React, { useState } from 'react'

type RefineChatProps = {
  onRefine: (message: string) => void
}

const REFINEMENT_OPTIONS = [
  { label: '💸 Cheaper', message: 'Show me cheaper options' },
  { label: '🚆 More transit', message: 'Show me homes closer to transit' },
  { label: '🤫 Quieter', message: 'Show me quieter neighborhoods' },
  { label: '✨ More premium', message: 'Show me more expensive listings' },
  { label: '📐 Bigger', message: 'Show me larger homes' },
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
    <section className="refine">
      <h3>Refine your search</h3>
      <div className="chips">
        {REFINEMENT_OPTIONS.map((option) => (
          <button
            key={option.label}
            type="button"
            className="btn btn--ghost"
            onClick={() => onRefine(option.message)}
          >
            {option.label}
          </button>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <div className="refine__row">
          <input
            id="refine-message"
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="e.g. more sunlight, quieter street, pet friendly…"
            aria-label="Add a custom refinement"
          />
          <button type="submit" className="btn btn--primary">
            Apply
          </button>
        </div>
      </form>
    </section>
  )
}
