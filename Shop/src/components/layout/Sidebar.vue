<template>
	<!-- Mobile Overlay -->
	<Teleport to="body">
		<Transition
			enter-active-class="transition-opacity duration-300"
			enter-from-class="opacity-0"
			enter-to-class="opacity-100"
			leave-active-class="transition-opacity duration-300"
			leave-from-class="opacity-100"
			leave-to-class="opacity-0"
		>
			<div
				v-if="open"
				class="lg:hidden fixed inset-0 bg-black/50 z-40"
				@click="$emit('update:open', false)"
			></div>
		</Transition>
	</Teleport>

	<!-- Sidebar -->
	<aside
		class="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-slate-200 transform transition-transform duration-300 lg:translate-x-0"
		:class="open ? 'translate-x-0' : '-translate-x-full'"
	>
		<!-- Logo -->
		<div class="flex items-center gap-3 px-6 py-5 border-b border-slate-200">
			<div class="w-10 h-10 rounded-xl bg-tookio-500 flex items-center justify-center">
				<svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
					<path stroke-linecap="round" stroke-linejoin="round" d="M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.016a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72L4.318 3.44A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.75c0 .415.336.75.75.75z" />
				</svg>
			</div>
			<div>
				<h1 class="font-bold text-slate-900">Tookio Shop</h1>
				<p class="text-xs text-slate-500">Inventory Management</p>
			</div>

			<!-- Close button on mobile -->
			<button
				@click="$emit('update:open', false)"
				class="lg:hidden ml-auto p-2 rounded-lg hover:bg-slate-100"
			>
				<svg class="w-5 h-5 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		</div>

		<!-- Navigation -->
		<nav class="p-4 space-y-1">
			<router-link
				v-for="item in navItems"
				:key="item.path"
				:to="item.path"
				class="nav-item"
				:class="{ active: isActive(item.path) }"
				@click="$emit('update:open', false)"
			>
				<component :is="item.icon" class="w-5 h-5" />
				{{ item.label }}
			</router-link>
		</nav>

		<!-- Subscription Info (Bottom) -->
		<div class="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-200">
			<router-link
				to="/subscriptions"
				class="block p-4 rounded-xl bg-gradient-to-r from-tookio-50 to-tookio-100 hover:from-tookio-100 hover:to-tookio-200 transition-colors"
			>
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-full bg-tookio-500 flex items-center justify-center">
						<svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
						</svg>
					</div>
					<div>
						<p class="text-sm font-medium text-tookio-900">Upgrade Plan</p>
						<p class="text-xs text-tookio-600">Get more features</p>
					</div>
				</div>
			</router-link>

			<!-- User Menu on Desktop -->
			<div class="hidden lg:block mt-4">
				<UserMenu />
			</div>
		</div>
	</aside>
</template>

<script setup>
import { computed, h, defineComponent } from "vue"
import { useRoute } from "vue-router"
import UserMenu from "@/components/common/UserMenu.vue"

defineProps({
	open: Boolean,
})

defineEmits(["update:open"])

const route = useRoute()

// Icons as components
const DashboardIcon = defineComponent({
	render() {
		return h("svg", { fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "2" }, [
			h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" })
		])
	}
})

const ShopsIcon = defineComponent({
	render() {
		return h("svg", { fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "2" }, [
			h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" })
		])
	}
})

const ProductsIcon = defineComponent({
	render() {
		return h("svg", { fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "2" }, [
			h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" })
		])
	}
})

const PurchasesIcon = defineComponent({
	render() {
		return h("svg", { fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "2" }, [
			h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" })
		])
	}
})

const InvoicesIcon = defineComponent({
	render() {
		return h("svg", { fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "2" }, [
			h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" })
		])
	}
})

const SubscriptionsIcon = defineComponent({
	render() {
		return h("svg", { fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "2" }, [
			h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" })
		])
	}
})

const SettingsIcon = defineComponent({
	render() {
		return h("svg", { fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "2" }, [
			h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" }),
			h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M15 12a3 3 0 11-6 0 3 3 0 016 0z" })
		])
	}
})

const navItems = [
	{ path: "/", label: "Dashboard", icon: DashboardIcon },
	{ path: "/shops", label: "Shops", icon: ShopsIcon },
	{ path: "/products", label: "Products", icon: ProductsIcon },
	{ path: "/purchases", label: "Purchases", icon: PurchasesIcon },
	{ path: "/invoices", label: "Invoices", icon: InvoicesIcon },
	{ path: "/subscriptions", label: "Subscription", icon: SubscriptionsIcon },
	{ path: "/settings", label: "Settings", icon: SettingsIcon },
]

function isActive(path) {
	if (path === "/") {
		return route.path === "/"
	}
	return route.path.startsWith(path)
}
</script>
