import { NextRequest, NextResponse } from 'next/server'
import { z } from 'zod'
import { getAffiliateNetwork, getAffiliateUrl } from '@/lib/affiliate'

const TrackClickRequest = z.object({
  listingId: z.string(),
  source: z.string(),
  sourceUrl: z.string().url(),
  affiliateNetwork: z.enum(['realtor', 'apartments']).optional(),
})

export async function POST(request: NextRequest) {
  const body = await request.json()
  const parsed = TrackClickRequest.parse(body)

  const backendUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/track-click`

  const response = await fetch(backendUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      listingId: parsed.listingId,
      source: parsed.source,
      affiliateNetwork: parsed.affiliateNetwork,
    }),
  })

  if (!response.ok) {
    const errorText = await response.text()
    return new NextResponse(errorText, { status: response.status })
  }

  const affiliateNetwork = parsed.affiliateNetwork ?? getAffiliateNetwork(parsed.sourceUrl, parsed.source)
  const affiliateUrl = getAffiliateUrl(parsed.sourceUrl, affiliateNetwork)

  if (affiliateNetwork && affiliateUrl !== parsed.sourceUrl) {
    try {
      await fetch(affiliateUrl, { method: 'GET' })
    } catch (error) {
      console.error('Affiliate pixel request failed', error)
    }
  }

  return NextResponse.json({ ok: true })
}
