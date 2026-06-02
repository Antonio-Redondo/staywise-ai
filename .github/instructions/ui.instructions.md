---
applyTo: "src/app/**,src/components/**"
---

# UI and frontend patterns

Load this whenever editing anything under `src/app/` or `src/components/`.

## Framework conventions

- Next.js 15 App Router. Pages are React Server Components by default.
- Mark client components with `'use client'` on the first line. Use sparingly.
- Server Actions for non-streaming mutations. Route Handlers under `src/app/api/` for streaming endpoints.
- Tailwind CSS v4 utility classes inline. No CSS modules. No styled-components. Single `globals.css` for tokens and resets.

## Component library

- shadcn/ui as the base. Components live in `src/components/ui/` and are owned by this repo.
- AI Elements for AI-specific patterns (Message, Reasoning, Tool, etc).
- Lucide for icons. Sonner for toasts. next-themes for theming.
- Compose, do not abstract early. A second usage justifies extraction; a first does not.

## Streaming the graph

The `/api/recommend` route streams LangGraph state updates as SSE. The client reads them with the Vercel AI SDK's `useObject` hook.

Pattern:

```tsx
'use client'
import { experimental_useObject as useObject } from '@ai-sdk/react'
import { GraphStateSchema } from '@/types/graph'

export function RecommendForm() {
  const { object, submit, isLoading } = useObject({
    api: '/api/recommend',
    schema: GraphStateSchema,
  })
  // render progressively as object fields fill in
}
```

Rules:

- Never block the UI on the full pipeline. Render each piece as its node completes.
- Show optimistic placeholders for the next stage while the current one runs.
- Persist the `threadId` in the URL so refresh and share-links keep working.

## Refine surface

The refine-my-search chat uses `assistant-ui` with its LangGraph adapter, pointed at the same compiled graph using the existing `threadId`. Refinements reuse the prior checkpoint, so the user does not re-state the original intent.

## Map and listings

- Map: Mapbox GL JS in a client component. Token from `NEXT_PUBLIC_MAPBOX_TOKEN`. Use a single named style URL, not inline style definitions.
- Listing cards: one component, `ListingCard`. Variants via props, not separate files.
- Photo galleries: `next/image` with explicit sizes. Lazy-load below the fold.
- Stagger card entry with Motion's stagger preset, max 200ms total delay across the visible set.

## Forms

- React Hook Form with Zod resolver.
- Share schemas with the backend by importing from `src/types/`. Never duplicate a shape between client and server.
- Inline error messages under fields, never in toasts.
- Disable the submit button while pending and show a spinner inside it.

## Accessibility

- All interactive elements reachable by keyboard.
- Focus visible on every focusable element. Do not remove the ring without a replacement.
- Color contrast meets WCAG AA. Test score-badge colors with a deuteranopia simulator.
- Maps and visualizations always have a text alternative.
- Form errors announced via `aria-live="polite"`.

## Performance budgets

- Largest Contentful Paint under 2.5s on mid-tier mobile, 4G.
- First listing card visible within 3s of submit.
- Recommend-page JS under 200KB gzipped.
- Defer Mapbox until the first listing renders. The map is below the fold on mobile.

## Affiliate links

- Build affiliate URLs server-side in the explanation node, never client-side. Partner codes do not leak to the browser.
- Wrap every outbound affiliate link in a tracker that POSTs `{ listingId, source, timestamp }` to `/api/track-click` before navigation completes.
- Show an FTC-compliant disclosure above the fold on every page that displays affiliate links.

## Testing

- Component tests with Vitest plus React Testing Library.
- E2E with Playwright covering the full submit-to-render flow with upstream mocked.
- Visual regression optional. If added, use Playwright snapshots, not a third-party service.
