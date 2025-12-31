/**
 * Google Workspace APIs Error Handling - TypeScript Implementation.
 * From document lines: 3535-3665 (Section 7)
 *
 * Implements retry with exponential backoff and common error handling.
 */
import { GaxiosError } from 'gaxios';

export interface RetryableRequest<T> {
  (): Promise<T>;
}

/**
 * Execute API request with exponential backoff.
 *
 * @param request - Async function that makes the API request
 * @param maxRetries - Maximum number of retry attempts (default: 5)
 * @returns Promise resolving to the request result
 * @throws Error if all retries are exhausted or non-retryable error occurs
 */
export async function executeWithRetry<T>(
  request: RetryableRequest<T>,
  maxRetries: number = 5
): Promise<T> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await request();
    } catch (error) {
      if (error instanceof GaxiosError) {
        const status = error.response?.status;
        if (status && [429, 500, 502, 503, 504].includes(status)) {
          const waitTime = Math.pow(2, attempt) + Math.random();
          console.log(`Attempt ${attempt + 1} failed with ${status}. Retrying in ${waitTime.toFixed(2)} seconds...`);
          await new Promise(resolve => setTimeout(resolve, waitTime * 1000));
          continue;
        }
      }
      throw error;
    }
  }
  throw new Error(`Failed after ${maxRetries} retries`);
}

/**
 * Error codes and their meanings
 */
export const ERROR_CODES: Record<number, { description: string; solution: string }> = {
  400: {
    description: 'Bad Request',
    solution: 'Check request parameters',
  },
  401: {
    description: 'Unauthorized',
    solution: 'Token expired - re-authenticate',
  },
  403: {
    description: 'Forbidden',
    solution: 'Check scopes, API enabled, quota',
  },
  404: {
    description: 'Not Found',
    solution: 'Invalid file/folder ID',
  },
  429: {
    description: 'Rate Limit',
    solution: 'Implement exponential backoff',
  },
  500: {
    description: 'Server Error',
    solution: 'Retry with backoff',
  },
};

/**
 * Rate limits by API
 */
export const RATE_LIMITS = {
  drive: '12,000 requests/minute/project',
  docs: '300 requests/minute/project',
  sheets: '500 requests/100 seconds/project',
  slides: '500 requests/100 seconds/project',
};

/**
 * Parse and return useful error information from a Google API error.
 *
 * @param error - The caught error
 * @returns Object with error details
 */
export function parseGoogleApiError(error: unknown): {
  status: number | null;
  message: string;
  description: string;
  solution: string;
} {
  if (error instanceof GaxiosError) {
    const status = error.response?.status || null;
    const errorInfo = status ? ERROR_CODES[status] : null;

    return {
      status,
      message: error.message,
      description: errorInfo?.description || 'Unknown error',
      solution: errorInfo?.solution || 'Check error details',
    };
  }

  if (error instanceof Error) {
    return {
      status: null,
      message: error.message,
      description: 'Non-API error',
      solution: 'Check error message for details',
    };
  }

  return {
    status: null,
    message: String(error),
    description: 'Unknown error type',
    solution: 'Inspect the error object',
  };
}

/**
 * Check if an error is retryable (server error or rate limit).
 *
 * @param error - The caught error
 * @returns true if the error is retryable
 */
export function isRetryableError(error: unknown): boolean {
  if (error instanceof GaxiosError) {
    const status = error.response?.status;
    return status !== undefined && [429, 500, 502, 503, 504].includes(status);
  }
  return false;
}

/**
 * Delay execution with optional jitter.
 *
 * @param ms - Base milliseconds to wait
 * @param jitter - If true, adds random jitter (default: true)
 */
export async function delay(ms: number, jitter: boolean = true): Promise<void> {
  const actualDelay = jitter ? ms + Math.random() * ms * 0.1 : ms;
  await new Promise(resolve => setTimeout(resolve, actualDelay));
}

/**
 * Calculate exponential backoff delay.
 *
 * @param attempt - Current attempt number (0-based)
 * @param baseDelay - Base delay in ms (default: 1000)
 * @param maxDelay - Maximum delay in ms (default: 32000)
 * @returns Delay in milliseconds
 */
export function calculateBackoffDelay(
  attempt: number,
  baseDelay: number = 1000,
  maxDelay: number = 32000
): number {
  const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);
  return delay + Math.random() * delay * 0.1; // Add jitter
}
