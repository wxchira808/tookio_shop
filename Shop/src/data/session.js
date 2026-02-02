import router from "@/router"
import { createResource } from "frappe-ui"
import { computed, reactive } from "vue"

import { ensureCSRFToken } from "@/utils/csrf"
import { userResource, userData, userRoles } from "./user"

export function sessionUser() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	let _sessionUser = cookies.get("user_id")
	if (_sessionUser === "Guest") {
		_sessionUser = null
	}
	return _sessionUser
}

export const session = reactive({
	login: createResource({
		url: "login",
		makeParams({ email, password }) {
			return {
				usr: email,
				pwd: password,
			}
		},
		async onSuccess(data) {
			// Initialize CSRF token immediately after successful login
			await ensureCSRFToken()

			await userResource.reload()

			// Refresh userData from cookies after login
			userData.refresh()

			session.user = sessionUser()
			session.login.reset()

			// Check user role and redirect appropriately
			try {
				const roles = await userRoles()
				if (roles.includes("System Manager")) {
					// System Manager goes to desk
					window.location.href = "/app"
				} else {
					// All other users go to Shop Dashboard
					router.push({ name: "Dashboard" })
				}
			} catch {
				// Default to dashboard on error
				router.push({ name: "Dashboard" })
			}
		},
		onError(error) {
			console.error("Login error:", error)
		},
	}),
	logout: createResource({
		url: "logout",
		onSuccess() {
			userResource.reset()
			session.user = sessionUser()
			router.replace({ name: "Login" })
		},
		onError(error) {
			console.error("Logout error:", error)
			// Even if logout fails on server, clear local session
			userResource.reset()
			session.user = null
			router.replace({ name: "Login" })
		},
	}),
	user: sessionUser(),
	isLoggedIn: computed(() => !!session.user),
})
