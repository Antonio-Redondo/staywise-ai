import { createThreadId, ensureThreadId } from '../../src/lib/thread-id'

describe('thread-id utilities', () => {
  test('createThreadId returns a non-empty string', () => {
    const id = createThreadId()
    expect(typeof id).toBe('string')
    expect(id.length).toBeGreaterThan(0)
  })

  test('ensureThreadId returns an existing threadId when present', () => {
    const originalLocation = window.location.href
    window.history.replaceState({}, '', '/?threadId=test-id')
    const id = ensureThreadId()
    expect(id).toBe('test-id')
    window.history.replaceState({}, '', originalLocation)
  })
})
