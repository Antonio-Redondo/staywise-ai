"use client"

import React from 'react'
import { getAffiliateNetwork, getAffiliateUrl } from '@/lib/affiliate'

export default function ListingCard({ listing, score, explanation }: any) {
  const placeholder = '/placeholder.png'
  const handleImageError = (e: any) => {
    e.currentTarget.src = placeholder
  }

  const affiliateNetwork = getAffiliateNetwork(listing.source_url, listing.source)
  const affiliateUrl = getAffiliateUrl(listing.source_url, affiliateNetwork)

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
    <div style={{ border: '1px solid #eee', padding: 12, borderRadius: 6 }}>
      <img
        src={listing.photo_url || placeholder}
        alt={listing.address}
        style={{ width: '100%', height: 180, objectFit: 'cover' }}
        onError={handleImageError}
      />
      <h3>{listing.address}</h3>
      <div>{listing.price ? `$${listing.price.toLocaleString()}` : 'Price hidden'}</div>
      <div>Score: {score}</div>
      <p>{explanation}</p>
      <a href={affiliateUrl} onClick={handleClick} target="_blank" rel="noreferrer noopener">
        View listing
      </a>
    </div>
  )
}
