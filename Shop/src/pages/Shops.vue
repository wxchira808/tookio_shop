<template>
	<div class="min-h-screen bg-slate-50">
		<!-- Mobile Header -->
		<header class="lg:hidden bg-white border-b border-slate-200 px-4 py-3 sticky top-0 z-40">
			<div class="flex items-center justify-between">
				<button @click="sidebarOpen = true" class="p-2 -ml-2 rounded-lg hover:bg-slate-100">
					<svg class="w-6 h-6 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				</button>
				<h1 class="text-lg font-semibold text-slate-900">Shops</h1>
				<UserMenu />
			</div>
		</header>

		<div class="flex">
			<Sidebar v-model:open="sidebarOpen" />

			<main class="flex-1 lg:ml-64 p-4 lg:p-8">
				<!-- Header -->
				<div class="flex items-center justify-between mb-8">
					<div>
						<h1 class="text-2xl lg:text-3xl font-bold text-slate-900">Shops</h1>
						<p class="text-slate-500 mt-1">Manage your shops and locations</p>
					</div>
					<button
						@click="showCreateDialog = true"
						class="px-4 py-2 rounded-xl bg-tookio-500 text-white font-medium hover:bg-tookio-600 transition-colors flex items-center gap-2"
					>
						<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
						</svg>
						Add Shop
					</button>
				</div>

				<!-- Loading State -->
				<div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					<div v-for="i in 3" :key="i" class="bg-white rounded-2xl border border-slate-200 p-6">
						<div class="h-6 w-32 bg-slate-200 rounded animate-pulse mb-2"></div>
						<div class="h-4 w-48 bg-slate-100 rounded animate-pulse"></div>
					</div>
				</div>

				<!-- Empty State -->
				<div v-else-if="shops.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
					<div class="w-20 h-20 mx-auto mb-6 rounded-full bg-slate-100 flex items-center justify-center">
						<svg class="w-10 h-10 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
						</svg>
					</div>
					<h3 class="text-xl font-semibold text-slate-900 mb-2">No shops yet</h3>
					<p class="text-slate-500 mb-6">Create your first shop to start managing your inventory</p>
					<button
						@click="showCreateDialog = true"
						class="px-6 py-3 rounded-xl bg-tookio-500 text-white font-medium hover:bg-tookio-600 transition-colors"
					>
						Create your first shop
					</button>
				</div>

				<!-- Shops Grid -->
				<div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					<div
						v-for="shop in shops"
						:key="shop.name"
						class="bg-white rounded-2xl border border-slate-200 p-6 hover:shadow-lg transition-shadow"
					>
						<div class="flex items-start justify-between mb-4">
							<div class="w-12 h-12 rounded-xl bg-tookio-100 flex items-center justify-center">
								<svg class="w-6 h-6 text-tookio-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
								</svg>
							</div>
							<span
								class="px-2 py-1 text-xs rounded-full"
								:class="shop.disabled ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'"
							>
								{{ shop.disabled ? 'Inactive' : 'Active' }}
							</span>
						</div>
						<h3 class="text-lg font-semibold text-slate-900 mb-1">{{ shop.shop_name }}</h3>
						<p class="text-sm text-slate-500">{{ shop.location || 'No location set' }}</p>
					</div>
				</div>
			</main>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { createResource } from "frappe-ui"
import Sidebar from "@/components/layout/Sidebar.vue"
import UserMenu from "@/components/common/UserMenu.vue"

const sidebarOpen = ref(false)
const showCreateDialog = ref(false)
const shops = ref([])
const loading = ref(true)

const shopsResource = createResource({
	url: "frappe.client.get_list",
	makeParams() {
		return {
			doctype: "Shop",
			fields: ["name", "shop_name", "location", "disabled"],
			order_by: "creation desc",
		}
	},
	auto: true,
	onSuccess(data) {
		shops.value = data
		loading.value = false
	},
	onError() {
		loading.value = false
	},
})
</script>
