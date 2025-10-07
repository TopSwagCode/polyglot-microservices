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
		update(s => ({ ...s, loading: true, error: null }));
		// Attempt real backend first
		try {
			const res = await fetch(`${apiBase}/auth/login`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password })
			});
			if (!res.ok) throw new Error(`Login failed (${res.status})`);
			const data = await res.json();
			// Expect shape: { token: string, user: { id, username, email? } }
			persistSession(data.token, data.user ?? { id: data.userId || 'me', username });
			return true;
		} catch (err: any) {
			// Fallback mock mode (no backend yet)
			console.info('Falling back to mock auth login');
			const mockUser: AuthUser = { id: crypto.randomUUID(), username };
			persistSession('mock-token', mockUser);
			return true;
		} finally {
			update(s => ({ ...s, loading: false }));
		}
	}

	async function loadUser() {
		// If already present, skip
		let current: AuthState | undefined;
		subscribe(v => (current = v))();
		if (!current?.token || current.user) return;
		update(s => ({ ...s, loading: true }));
		try {
			const res = await fetch(`${apiBase}/auth/me`, { headers: { Authorization: `Bearer ${current!.token}` } });
			if (!res.ok) throw new Error('Failed to load user');
			const user = await res.json();
			update(s => ({ ...s, user, error: null }));
			if (browser) localStorage.setItem(STORAGE_USER_KEY, JSON.stringify(user));
		} catch (err: any) {
			update(s => ({ ...s, error: err.message || 'Failed to load user' }));
		} finally {
			update(s => ({ ...s, loading: false }));
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
