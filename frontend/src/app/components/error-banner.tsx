"use client"

import React from 'react'

type Props = {
  message: string
  onRetry?: () => void
}

export default function ErrorBanner({ message, onRetry }: Props) {
  return (
    <div style={{ border: '1px solid #fcc', background: '#fff5f5', padding: 12, marginTop: 12 }} role="alert">
      <div style={{ color: '#900', marginBottom: 8 }}>{message}</div>
      {onRetry && (
        <button onClick={onRetry} aria-label="retry-button">
          Retry
        </button>
      )}
    </div>
  )
}
