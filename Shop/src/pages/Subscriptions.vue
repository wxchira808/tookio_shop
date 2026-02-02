<template>
	<div class="min-h-screen bg-slate-50">
		<header class="lg:hidden bg-white border-b border-slate-200 px-4 py-3 sticky top-0 z-40">
			<div class="flex items-center justify-between">
				<button @click="sidebarOpen = true" class="p-2 -ml-2 rounded-lg hover:bg-slate-100">
					<svg class="w-6 h-6 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				</button>
				<h1 class="text-lg font-semibold text-slate-900">Subscription</h1>
				<UserMenu />
			</div>
		</header>

		<div class="flex">
			<Sidebar v-model:open="sidebarOpen" />

			<main class="flex-1 lg:ml-64 p-4 lg:p-8">
				<div class="mb-8">
					<h1 class="text-2xl lg:text-3xl font-bold text-slate-900">Subscription</h1>
					<p class="text-slate-500 mt-1">Manage your plan and billing</p>
				</div>

				<!-- Current Plan -->
				<div class="bg-white rounded-2xl border border-slate-200 p-6 mb-6">
					<div class="flex items-center justify-between mb-6">
						<h2 class="text-lg font-semibold text-slate-900">Current Plan</h2>
						<span class="px-3 py-1 text-sm rounded-full bg-tookio-100 text-tookio-700 font-medium">
							{{ currentPlan?.name || 'Free' }}
						</span>
					</div>

					<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
						<div>
							<p class="text-sm text-slate-500">Products Limit</p>
							<p class="text-2xl font-bold text-slate-900">{{ currentPlan?.product_limit || 10 }}</p>
						</div>
						<div>
							<p class="text-sm text-slate-500">Shops Limit</p>
							<p class="text-2xl font-bold text-slate-900">{{ currentPlan?.shop_limit || 1 }}</p>
						</div>
						<div>
							<p class="text-sm text-slate-500">Monthly Invoices</p>
							<p class="text-2xl font-bold text-slate-900">{{ currentPlan?.invoice_limit || 50 }}</p>
						</div>
					</div>
				</div>

				<!-- Available Plans -->
				<h2 class="text-lg font-semibold text-slate-900 mb-4">Available Plans</h2>
				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					<!-- Free Plan -->
					<div class="bg-white rounded-2xl border border-slate-200 p-6">
						<h3 class="text-xl font-bold text-slate-900 mb-2">Free</h3>
						<p class="text-3xl font-bold text-slate-900 mb-4">
							KES 0
							<span class="text-sm font-normal text-slate-500">/month</span>
						</p>
						<ul class="space-y-3 mb-6">
							<li class="flex items-center gap-2 text-sm text-slate-600">
								<svg class="w-5 h-5 text-tookio-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
								</svg>
								10 Products
							</li>
							<li class="flex items-center gap-2 text-sm text-slate-600">
								<svg class="w-5 h-5 text-tookio-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
								</svg>
								1 Shop
							</li>
							<li class="flex items-center gap-2 text-sm text-slate-600">
								<svg class="w-5 h-5 text-tookio-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
								</svg>
								50 Invoices/month
							</li>
						</ul>
						<button class="w-full py-3 rounded-xl border-2 border-slate-200 text-slate-700 font-medium">
							Current Plan
						</button>
					</div>

					<!-- Starter Plan -->
					<div class="bg-white rounded-2xl border-2 border-tookio-500 p-6 relative">
						<div class="absolute -top-3 left-1/2 -translate-x-1/2">
							<span class="px-3 py-1 text-xs font-semibold bg-tookio-500 text-white rounded-full">Popular</span>
						</div>
						<h3 class="text-xl font-bold text-slate-900 mb-2">Starter</h3>
						<p class="text-3xl font-bold text-slate-900 mb-4">
							KES 500
							<span class="text-sm font-normal text-slate-500">/month</span>
						</p>
						<ul class="space-y-3 mb-6">
							<li class="flex items-center gap-2 text-sm text-slate-600">
								<svg class="w-5 h-5 text-tookio-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
								</svg>
								100 Products
							</li>
							<li class="flex items-center gap-2 text-sm text-slate-600">
								<svg class="w-5 h-5 text-tookio-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
								</svg>
								3 Shops
							</li>
							<li class="flex items-center gap-2 text-sm text-slate-600">
								<svg class="w-5 h-5 text-tookio-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
								</svg>
								Unlimited Invoices
							</li>
						</ul>
						<button class="w-full py-3 rounded-xl bg-tookio-500 text-white font-medium hover:bg-tookio-600 transition-colors">
							Upgrade
						</button>
					</div>

					<!-- Business Plan -->
					<div class="bg-white rounded-2xl border border-slate-200 p-6">
						<h3 class="text-xl font-bold text-slate-900 mb-2">Business</h3>
						<p class="text-3xl font-bold text-slate-900 mb-4">
							KES 1,500
							<span class="text-sm font-normal text-slate-500">/month</span>
						</p>
						<ul class="space-y-3 mb-6">
							<li class="flex items-center gap-2 text-sm text-slate-600">
								<svg class="w-5 h-5 text-tookio-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
								</svg>
								Unlimited Products
							</li>
							<li class="flex items-center gap-2 text-sm text-slate-600">
								<svg class="w-5 h-5 text-tookio-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
								</svg>
								Unlimited Shops
							</li>
							<li class="flex items-center gap-2 text-sm text-slate-600">
								<svg class="w-5 h-5 text-tookio-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
								</svg>
								Priority Support
							</li>
						</ul>
						<button class="w-full py-3 rounded-xl border-2 border-tookio-500 text-tookio-600 font-medium hover:bg-tookio-50 transition-colors">
							Upgrade
						</button>
					</div>
				</div>
			</main>
		</div>
	</div>
</template>

<script setup>
import { ref } from "vue"
import Sidebar from "@/components/layout/Sidebar.vue"
import UserMenu from "@/components/common/UserMenu.vue"

const sidebarOpen = ref(false)
const currentPlan = ref({
	name: "Free",
	product_limit: 10,
	shop_limit: 1,
	invoice_limit: 50,
})
</script>
