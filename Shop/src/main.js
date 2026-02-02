/**
 * Tookio Shop - Application Entry Point
 *
 * Initialization sequence:
 * 1. Configure Vue app with plugins and global components
 * 2. Authenticate user and initialize CSRF token (in parallel)
 * 3. Check user role for routing (System Manager -> desk, others -> Shop UI)
 * 4. Register router and mount app
 */

import { createPinia } from "pinia"
import { createApp } from "vue"

import App from "./App.vue"
import { session, sessionUser } from "./data/session"
import { userResource } from "./data/user"
import router from "./router"
import { ensureCSRFToken, getCSRFTokenFromCookie, createCSRFAwareRequest } from "./utils/csrf"

import {
	Alert,
	Badge,
	Button,
	Dialog,
	ErrorMessage,
	FormControl,
	Input,
	TextInput,
	frappeRequest,
	pageMetaPlugin,
	resourcesPlugin,
	setConfig,
} from "frappe-ui"

import "./index.css"

// =============================================================
// Global Components (available in all templates without import)
// =============================================================

const globalComponents = {
	Button,
	TextInput,
	Input,
	FormControl,
	ErrorMessage,
	Dialog,
	Alert,
	Badge,
}

// =============================================================
// Application Initialization
// =============================================================

async function initializeApp() {
	const app = createApp(App)
	const pinia = createPinia()

	// Enable automatic CSRF token refresh on 401/403 errors
	const csrfAwareFrappeRequest = createCSRFAwareRequest(frappeRequest)
	setConfig("resourceFetcher", csrfAwareFrappeRequest)

	// Register plugins
	app.use(pinia)
	app.use(resourcesPlugin)
	app.use(pageMetaPlugin)

	// Register global components
	for (const key in globalComponents) {
		app.component(key, globalComponents[key])
	}

	// Disable double-tap zoom on mobile for faster touch response
	app.directive("touch-action", {
		mounted: (el) => (el.style.touchAction = "manipulation"),
	})

	// -----------------------------------------------------
	// Authentication (CSRF + User fetched in parallel for faster startup)
	// -----------------------------------------------------

	const csrfPromise = (async () => {
		const existingToken = getCSRFTokenFromCookie()
		if (existingToken) {
			console.debug("CSRF token found in cookie")
			return true
		}

		console.debug("Fetching CSRF token...")
		try {
			await ensureCSRFToken({ silent: true })
			return true
		} catch {
			console.debug("CSRF fetch failed, will retry on first API call")
			return false
		}
	})()

	const userPromise = (async () => {
		try {
			if (!userResource.loading) userResource.fetch()
			await userResource.promise
			return sessionUser()
		} catch (error) {
			console.debug("User not logged in", error?.message || "No session")
			return null
		}
	})()

	const [, user] = await Promise.all([csrfPromise, userPromise])
	session.user = user
	console.info(`User authenticated: ${session.user}`)

	// -----------------------------------------------------
	// Mount Application
	// -----------------------------------------------------

	console.debug("Registering router, auth state:", session.isLoggedIn)
	app.use(router)
	app.mount("#app")

	// -----------------------------------------------------
	// Scheduled CSRF Token Refresh (every 30 minutes)
	// -----------------------------------------------------

	setInterval(
		async () => {
			console.debug("Scheduled CSRF token refresh")
			await ensureCSRFToken({ forceRefresh: true, silent: true })
		},
		30 * 60 * 1000,
	)
}

initializeApp()
