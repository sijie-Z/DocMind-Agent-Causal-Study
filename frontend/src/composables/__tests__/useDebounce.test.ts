import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, nextTick } from 'vue'
import { useDebounce, useThrottle, useDebounceFn, useThrottleFn } from '../useDebounce'

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('returns initial value immediately', () => {
    const source = ref('hello')
    const debounced = useDebounce(source, 300)
    expect(debounced.value).toBe('hello')
  })

  it('delays value update', async () => {
    const source = ref('a')
    const debounced = useDebounce(source, 300)

    source.value = 'b'
    await nextTick()
    expect(debounced.value).toBe('a')

    vi.advanceTimersByTime(300)
    await nextTick()
    expect(debounced.value).toBe('b')
  })

  it('resets timer on rapid changes', async () => {
    const source = ref(0)
    const debounced = useDebounce(source, 200)

    source.value = 1
    await nextTick()
    vi.advanceTimersByTime(100)

    source.value = 2
    await nextTick()
    vi.advanceTimersByTime(100)
    expect(debounced.value).toBe(0)

    vi.advanceTimersByTime(100)
    await nextTick()
    expect(debounced.value).toBe(2)
  })
})

describe('useThrottle', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('updates value immediately on first change', async () => {
    const source = ref('a')
    const throttled = useThrottle(source, 300)

    source.value = 'b'
    await nextTick()
    expect(throttled.value).toBe('b')
  })

  it('ignores changes within throttle window', async () => {
    const source = ref('a')
    const throttled = useThrottle(source, 300)

    source.value = 'b'
    await nextTick()
    expect(throttled.value).toBe('b')

    source.value = 'c'
    await nextTick()
    expect(throttled.value).toBe('b')
  })

  it('allows update after throttle window', async () => {
    const source = ref('a')
    const throttled = useThrottle(source, 300)

    source.value = 'b'
    await nextTick()

    vi.advanceTimersByTime(300)
    source.value = 'c'
    await nextTick()
    expect(throttled.value).toBe('c')
  })
})

describe('useDebounceFn', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('delays function execution', () => {
    const fn = vi.fn()
    const debounced = useDebounceFn(fn, 200)

    debounced()
    expect(fn).not.toHaveBeenCalled()

    vi.advanceTimersByTime(200)
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('passes arguments to the function', () => {
    const fn = vi.fn()
    const debounced = useDebounceFn(fn, 100)

    debounced('a', 'b')
    vi.advanceTimersByTime(100)
    expect(fn).toHaveBeenCalledWith('a', 'b')
  })

  it('cancels previous call on rapid invocations', () => {
    const fn = vi.fn()
    const debounced = useDebounceFn(fn, 200)

    debounced('first')
    vi.advanceTimersByTime(100)
    debounced('second')
    vi.advanceTimersByTime(200)

    expect(fn).toHaveBeenCalledTimes(1)
    expect(fn).toHaveBeenCalledWith('second')
  })
})

describe('useThrottleFn', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('executes function immediately on first call', () => {
    const fn = vi.fn()
    const throttled = useThrottleFn(fn, 300)

    throttled()
    expect(fn).toHaveBeenCalledTimes(1)
  })

  it('ignores calls within throttle window', () => {
    const fn = vi.fn()
    const throttled = useThrottleFn(fn, 300)

    throttled('a')
    throttled('b')
    expect(fn).toHaveBeenCalledTimes(1)
    expect(fn).toHaveBeenCalledWith('a')
  })

  it('allows execution after throttle window', () => {
    const fn = vi.fn()
    const throttled = useThrottleFn(fn, 300)

    throttled('a')
    vi.advanceTimersByTime(300)
    throttled('b')

    expect(fn).toHaveBeenCalledTimes(2)
    expect(fn).toHaveBeenLastCalledWith('b')
  })
})
