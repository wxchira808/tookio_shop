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
				<h1 class="text-lg font-semibold text-slate-900">Products</h1>
				<UserMenu />
			</div>
		</header>

		<div class="flex">
			<Sidebar v-model:open="sidebarOpen" />

			<main class="flex-1 lg:ml-64 p-4 lg:p-8">
				<!-- Header -->
				<div class="flex items-center justify-between mb-8">
					<div>
						<h1 class="text-2xl lg:text-3xl font-bold text-slate-900">Products</h1>
						<p class="text-slate-500 mt-1">Manage your product catalog and inventory</p>
					</div>
					<button
						@click="showCreateDialog = true"
						class="px-4 py-2 rounded-xl bg-tookio-500 text-white font-medium hover:bg-tookio-600 transition-colors flex items-center gap-2"
					>
						<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
						</svg>
						Add Product
					</button>
				</div>

				<!-- Search & Filters -->
				<div class="bg-white rounded-2xl border border-slate-200 p-4 mb-6">
					<div class="flex flex-col sm:flex-row gap-4">
						<div class="flex-1 relative">
							<svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
							</svg>
							<input
								v-model="searchQuery"
								type="text"
								placeholder="Search products..."
								class="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 focus:border-tookio-500 focus:ring-2 focus:ring-tookio-500/20 outline-none"
							/>
						</div>
					</div>
				</div>

				<!-- Loading State -->
				<div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
					<div v-for="i in 8" :key="i" class="bg-white rounded-2xl border border-slate-200 p-4">
						<div class="h-40 bg-slate-200 rounded-xl animate-pulse mb-4"></div>
						<div class="h-5 w-24 bg-slate-200 rounded animate-pulse mb-2"></div>
						<div class="h-4 w-16 bg-slate-100 rounded animate-pulse"></div>
					</div>
				</div>

				<!-- Empty State -->
				<div v-else-if="products.length === 0" class="bg-white rounded-2xl border border-slate-200 p-12 text-center">
					<div class="w-20 h-20 mx-auto mb-6 rounded-full bg-slate-100 flex items-center justify-center">
						<svg class="w-10 h-10 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
						</svg>
					</div>
					<h3 class="text-xl font-semibold text-slate-900 mb-2">No products yet</h3>
					<p class="text-slate-500 mb-6">Add your first product to start managing your inventory</p>
					<button
						@click="showCreateDialog = true"
						class="px-6 py-3 rounded-xl bg-tookio-500 text-white font-medium hover:bg-tookio-600 transition-colors"
					>
						Add your first product
					</button>
				</div>

				<!-- Products Grid -->
				<div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
					<div
						v-for="product in filteredProducts"
						:key="product.name"
						class="bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-lg transition-shadow"
					>
						<div class="h-40 bg-slate-100 flex items-center justify-center">
							<img
								v-if="product.image"
								:src="product.image"
								:alt="product.product_name"
								class="w-full h-full object-cover"
							/>
							<svg v-else class="w-12 h-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
							</svg>
						</div>
						<div class="p-4">
							<h3 class="font-semibold text-slate-900 truncate">{{ product.product_name }}</h3>
							<p class="text-tookio-600 font-bold mt-1">{{ formatCurrency(product.selling_price) }}</p>
							<div class="flex items-center justify-between mt-3">
								<span class="text-sm text-slate-500">Stock: {{ product.current_stock || 0 }}</span>
								<span
									class="px-2 py-0.5 text-xs rounded-full"
									:class="product.current_stock > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
								>
									{{ product.current_stock > 0 ? 'In Stock' : 'Out of Stock' }}
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
import { ref, computed } from "vue"
import { createResource } from "frappe-ui"
import Sidebar from "@/components/layout/Sidebar.vue"
import UserMenu from "@/components/common/UserMenu.vue"

const sidebarOpen = ref(false)
const showCreateDialog = ref(false)
const searchQuery = ref("")
const products = ref([])
const loading = ref(true)

const productsResource = createResource({
	url: "frappe.client.get_list",
	makeParams() {
		return {
			doctype: "Product",
			fields: ["name", "product_name", "selling_price", "current_stock", "image"],
			order_by: "creation desc",
		}
	},
	auto: true,
	onSuccess(data) {
		products.value = data
		loading.value = false
	},
	onError() {
		loading.value = false
	},
})

const filteredProducts = computed(() => {
	if (!searchQuery.value) return products.value
	const query = searchQuery.value.toLowerCase()
	return products.value.filter((p) =>
		p.product_name?.toLowerCase().includes(query)
	)
})

function formatCurrency(amount) {
	return new Intl.NumberFormat("en-KE", {
		style: "currency",
		currency: "KES",
		minimumFractionDigits: 0,
	}).format(amount || 0)
}
</script>
