import { z } from "zod"

export const RecommendRequest = z.object({
  userQuery: z.string(),
  threadId: z.string().optional(),
})

export const ListingCard = z.object({
  id: z.string(),
  source_url: z.string().url(),
  address: z.string(),
  price: z.number().nullable(),
  bedrooms: z.number().nullable(),
  bathrooms: z.number().nullable(),
  square_feet: z.number().nullable(),
  photo_url: z.string().url().nullable(),
  source: z.string(),
  listed_date: z.string().nullable(),
  amenities: z.array(z.string()),
})

export const RecommendResponse = z.object({
  intent: z.any().nullable(),
  neighborhood_scores: z.array(z.object({ name: z.string(), score: z.number() })).nullable(),
  listings: z.array(ListingCard).nullable(),
  scored: z.any().nullable(),
  explained: z.any().nullable(),
})
