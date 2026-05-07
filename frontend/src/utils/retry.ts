interface RetryOptions {
  maxRetries?: number
  retryDelay?: number
  retryCondition?: (error: unknown) => boolean
  onRetry?: (error: unknown, attempt: number) => void
}

const DEFAULT_RETRY_OPTIONS: Required<RetryOptions> = {
  maxRetries: 3,
  retryDelay: 1000,
  retryCondition: (error: unknown) => {
    if (!error) return false
    const err = error as Record<string, unknown>
    const resp = err.response as Record<string, unknown> | undefined
    const status = (err.status as number) || (resp?.status as number)
    return status === 429 || status === 503 || status === 504 || status === 408 || status === 0
  },
  onRetry: () => {}
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const opts = { ...DEFAULT_RETRY_OPTIONS, ...options }
  let lastError: unknown

  for (let attempt = 1; attempt <= opts.maxRetries + 1; attempt++) {
    try {
      return await fn()
    } catch (error: unknown) {
      lastError = error

      if (attempt > opts.maxRetries) {
        break
      }

      if (opts.retryCondition(error)) {
        opts.onRetry(error, attempt)

        const delay = opts.retryDelay * Math.pow(2, attempt - 1)

        const err = error as Record<string, unknown>
        const resp = err.response as Record<string, unknown> | undefined
        const retryAfter = (err.headers as Record<string, string>)?.['retry-after'] || (resp?.headers as Record<string, string>)?.['retry-after']
        const actualDelay = retryAfter ? parseInt(retryAfter) * 1000 : delay

        await new Promise(resolve => setTimeout(resolve, actualDelay))
        continue
      }

      throw error
    }
  }

  throw lastError
}

export class RetryableFetch {
  constructor(private options: RetryOptions = {}) {}

  async post(url: string, data: unknown, headers: Record<string, string> = {}): Promise<Response> {
    return withRetry(
      () => fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(data)
      }),
      this.options
    )
  }
}
