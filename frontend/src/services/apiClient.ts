/**
 * Centralized API client for CRIMESHIELD Flask + SQLite backend.
 */

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000').replace(/\/+$/, '');

export interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined | null>;
  timeoutMs?: number;
}

export class ApiClientError extends Error {
  status: number;
  details?: string;

  constructor(message: string, status: number, details?: string) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.details = details;
  }
}

export async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, timeoutMs = 10000, ...customConfig } = options;

  let url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  if (params) {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== '') {
        query.append(key, String(value));
      }
    }
    const queryString = query.toString();
    if (queryString) {
      url += (url.includes('?') ? '&' : '?') + queryString;
    }
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  const headers = new Headers(customConfig.headers || {});
  if (!headers.has('Content-Type') && !(customConfig.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  headers.set('Accept', 'application/json');

  try {
    const response = await fetch(url, {
      ...customConfig,
      headers,
      signal: controller.signal,
    });

    clearTimeout(timer);

    const contentType = response.headers.get('content-type') || '';
    const isJson = contentType.includes('application/json');

    if (!response.ok) {
      let errorMessage = `Request failed with status ${response.status}`;
      let details: string | undefined;

      if (isJson) {
        try {
          const errorData = await response.json();
          errorMessage = errorData.error || errorData.message || errorMessage;
          details = errorData.details;
        } catch {
          // ignore parsing error
        }
      } else {
        const text = await response.text();
        if (text) errorMessage = text;
      }

      throw new ApiClientError(errorMessage, response.status, details);
    }

    if (response.status === 204) {
      return {} as T;
    }

    if (isJson) {
      return (await response.json()) as T;
    }

    return (await response.text()) as unknown as T;
  } catch (err: unknown) {
    clearTimeout(timer);
    if (err instanceof ApiClientError) {
      throw err;
    }
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new ApiClientError('Request timed out after 10 seconds. Is the Flask backend running?', 408);
    }
    const message = err instanceof Error ? err.message : 'Unknown network error';
    throw new ApiClientError(`Cannot connect to CRIMESHIELD backend: ${message}`, 0);
  }
}

export async function downloadFile(endpoint: string, filename: string): Promise<void> {
  const url = `${API_BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  const response = await fetch(url);
  if (!response.ok) {
    let errText = `Download failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      errText = errJson.error || errJson.details || errText;
    } catch {
      // not json
    }
    throw new ApiClientError(errText, response.status);
  }

  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);
}

export { API_BASE_URL };
