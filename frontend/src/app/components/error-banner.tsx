"use client"

import React from 'react'

type Props = {
  message: string
  onRetry?: () => void
}

export default function ErrorBanner({ message, onRetry }: Props) {
  return (
    <div className="banner banner--error" role="alert">
      <span className="banner__icon">⚠️</span>
      <span className="banner__text">{message}</span>
      {onRetry && (
        <button className="btn btn--ghost" onClick={onRetry} aria-label="retry-button">
          Retry
        </button>
      )}
    </div>
  )
}
