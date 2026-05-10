import { describe, it, expect } from 'vitest'
import { useRequestErrorHandler } from '@/composables/useErrorHandler'

describe('useRequestErrorHandler', () => {
  const { handleError } = useRequestErrorHandler()

  it('returns needAuth true for 401', () => {
    const result = handleError({ status: 401 })
    expect(result.needAuth).toBe(true)
    expect(result.message).toBe('请重新登录')
  })

  it('returns needAuth false for 403', () => {
    const result = handleError({ status: 403 })
    expect(result.needAuth).toBe(false)
    expect(result.message).toBe('没有权限')
  })

  it('returns needAuth false for 404', () => {
    const result = handleError({ status: 404 })
    expect(result.needAuth).toBe(false)
    expect(result.message).toBe('请求的资源不存在')
  })

  it('returns server error message for 500+', () => {
    const result = handleError({ status: 500 })
    expect(result.needAuth).toBe(false)
    expect(result.message).toBe('服务器错误，请稍后重试')
  })

  it('returns server error message for 502', () => {
    const result = handleError({ status: 502 })
    expect(result.message).toBe('服务器错误，请稍后重试')
  })

  it('uses error.message for unknown status', () => {
    const result = handleError({ status: 418, message: 'I am a teapot' })
    expect(result.needAuth).toBe(false)
    expect(result.message).toBe('I am a teapot')
  })

  it('uses error.msg as fallback', () => {
    const result = handleError({ msg: 'custom error' })
    expect(result.message).toBe('custom error')
  })

  it('falls back to default message when no message provided', () => {
    const result = handleError({})
    expect(result.message).toBe('网络请求失败')
  })

  it('handles null/undefined input gracefully', () => {
    const result1 = handleError(null)
    expect(result1.message).toBe('网络请求失败')

    const result2 = handleError(undefined)
    expect(result2.message).toBe('网络请求失败')
  })
})
