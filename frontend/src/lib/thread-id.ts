export function createThreadId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `thread-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

export function ensureThreadId(): string {
  if (typeof window === 'undefined') {
    return ''
  }
  const url = new URL(window.location.href)
  const existing = url.searchParams.get('threadId')
  if (existing) {
    return existing
  }
  const threadId = createThreadId()
  url.searchParams.set('threadId', threadId)
  try {
    window.history.replaceState({}, '', url.toString())
  } catch {
    window.location.href = url.toString()
  }
  return threadId
}
