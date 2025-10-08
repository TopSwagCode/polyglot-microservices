import { browser } from '$app/environment';
import { auth } from '$lib/stores/auth';

// Determine base URL for API Gateway.
// Use VITE_API_BASE if provided; fallback to common gateway port (8080) but warn in dev.
const rawBase: string = (import.meta as any).env?.VITE_API_BASE || 'http://localhost:8080';
const normalizedBase = rawBase.replace(/\/$/, '');
if (browser && (import.meta as any).env?.DEV && !((import.meta as any).env?.VITE_API_BASE)) {
	console.warn('[api] VITE_API_BASE not set; using fallback', normalizedBase);
}

export interface RequestOptions {
	method?: string;
	body?: any;
	auth?: boolean; // include Authorization header if token present
	headers?: Record<string, string>;
	query?: Record<string, string | number | boolean | undefined | null>;
}

export class ApiClient {
	constructor(public baseUrl: string = normalizedBase) {}

	private buildUrl(endpoint: string, query?: RequestOptions['query']) {
		let url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;
		if (query && Object.keys(query).length) {
			const params = new URLSearchParams();
			for (const [k, v] of Object.entries(query)) {
				if (v == null) continue;
				params.append(k, String(v));
			}
			url += (url.includes('?') ? '&' : '?') + params.toString();
		}
		return url;
	}

	private async request<T = any>(endpoint: string, options: RequestOptions = {}): Promise<T> {
		const { method = 'GET', body, auth: needsAuth, headers = {}, query } = options;
		const url = this.buildUrl(endpoint, query);

		const finalHeaders: Record<string, string> = {
			'Content-Type': 'application/json',
			...headers
		};

		if (needsAuth) {
			let token: string | null = null;
			// Pull from auth store (already hydrated) OR localStorage when in browser
			if (browser) {
				try { token = localStorage.getItem('auth_token'); } catch {}
			}
			if (!token) {
				// subscribe once to get state
				auth.subscribe(s => { token = s.token; })();
			}
			if (token) finalHeaders['Authorization'] = `Bearer ${token}`;
		}

		const fetchInit: RequestInit = {
			method,
			headers: finalHeaders
		};
		if (body !== undefined) fetchInit.body = typeof body === 'string' ? body : JSON.stringify(body);

		const res = await fetch(url, fetchInit);
		if (!res.ok) {
			// Attempt to parse error body
			let detail: any = null;
			try { detail = await res.json(); } catch {}
			const message = detail?.message || detail?.error || `${res.status} ${res.statusText}`;
			if (res.status === 401 && needsAuth) {
				// Auto logout on auth failure
				auth.logout();
			}
			throw new Error(message);
		}
		// Handle no-content
		if (res.status === 204) return undefined as T;
		const text = await res.text();
		if (!text) return undefined as T;
		try { return JSON.parse(text) as T; } catch { return text as any as T; }
	}

	get<T = any>(endpoint: string, options: Omit<RequestOptions, 'method' | 'body'> = {}) {
		return this.request<T>(endpoint, { ...options, method: 'GET' });
	}
	post<T = any>(endpoint: string, body?: any, options: Omit<RequestOptions, 'method' | 'body'> = {}) {
		return this.request<T>(endpoint, { ...options, method: 'POST', body });
	}
	put<T = any>(endpoint: string, body?: any, options: Omit<RequestOptions, 'method' | 'body'> = {}) {
		return this.request<T>(endpoint, { ...options, method: 'PUT', body });
	}
	patch<T = any>(endpoint: string, body?: any, options: Omit<RequestOptions, 'method' | 'body'> = {}) {
		return this.request<T>(endpoint, { ...options, method: 'PATCH', body });
	}
	delete<T = any>(endpoint: string, options: Omit<RequestOptions, 'method' | 'body'> = {}) {
		return this.request<T>(endpoint, { ...options, method: 'DELETE' });
	}
}

export const apiClient = new ApiClient();
