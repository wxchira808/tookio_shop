<template>
	<div class="min-h-screen bg-slate-50">
		<header class="lg:hidden bg-white border-b border-slate-200 px-4 py-3 sticky top-0 z-40">
			<div class="flex items-center justify-between">
				<button @click="sidebarOpen = true" class="p-2 -ml-2 rounded-lg hover:bg-slate-100">
					<svg class="w-6 h-6 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				</button>
				<h1 class="text-lg font-semibold text-slate-900">Purchases</h1>
				<UserMenu />
			</div>
		</header>

		<div class="flex">
			<Sidebar v-model:open="sidebarOpen" />

			<main class="flex-1 lg:ml-64 p-4 lg:p-8">
				<div class="flex items-center justify-between mb-8">
					<div>
						<h1 class="text-2xl lg:text-3xl font-bold text-slate-900">Purchases</h1>
						<p class="text-slate-500 mt-1">Track your stock purchases and supplier orders</p>
					</div>
					<button class="px-4 py-2 rounded-xl bg-tookio-500 text-white font-medium hover:bg-tookio-600 transition-colors flex items-center gap-2">
						<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
						</svg>
						Add Purchase
					</button>
				</div>

				<!-- Loading State -->
				<div v-if="loading" class="space-y-4">
					<div v-for="i in 3" :key="i" class="bg-white rounded-2xl border border-slate-200 p-6">
						<div class="h-6 w-32 bg-slate-200 rounded animate-pulse mb-2"></div>
						<div class="h-4 w-48 bg-slate-100 rounded animate-pulse"></div>
					</div>
				</div>

				<!-- Empty State -->
				<div v-else-if="purchases.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
					<div class="w-20 h-20 mx-auto mb-6 rounded-full bg-slate-100 flex items-center justify-center">
						<svg class="w-10 h-10 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
						</svg>
					</div>
					<h3 class="text-xl font-semibold text-slate-900 mb-2">No purchases yet</h3>
					<p class="text-slate-500 mb-6">Record your first purchase to track inventory</p>
					<button class="px-6 py-3 rounded-xl bg-tookio-500 text-white font-medium hover:bg-tookio-600 transition-colors">
						Record first purchase
					</button>
				</div>

				<!-- Purchases List -->
				<div v-else class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
					<div class="overflow-x-auto">
						<table class="w-full">
							<thead class="bg-slate-50 border-b border-slate-200">
								<tr>
									<th class="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">ID</th>
									<th class="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Date</th>
									<th class="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Supplier</th>
									<th class="text-right px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Amount</th>
									<th class="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-slate-200">
								<tr v-for="purchase in purchases" :key="purchase.name" class="hover:bg-slate-50">
									<td class="px-6 py-4 text-sm font-medium text-slate-900">{{ purchase.name }}</td>
									<td class="px-6 py-4 text-sm text-slate-500">{{ formatDate(purchase.creation) }}</td>
									<td class="px-6 py-4 text-sm text-slate-900">{{ purchase.supplier || '-' }}</td>
									<td class="px-6 py-4 text-sm text-slate-900 text-right font-medium">{{ formatCurrency(purchase.total_amount) }}</td>
									<td class="px-6 py-4">
										<span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-700">
											{{ purchase.status || 'Completed' }}
										</span>
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>
			</main>
		</div>
	</div>
</template>

<script setup>
import { ref } from "vue"
import { createResource } from "frappe-ui"
import Sidebar from "@/components/layout/Sidebar.vue"
import UserMenu from "@/components/common/UserMenu.vue"

const sidebarOpen = ref(false)
const purchases = ref([])
const loading = ref(true)

const purchasesResource = createResource({
	url: "frappe.client.get_list",
	makeParams() {
		return {
			doctype: "Purchase",
			fields: ["name", "creation", "supplier", "total_amount", "status"],
			order_by: "creation desc",
		}
	},
	auto: true,
	onSuccess(data) {
		purchases.value = data
		loading.value = false
	},
	onError() {
		loading.value = false
	},
})

function formatDate(date) {
	if (!date) return ""
	return new Date(date).toLocaleDateString("en-KE", {
		day: "numeric",
		month: "short",
		year: "numeric",
	})
}

function formatCurrency(amount) {
	return new Intl.NumberFormat("en-KE", {
		style: "currency",
		currency: "KES",
		minimumFractionDigits: 0,
	}).format(amount || 0)
}
</script>
