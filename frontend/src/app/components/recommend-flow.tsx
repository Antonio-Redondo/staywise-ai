"use client"

import React, { ChangeEvent, FormEvent, useEffect, useState } from 'react'
import IntentCard from './intent-card'
import ListingsGrid from './listings-grid'
import NeighborhoodMap from './neighborhood-map'
import RefineChat from './refine-chat'
import ErrorBanner from './error-banner'
import { ensureThreadId } from '@/lib/thread-id'
import { recommend } from '@/lib/api-client'

const EXAMPLES = [
  '2 bed, walkable, near BART, under $4000',
  'Quiet 1 bedroom with in-unit laundry and parking',
  'Family home close to good schools and parks',
]

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
      <form className="search" onSubmit={handleSubmit}>
        <label className="search__label" htmlFor="query">
          Describe what you want
        </label>
        <textarea
          id="query"
          value={query}
          placeholder="e.g. Sunny 2-bedroom, walkable to cafés, near BART, under $4,000/mo"
          onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setQuery(e.target.value)}
          rows={3}
        />
        <div className="chips" style={{ marginTop: 12 }}>
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              type="button"
              className="chip chip--muted"
              style={{ cursor: 'pointer' }}
              onClick={() => setQuery(ex)}
            >
              {ex}
            </button>
          ))}
        </div>
        <div className="search__row">
          {threadId && <span className="session-pill">session · {threadId.slice(0, 8)}</span>}
          <button type="submit" className="btn btn--primary" disabled={loading || !query.trim()}>
            {loading ? 'Searching…' : 'Find recommendations →'}
          </button>
        </div>
      </form>

      <RefineChat onRefine={handleRefine} />

      {error && (
        <ErrorBanner
          message={error}
          onRetry={() => {
            if (query && query.trim()) submitQuery(query)
          }}
        />
      )}

      {loading && (
        <div className="section">
          <div className="listings-grid">
            {[0, 1, 2].map((i) => (
              <div className="skeleton-card" key={i}>
                <div className="skeleton skeleton--media" />
                <div className="skeleton skeleton--line" />
                <div className="skeleton skeleton--line short" />
                <div className="skeleton skeleton--line" style={{ marginBottom: 18 }} />
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && state && (
        <>
          {state.intent && (
            <div className="section">
              <div className="section__head">
                <h2>What we heard</h2>
              </div>
              <IntentCard intent={state.intent} />
            </div>
          )}

          <div className="section">
            <div className="section__head">
              <h2>Neighborhoods</h2>
            </div>
            <NeighborhoodMap neighborhoods={state.neighborhoods} />
          </div>

          <div className="section">
            <div className="section__head">
              <h2>Your matches</h2>
              <span className="section__count">
                {state.items?.length || 0} {state.items?.length === 1 ? 'home' : 'homes'}
              </span>
            </div>
            <ListingsGrid items={state.items} />
          </div>
        </>
      )}
    </section>
  )
}
