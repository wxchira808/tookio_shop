import router from "@/router"
import { createResource } from "frappe-ui"
import { computed, reactive } from "vue"

const getCookie = (key) => {
	const cookies = new Map(
		document.cookie.split("; ").filter(Boolean).map((c) => c.split("=").map(decodeURIComponent))
	)
	return cookies.get(key) || null
}

export const userData = reactive({
	userId: null,
	fullName: null,
	userImage: null,
	roles: [],

	refresh() {
		const userId = getCookie("user_id")
		const fullName = getCookie("full_name")
		const userImage = getCookie("user_image")

		// Only update if we have valid data (not Guest)
		if (userId && userId !== "Guest") {
			this.userId = userId
			this.fullName = fullName
			this.userImage = userImage
		}
	},

	getDisplayName() {
		return this.fullName || window.frappe?.session?.user_fullname || window.frappe?.session?.user || "User"
	},

	getImageUrl() {
		return this.userImage || window.frappe?.session?.user_image || null
	},

	getInitials() {
		const parts = this.getDisplayName().split(" ").filter(Boolean)
		return parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : this.getDisplayName().substring(0, 2).toUpperCase()
	},
})

// Initial refresh
userData.refresh()

// Watch for cookie changes (e.g., after login) and auto-refresh
if (typeof window !== 'undefined') {
	let lastCookie = document.cookie
	setInterval(() => {
		if (document.cookie !== lastCookie) {
			lastCookie = document.cookie
			userData.refresh()
		}
	}, 500)
}

export const useUserData = () => ({
	userName: computed(() => userData.getDisplayName()),
	userImage: computed(() => userData.getImageUrl()),
	userInitials: computed(() => userData.getInitials()),
	userId: computed(() => userData.userId),
	refresh: () => userData.refresh(),
})

export const userResource = createResource({
	url: "frappe.auth.get_logged_user",
	cache: "User",
	onError(error) {
		if (error?.exc_type === "AuthenticationError") {
			router.push({ name: "Login" })
		}
	},
})

// Resource to get user roles
const userRolesResource = createResource({
	url: "frappe.client.get_list",
	makeParams() {
		return {
			doctype: "Has Role",
			filters: { parent: userData.userId },
			fields: ["role"],
			limit_page_length: 0,
		}
	},
})

// Function to get user roles
export async function userRoles() {
	if (userData.roles.length > 0) {
		return userData.roles
	}
	
	try {
		// First check if roles are in boot data
		if (window.frappe?.boot?.user?.roles) {
			userData.roles = window.frappe.boot.user.roles
			return userData.roles
		}

		// Otherwise fetch from API
		await userRolesResource.fetch()
		if (userRolesResource.data) {
			userData.roles = userRolesResource.data.map(r => r.role)
		}
		return userData.roles
	} catch (error) {
		console.error("Failed to fetch user roles:", error)
		return []
	}
}
