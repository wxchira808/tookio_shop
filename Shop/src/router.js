import { userResource, userRoles } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"

const routes = [
	{
		path: "/",
		name: "Dashboard",
		component: () => import("@/pages/Dashboard.vue"),
		meta: { requiresAuth: true },
	},
	{
		path: "/shops",
		name: "Shops",
		component: () => import("@/pages/Shops.vue"),
		meta: { requiresAuth: true },
	},
	{
		path: "/products",
		name: "Products",
		component: () => import("@/pages/Products.vue"),
		meta: { requiresAuth: true },
	},
	{
		path: "/purchases",
		name: "Purchases",
		component: () => import("@/pages/Purchases.vue"),
		meta: { requiresAuth: true },
	},
	{
		path: "/invoices",
		name: "Invoices",
		component: () => import("@/pages/Invoices.vue"),
		meta: { requiresAuth: true },
	},
	{
		path: "/subscriptions",
		name: "Subscriptions",
		component: () => import("@/pages/Subscriptions.vue"),
		meta: { requiresAuth: true },
	},
	{
		path: "/settings",
		name: "Settings",
		component: () => import("@/pages/Settings.vue"),
		meta: { requiresAuth: true },
	},
	{
		name: "Login",
		path: "/login",
		component: () => import("@/pages/Login.vue"),
	},
	{
		name: "Signup",
		path: "/signup",
		component: () => import("@/pages/Signup.vue"),
	},
	{
		name: "SetPassword",
		path: "/set-password",
		component: () => import("@/pages/SetPassword.vue"),
	},
	// Catch-all route
	{
		path: "/:pathMatch(.*)*",
		redirect: "/",
	},
]

const router = createRouter({
	history: createWebHistory("/shop"),
	routes,
})

router.beforeEach(async (to, from, next) => {
	const isLoggedIn = session.isLoggedIn

	// Only log during development
	if (import.meta.env.DEV) {
		console.log(
			`[Router] ${to.name} (from: ${from.name || "initial"}), auth: ${isLoggedIn}`,
		)
	}

	// Redirect logic
	if ((to.name === "Login" || to.name === "Signup" || to.name === "SetPassword") && isLoggedIn) {
		// If user is logged in, check their role
		try {
			const roles = await userRoles()
			// If System Manager, redirect to desk
			if (roles.includes("System Manager")) {
				window.location.href = "/app"
				return
			}
			// Otherwise go to dashboard
			next({ name: "Dashboard" })
		} catch {
			next({ name: "Dashboard" })
		}
	} else if (to.meta.requiresAuth && !isLoggedIn) {
		next({ name: "Login" })
	} else {
		next()
	}
})

export default router
