<template>
	<div class="min-h-screen bg-slate-50">
		<header class="lg:hidden bg-white border-b border-slate-200 px-4 py-3 sticky top-0 z-40">
			<div class="flex items-center justify-between">
				<button @click="sidebarOpen = true" class="p-2 -ml-2 rounded-lg hover:bg-slate-100">
					<svg class="w-6 h-6 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
					</svg>
				</button>
				<h1 class="text-lg font-semibold text-slate-900">Settings</h1>
				<UserMenu />
			</div>
		</header>

		<div class="flex">
			<Sidebar v-model:open="sidebarOpen" />

			<main class="flex-1 lg:ml-64 p-4 lg:p-8">
				<div class="mb-8">
					<h1 class="text-2xl lg:text-3xl font-bold text-slate-900">Settings</h1>
					<p class="text-slate-500 mt-1">Manage your account and preferences</p>
				</div>

				<div class="space-y-6">
					<!-- Profile Settings -->
					<div class="bg-white rounded-2xl border border-slate-200 p-6">
						<h2 class="text-lg font-semibold text-slate-900 mb-6">Profile</h2>
						<div class="flex items-center gap-6 mb-6">
							<div class="w-20 h-20 rounded-full bg-tookio-100 flex items-center justify-center">
								<span class="text-2xl font-bold text-tookio-600">{{ userInitials }}</span>
							</div>
							<div>
								<p class="font-semibold text-slate-900">{{ userName }}</p>
								<p class="text-sm text-slate-500">{{ userId }}</p>
							</div>
						</div>
						<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
							<div>
								<label class="block text-sm font-medium text-slate-700 mb-2">Full Name</label>
								<input
									:value="userName"
									disabled
									class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-700"
								/>
							</div>
							<div>
								<label class="block text-sm font-medium text-slate-700 mb-2">Email</label>
								<input
									:value="userId"
									disabled
									class="w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-700"
								/>
							</div>
						</div>
					</div>

					<!-- Account Actions -->
					<div class="bg-white rounded-2xl border border-slate-200 p-6">
						<h2 class="text-lg font-semibold text-slate-900 mb-6">Account</h2>
						<div class="space-y-4">
							<a
								href="/app/user"
								class="flex items-center justify-between p-4 rounded-xl border border-slate-200 hover:bg-slate-50 transition-colors"
							>
								<div class="flex items-center gap-3">
									<div class="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center">
										<svg class="w-5 h-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
										</svg>
									</div>
									<div>
										<p class="font-medium text-slate-900">Change Password</p>
										<p class="text-sm text-slate-500">Update your account password</p>
									</div>
								</div>
								<svg class="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
								</svg>
							</a>

							<button
								@click="handleLogout"
								class="flex items-center justify-between w-full p-4 rounded-xl border border-red-200 hover:bg-red-50 transition-colors"
							>
								<div class="flex items-center gap-3">
									<div class="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
										<svg class="w-5 h-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
											<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
										</svg>
									</div>
									<div class="text-left">
										<p class="font-medium text-red-600">Sign Out</p>
										<p class="text-sm text-slate-500">Log out of your account</p>
									</div>
								</div>
							</button>
						</div>
					</div>
				</div>
			</main>
		</div>
	</div>
</template>

<script setup>
import { ref } from "vue"
import { useUserData } from "@/data/user"
import { session } from "@/data/session"
import Sidebar from "@/components/layout/Sidebar.vue"
import UserMenu from "@/components/common/UserMenu.vue"

const { userName, userInitials, userId } = useUserData()
const sidebarOpen = ref(false)

function handleLogout() {
	session.logout.submit()
}
</script>
