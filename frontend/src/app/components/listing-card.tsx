"use client"

import React from 'react'
import { getAffiliateNetwork, getAffiliateUrl } from '@/lib/affiliate'

// Curated example photos (real homes/interiors) used to illustrate every match.
const EXAMPLE_PHOTOS = [
  'https://images.unsplash.com/photo-1568605114967-8130f3a36994',
  'https://images.unsplash.com/photo-1570129477492-45c003edd2be',
  'https://images.unsplash.com/photo-1512917774080-9991f1c4c750',
  'https://images.unsplash.com/photo-1493809842364-78817add7ffb',
  'https://images.unsplash.com/photo-1484154218962-a197022b5858',
  'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267',
  'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2',
  'https://images.unsplash.com/photo-1554995207-c18c203602cb',
  'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688',
  'https://images.unsplash.com/photo-1560185007-cde436f6a4d0',
  'https://images.unsplash.com/photo-1576941089067-2de3c901e126',
  'https://images.unsplash.com/photo-1505691938895-1758d7feb511',
].map((u) => `${u}?auto=format&fit=crop&w=900&q=70`)

// Inline SVG fallback so a card never shows a broken image.
const FALLBACK =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="900" height="563"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#6366f1"/><stop offset="1" stop-color="#ec4899"/></linearGradient></defs><rect width="900" height="563" fill="url(#g)"/><text x="50%" y="52%" font-family="sans-serif" font-size="64" fill="rgba(255,255,255,0.85)" text-anchor="middle">🏠</text></svg>`
  )

function hash(str: string): number {
  let h = 0
  for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0
  return h
}

function pickPhoto(listing: any): string {
  const url: string | undefined = listing.photo_url
  if (url && !url.includes('example.com')) return url
  const idx = hash(String(listing.id || listing.address || '')) % EXAMPLE_PHOTOS.length
  return EXAMPLE_PHOTOS[idx]
}

export default function ListingCard({ listing, score, explanation }: any) {
  const handleImageError = (e: any) => {
    e.currentTarget.src = FALLBACK
  }

  const affiliateNetwork = getAffiliateNetwork(listing.source_url, listing.source)
  const affiliateUrl = getAffiliateUrl(listing.source_url, affiliateNetwork)

  const pct = typeof score === 'number' ? Math.round(score <= 1 ? score * 100 : score) : null
  const scoreClass = pct == null ? '' : pct >= 70 ? 'listing__score--good' : pct >= 40 ? 'listing__score--mid' : ''
  const amenities: string[] = Array.isArray(listing.amenities) ? listing.amenities : []

  async function handleClick() {
    try {
      await fetch('/api/track-click', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          listingId: listing.id,
          source: listing.source,
          sourceUrl: listing.source_url,
          affiliateNetwork,
        }),
      })
    } catch (e) {
      // ignore tracking failures
    }
  }

  return (
    <article className="listing">
      <div className="listing__media">
        <img src={pickPhoto(listing)} alt={listing.address} loading="lazy" onError={handleImageError} />
        {listing.price && (
          <div className="listing__price">
            ${listing.price.toLocaleString()} <small>/mo</small>
          </div>
        )}
        {pct != null && <div className={`listing__score ${scoreClass}`}>{pct}% match</div>}
      </div>

      <div className="listing__body">
        <h3 className="listing__title">{listing.address}</h3>

        <div className="listing__meta">
          {listing.bedrooms != null && <span>🛏 {listing.bedrooms} bd</span>}
          {listing.bathrooms != null && <span>🛁 {listing.bathrooms} ba</span>}
          {listing.square_feet != null && <span>📐 {listing.square_feet.toLocaleString()} sqft</span>}
        </div>

        {amenities.length > 0 && (
          <div className="chips">
            {amenities.slice(0, 4).map((a) => (
              <span key={a} className="chip chip--muted">
                {a.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        )}

        {explanation && <p className="listing__explanation">{explanation}</p>}

        <a
          className="listing__cta"
          href={affiliateUrl}
          onClick={handleClick}
          target="_blank"
          rel="noreferrer noopener"
        >
          View listing →
        </a>
      </div>
    </article>
  )
}
