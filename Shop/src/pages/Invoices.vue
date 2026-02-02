<template>
	<div class="min-h-screen bg-slate-50">
		<header class="lg:hidden bg-white border-b border-slate-200 px-4 py-3 sticky top-0 z-40">
			<div class="flex items-center justify-between">
				<button @click="sidebarOpen = true" class="p-2 -ml-2 rounded-lg hover:bg-slate-100">
					<svg class="w-6 h-6 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				</button>
				<h1 class="text-lg font-semibold text-slate-900">Invoices</h1>
				<UserMenu />
			</div>
		</header>

		<div class="flex">
			<Sidebar v-model:open="sidebarOpen" />

			<main class="flex-1 lg:ml-64 p-4 lg:p-8">
				<div class="flex items-center justify-between mb-8">
					<div>
						<h1 class="text-2xl lg:text-3xl font-bold text-slate-900">Sales Invoices</h1>
						<p class="text-slate-500 mt-1">Manage your sales and invoices</p>
					</div>
					<button class="px-4 py-2 rounded-xl bg-tookio-500 text-white font-medium hover:bg-tookio-600 transition-colors flex items-center gap-2">
						<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
						</svg>
						New Invoice
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
				<div v-else-if="invoices.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
					<div class="w-20 h-20 mx-auto mb-6 rounded-full bg-slate-100 flex items-center justify-center">
						<svg class="w-10 h-10 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						</svg>
					</div>
					<h3 class="text-xl font-semibold text-slate-900 mb-2">No invoices yet</h3>
					<p class="text-slate-500 mb-6">Create your first invoice to start tracking sales</p>
					<button class="px-6 py-3 rounded-xl bg-tookio-500 text-white font-medium hover:bg-tookio-600 transition-colors">
						Create first invoice
					</button>
				</div>

				<!-- Invoices List -->
				<div v-else class="bg-white rounded-2xl border border-slate-200 overflow-hidden">
					<div class="overflow-x-auto">
						<table class="w-full">
							<thead class="bg-slate-50 border-b border-slate-200">
								<tr>
									<th class="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Invoice #</th>
									<th class="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Date</th>
									<th class="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Customer</th>
									<th class="text-right px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Amount</th>
									<th class="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-slate-200">
								<tr v-for="invoice in invoices" :key="invoice.name" class="hover:bg-slate-50">
									<td class="px-6 py-4 text-sm font-medium text-slate-900">{{ invoice.name }}</td>
									<td class="px-6 py-4 text-sm text-slate-500">{{ formatDate(invoice.creation) }}</td>
									<td class="px-6 py-4 text-sm text-slate-900">{{ invoice.customer_name || 'Walk-in' }}</td>
									<td class="px-6 py-4 text-sm text-slate-900 text-right font-medium">{{ formatCurrency(invoice.grand_total) }}</td>
									<td class="px-6 py-4">
										<span
											class="px-2 py-1 text-xs rounded-full"
											:class="getStatusClass(invoice.status)"
										>
											{{ invoice.status || 'Draft' }}
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
const invoices = ref([])
const loading = ref(true)

const invoicesResource = createResource({
	url: "frappe.client.get_list",
	makeParams() {
		return {
			doctype: "Sale Invoice",
			fields: ["name", "creation", "customer_name", "grand_total", "status"],
			order_by: "creation desc",
		}
	},
	auto: true,
	onSuccess(data) {
		invoices.value = data
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
