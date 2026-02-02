/**
 * CSRF Token Management Utilities
 * Handles CSRF token retrieval, refresh, and request wrapping
 */

import { frappeRequest } from "frappe-ui"

// Event listeners for CSRF token refresh
const csrfRefreshListeners = []

/**
 * Get CSRF token from cookie
 */
export function getCSRFTokenFromCookie() {
	const match = document.cookie.match(/csrf_token=([^;]+)/)
	return match ? decodeURIComponent(match[1]) : null
}

/**
 * Ensure CSRF token is available
 */
export async function ensureCSRFToken(options = {}) {
	const { forceRefresh = false, silent = false } = options

	// Check existing token
	const existingToken = getCSRFTokenFromCookie() || window.csrf_token
	if (existingToken && !forceRefresh) {
		window.csrf_token = existingToken
		return existingToken
	}

	// Fetch new token
	try {
		const response = await frappeRequest({
			url: "/api/method/frappe.auth.get_logged_user",
			method: "GET",
		})

		// Token should now be in cookies
		const newToken = getCSRFTokenFromCookie()
		if (newToken) {
			window.csrf_token = newToken
			// Notify listeners
			csrfRefreshListeners.forEach((cb) => cb(newToken))
			return newToken
		}

		throw new Error("CSRF token not found after refresh")
	} catch (error) {
		if (!silent) {
			console.error("Failed to refresh CSRF token:", error)
		}
		throw error
	}
}

/**
 * Register a callback for CSRF token refresh events
 */
export function onCSRFTokenRefresh(callback) {
	csrfRefreshListeners.push(callback)
	return () => {
		const index = csrfRefreshListeners.indexOf(callback)
		if (index > -1) {
			csrfRefreshListeners.splice(index, 1)
		}
	}
}

/**
 * Create a CSRF-aware request wrapper
 * Automatically retries on 401/403 with refreshed token
 */
export function createCSRFAwareRequest(baseFetcher) {
	return async (options) => {
		try {
			return await baseFetcher(options)
		} catch (error) {
			// Check if it's a CSRF or auth error
			if (error?.httpStatus === 401 || error?.httpStatus === 403) {
				try {
					// Try to refresh CSRF token
					await ensureCSRFToken({ forceRefresh: true, silent: true })
					// Retry the request
					return await baseFetcher(options)
				} catch (retryError) {
					throw retryError
				}
			}
			throw error
		}
	}
}
