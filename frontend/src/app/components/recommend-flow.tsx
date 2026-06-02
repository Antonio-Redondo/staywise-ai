"use client"

import React, { ChangeEvent, FormEvent, useEffect, useState } from 'react'
import IntentCard from './intent-card'
import ListingsGrid from './listings-grid'
import NeighborhoodMap from './neighborhood-map'
import RefineChat from './refine-chat'
import ErrorBanner from './error-banner'
import { ensureThreadId } from '@/lib/thread-id'
import { recommend } from '@/lib/api-client'

export default function RecommendFlow() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [state, setState] = useState<any | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [threadId, setThreadId] = useState('')

  useEffect(() => {
    if (!threadId) {
      setThreadId(ensureThreadId())
    }
  }, [threadId])

  async function submitQuery(userQuery: string) {
    setLoading(true)
    setError(null)
    const currentThreadId = threadId || ensureThreadId()
    if (!threadId) {
      setThreadId(currentThreadId)
    }
    try {
      const data = await recommend({ userQuery, threadId: currentThreadId })
      let items: any[] = []
      if (data.scored && Array.isArray(data.scored) && data.scored.length > 0) {
        const explainedMap = (data.explained || []).reduce((acc: any, ex: any) => {
          if (ex.listing_id) acc[ex.listing_id] = ex.explanation
          return acc
        }, {})
        items = data.scored.map((s: any) => {
          const listing = s.listing || s['listing'] || {}
          return {
            ...listing,
            score: s.score,
            explanation: explainedMap[listing.id] || s.explanation || '',
          }
        })
      } else if (data.listings && Array.isArray(data.listings)) {
        items = data.listings
      }

      setState({ intent: data.intent, neighborhoods: data.neighborhood_scores, items })
    } catch (err: any) {
      setError(err.message || String(err))
    } finally {
      setLoading(false)
    }
  }

  function handleRefine(message: string) {
    const refinedQuery = query.trim() ? `${query.trim()} ${message}` : message
    setQuery(refinedQuery)
    submitQuery(refinedQuery)
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    await submitQuery(query)
  }

  return (
    <section>
      <form onSubmit={handleSubmit}>
        <label htmlFor="query">Describe what you want</label>
        <textarea
          id="query"
          value={query}
          onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setQuery(e.target.value)}
          rows={4}
          style={{ width: '100%' }}
        />
        <div style={{ marginTop: 8 }}>
          <button type="submit" disabled={loading || !query.trim()}>
            {loading ? 'Searching…' : 'Find recommendations'}
          </button>
        </div>
      </form>

      {threadId && <div style={{ marginTop: 8, color: '#666' }}>Session: {threadId}</div>}
      <RefineChat onRefine={handleRefine} />

      {error && (
        <ErrorBanner
          message={error}
          onRetry={() => {
            // retry last query if present
            if (query && query.trim()) submitQuery(query)
          }}
        />
      )}

      {state && (
        <div style={{ marginTop: 16 }}>
          <h2>Intent</h2>
          <IntentCard intent={state.intent} />

          <h2>Neighborhoods</h2>
          <NeighborhoodMap neighborhoods={state.neighborhoods} />

          <h2>Listings</h2>
          <ListingsGrid items={state.items} />
        </div>
      )}
    </section>
  )
}
