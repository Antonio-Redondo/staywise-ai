// frontend/src/lib/observability.ts

/**
 * Observability stub.
 *
 * Sentry + PostHog will be wired in once we add the dependencies. For now,
 * these are no-ops so the rest of the app can call them safely.
 */

export function initObservability(): void {
  // no-op
}

export function captureEvent(name: string, properties?: Record<string, unknown>): void {
  // no-op
  if (process.env.NODE_ENV === 'development') {
    // eslint-disable-next-line no-console
    console.debug('[observability] captureEvent', name, properties)
  }
}

export function captureError(error: unknown, context?: Record<string, unknown>): void {
  // no-op
  if (process.env.NODE_ENV === 'development') {
    // eslint-disable-next-line no-console
    console.error('[observability] captureError', error, context)
  }
}