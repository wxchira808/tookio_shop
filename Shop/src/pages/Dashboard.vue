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
				<h1 class="text-lg font-semibold text-slate-900">Dashboard</h1>
				<UserMenu />
			</div>
		</header>

		<div class="flex">
			<!-- Sidebar -->
			<Sidebar v-model:open="sidebarOpen" />

			<!-- Main Content -->
			<main class="flex-1 lg:ml-64 p-4 lg:p-8">
				<!-- Welcome Section -->
				<div class="mb-8">
					<h1 class="text-2xl lg:text-3xl font-bold text-slate-900">
						Welcome back, {{ userName }}!
					</h1>
					<p class="text-slate-500 mt-1">Here's what's happening with your shop today.</p>
				</div>

				<!-- Stats Grid -->
				<div class="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 mb-8">
					<StatCard
						title="Total Products"
						:value="stats.totalProducts"
						icon="package"
						color="tookio"
						:loading="statsLoading"
					/>
					<StatCard
						title="Total Sales"
						:value="formatCurrency(stats.totalSales)"
						icon="trending-up"
						color="green"
						:loading="statsLoading"
					/>
					<StatCard
						title="Pending Invoices"
						:value="stats.pendingInvoices"
						icon="file-text"
						color="amber"
						:loading="statsLoading"
					/>
					<StatCard
						title="Active Shops"
						:value="stats.activeShops"
						icon="store"
						color="blue"
						:loading="statsLoading"
					/>
				</div>

				<!-- Quick Actions -->
				<div class="bg-white rounded-2xl border border-slate-200 p-6 mb-8">
					<h2 class="text-lg font-semibold text-slate-900 mb-4">Quick Actions</h2>
					<div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
						<router-link
							to="/products"
							class="flex flex-col items-center gap-3 p-4 rounded-xl bg-tookio-50 hover:bg-tookio-100 transition-colors"
						>
							<div class="w-12 h-12 rounded-xl bg-tookio-500 flex items-center justify-center">
								<svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
								</svg>
							</div>
							<span class="text-sm font-medium text-slate-700">Add Product</span>
						</router-link>

						<router-link
							to="/invoices"
							class="flex flex-col items-center gap-3 p-4 rounded-xl bg-green-50 hover:bg-green-100 transition-colors"
						>
							<div class="w-12 h-12 rounded-xl bg-green-500 flex items-center justify-center">
								<svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
								</svg>
							</div>
							<span class="text-sm font-medium text-slate-700">New Sale</span>
						</router-link>

						<router-link
							to="/purchases"
							class="flex flex-col items-center gap-3 p-4 rounded-xl bg-blue-50 hover:bg-blue-100 transition-colors"
						>
							<div class="w-12 h-12 rounded-xl bg-blue-500 flex items-center justify-center">
								<svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
								</svg>
							</div>
							<span class="text-sm font-medium text-slate-700">Add Purchase</span>
						</router-link>

						<router-link
							to="/shops"
							class="flex flex-col items-center gap-3 p-4 rounded-xl bg-purple-50 hover:bg-purple-100 transition-colors"
						>
							<div class="w-12 h-12 rounded-xl bg-purple-500 flex items-center justify-center">
								<svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
								</svg>
							</div>
							<span class="text-sm font-medium text-slate-700">Manage Shops</span>
						</router-link>
					</div>
				</div>

				<!-- Recent Activity -->
				<div class="bg-white rounded-2xl border border-slate-200 p-6">
					<div class="flex items-center justify-between mb-4">
						<h2 class="text-lg font-semibold text-slate-900">Recent Sales</h2>
						<router-link to="/invoices" class="text-sm text-tookio-600 hover:text-tookio-500 font-medium">
							View all →
						</router-link>
					</div>

					<div v-if="recentSalesLoading" class="space-y-4">
						<div v-for="i in 3" :key="i" class="h-16 bg-slate-100 rounded-xl animate-pulse"></div>
					</div>

					<div v-else-if="recentSales.length === 0" class="text-center py-8">
						<div class="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-100 flex items-center justify-center">
							<svg class="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
						</div>
						<p class="text-slate-500">No sales yet. Create your first sale!</p>
					</div>

					<div v-else class="space-y-3">
						<div
							v-for="sale in recentSales"
							:key="sale.name"
							class="flex items-center justify-between p-4 rounded-xl bg-slate-50 hover:bg-slate-100 transition-colors"
						>
							<div>
								<p class="font-medium text-slate-900">{{ sale.name }}</p>
								<p class="text-sm text-slate-500">{{ formatDate(sale.creation) }}</p>
							</div>
							<div class="text-right">
								<p class="font-semibold text-slate-900">{{ formatCurrency(sale.grand_total) }}</p>
								<span
									class="text-xs px-2 py-0.5 rounded-full"
									:class="getStatusClass(sale.status)"
								>
									{{ sale.status }}
								</span>
							</div>
						</div>
					</div>
				</div>
			</main>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue"
import { createResource } from "frappe-ui"
import { useUserData } from "@/data/user"
import Sidebar from "@/components/layout/Sidebar.vue"
import UserMenu from "@/components/common/UserMenu.vue"
import StatCard from "@/components/dashboard/StatCard.vue"

const { userName } = useUserData()
const sidebarOpen = ref(false)

// Stats
const stats = ref({
	totalProducts: 0,
	totalSales: 0,
	pendingInvoices: 0,
	activeShops: 0,
})
const statsLoading = ref(true)

// Recent sales
const recentSales = ref([])
const recentSalesLoading = ref(true)

// Fetch stats
const statsResource = createResource({
	url: "tookio_shop.api.dashboard.get_stats",
	auto: true,
	onSuccess(data) {
		stats.value = data
		statsLoading.value = false
	},
	onError() {
		statsLoading.value = false
	},
})

// Fetch recent sales
const salesResource = createResource({
	url: "frappe.client.get_list",
	makeParams() {
		return {
			doctype: "Sale Invoice",
			fields: ["name", "creation", "grand_total", "status"],
			order_by: "creation desc",
			limit_page_length: 5,
		}
	},
	auto: true,
	onSuccess(data) {
		recentSales.value = data
		recentSalesLoading.value = false
	},
	onError() {
		recentSalesLoading.value = false
	},
})

function formatCurrency(amount) {
	return new Intl.NumberFormat("en-KE", {
		style: "currency",
		currency: "KES",
		minimumFractionDigits: 0,
	}).format(amount || 0)
}

function formatDate(date) {
	if (!date) return ""
	return new Date(date).toLocaleDateString("en-KE", {
		day: "numeric",
		month: "short",
		year: "numeric",
	})
}

function getStatusClass(status) {
	switch (status?.toLowerCase()) {
		case "paid":
			return "bg-green-100 text-green-700"
		case "pending":
			return "bg-amber-100 text-amber-700"
		case "cancelled":
			return "bg-red-100 text-red-700"
		default:
			return "bg-slate-100 text-slate-700"
	}
}
</script>
