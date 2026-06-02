export async function initObservability() {
  if (typeof window === 'undefined') return

  const sentryDsn = process.env.NEXT_PUBLIC_SENTRY_DSN
  const posthogKey = process.env.NEXT_PUBLIC_POSTHOG_KEY
  const posthogHost = process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com'

  if (sentryDsn) {
    try {
      const Sentry = await import('@sentry/browser')
      Sentry.init({ dsn: sentryDsn, environment: process.env.NODE_ENV })
    } catch (e) {
      // Fail gracefully if package not installed or init fails
      // eslint-disable-next-line no-console
      console.warn('Sentry init failed', e)
    }
  }

  if (posthogKey) {
    try {
      const posthog = await import('posthog-js')
      posthog.init(posthogKey, { api_host: posthogHost })
      // expose for manual use in tests or other modules
      ;(window as any).posthog = posthog
    } catch (e) {
      // eslint-disable-next-line no-console
      console.warn('PostHog init failed', e)
    }
  }
}

export function trackRecommendSubmitted(payload?: Record<string, any>) {
  if (typeof window === 'undefined') return
  const ph = (window as any).posthog
  if (ph && typeof ph.capture === 'function') ph.capture('recommend_submitted', payload || {})
}
