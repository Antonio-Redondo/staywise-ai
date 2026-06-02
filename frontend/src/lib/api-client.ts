import { z } from 'zod'
import { RecommendRequest, RecommendResponse } from '../types/api'

const API_ROOT = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function recommend(payload: z.infer<typeof RecommendRequest>) {
  const parsedPayload = RecommendRequest.parse(payload)
  const res = await fetch(`${API_ROOT}/api/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(parsedPayload),
  })
  if (!res.ok) throw new Error(await res.text())
  const data = await res.json()
  return RecommendResponse.parse(data)
}
