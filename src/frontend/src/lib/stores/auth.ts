import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// ---- Types ----
export interface AuthUser {
	id: string;
	username: string;
	email?: string;
}

export interface AuthState {
	user: AuthUser | null;
	token: string | null;
	loading: boolean;
	error: string | null;
}

const STORAGE_TOKEN_KEY = 'auth_token';
const STORAGE_USER_KEY = 'auth_user';

const initialState: AuthState = {
	user: null,
	token: null,
	loading: false,
	error: null
};

function createAuthStore() {
	const { subscribe, update, set } = writable<AuthState>(initialState);
	const apiBase = (import.meta as any).env?.VITE_API_BASE || 'http://localhost:8080';

	// Restore persisted session (client only)
	if (browser) {
		try {
			const token = localStorage.getItem(STORAGE_TOKEN_KEY);
			const userRaw = localStorage.getItem(STORAGE_USER_KEY);
			if (token && userRaw) {
				const user: AuthUser = JSON.parse(userRaw);
				set({ user, token, loading: false, error: null });
			}
		} catch (err) {
			console.warn('Auth restore failed', err);
		}
	}

	async function login(username: string, password: string) {
		update((s: AuthState) => ({ ...s, loading: true, error: null }));
		try {
			const res = await fetch(`${apiBase}/auth/login`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password })
			});
			if (!res.ok) {
				if (res.status === 401 || res.status === 400) {
					// Invalid credentials – do not fallback, surface error
					const detail = await safeParseError(res);
					update((s: AuthState) => ({ ...s, error: detail || 'Invalid credentials' }));
					return false;
				}
				// Other server errors
				const detail = await safeParseError(res);
				throw new Error(detail || `Login failed (${res.status})`);
			}
			const data = await res.json();
			persistSession(data.token, data.user ?? { id: data.userId || 'me', username });
			return true;
		} catch (err: any) {
			const message = err?.message || 'Unable to login';
			update((s: AuthState) => ({ ...s, error: message }));
			return false;
		} finally {
			update((s: AuthState) => ({ ...s, loading: false }));
		}
	}

	async function safeParseError(res: Response): Promise<string | null> {
		try {
			const data = await res.json();
			if (typeof data === 'string') return data;
			if (data?.error) return data.error;
			if (data?.message) return data.message;
			return null;
		} catch {
			return null;
		}
	}

	async function loadUser() {
		// If already present, skip
		let current: AuthState | undefined;
		subscribe((v: AuthState) => (current = v))();
		if (!current?.token || current.user) return;
		update((s: AuthState) => ({ ...s, loading: true }));
		try {
			const res = await fetch(`${apiBase}/auth/me`, { headers: { Authorization: `Bearer ${current!.token}` } });
			if (!res.ok) throw new Error('Failed to load user');
			const user = await res.json();
			update((s: AuthState) => ({ ...s, user, error: null }));
			if (browser) localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(user));
		} catch (err: any) {
			update((s: AuthState) => ({ ...s, error: err.message || 'Failed to load user' }));
		} finally {
			update((s: AuthState) => ({ ...s, loading: false }));
		}
	}

	function logout() {
		if (browser) {
			localStorage.removeItem(STORAGE_TOKEN_KEY);
			localStorage.removeItem(STORAGE_USER_KEY);
		}
		set({ ...initialState });
	}

	function persistSession(token: string, user: AuthUser) {
		if (browser) {
			localStorage.setItem(STORAGE_TOKEN_KEY, token);
			localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(user));
		}
		set({ user, token, loading: false, error: null });
	}

	return {
		subscribe,
		login,
		logout,
		loadUser
	};
}

export const auth = createAuthStore();
