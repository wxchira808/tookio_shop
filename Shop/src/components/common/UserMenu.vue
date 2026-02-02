<template>
	<div class="relative" ref="menuRef">
		<button
			@click="toggleMenu"
			class="flex items-center gap-2 p-2 rounded-xl hover:bg-surface-100 transition-colors"
		>
			<!-- User Avatar -->
			<div
				class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold overflow-hidden"
				:class="userImage ? '' : 'bg-tookio-100 text-tookio-700'"
			>
				<img
					v-if="userImage"
					:src="userImage"
					:alt="userName"
					class="w-full h-full object-cover"
				/>
				<span v-else>{{ userInitials }}</span>
			</div>
			
			<!-- User Name (hidden on mobile) -->
			<div class="hidden md:block text-left">
				<p class="text-sm font-medium text-slate-900 truncate max-w-[120px]">
					{{ userName }}
				</p>
			</div>
			
			<!-- Chevron -->
			<svg
				class="w-4 h-4 text-slate-400 transition-transform hidden md:block"
				:class="{ 'rotate-180': isOpen }"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
			</svg>
		</button>

		<!-- Dropdown Menu -->
		<Transition
			enter-active-class="transition duration-100 ease-out"
			enter-from-class="transform scale-95 opacity-0"
			enter-to-class="transform scale-100 opacity-100"
			leave-active-class="transition duration-75 ease-in"
			leave-from-class="transform scale-100 opacity-100"
			leave-to-class="transform scale-95 opacity-0"
		>
			<div
				v-if="isOpen"
				class="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl shadow-lg border border-slate-100 py-2 z-50"
			>
				<!-- User Info -->
				<div class="px-4 py-3 border-b border-slate-100">
					<p class="text-sm font-medium text-slate-900">{{ userName }}</p>
					<p class="text-xs text-slate-500 truncate">{{ userId }}</p>
				</div>

				<!-- Menu Items -->
				<div class="py-1">
					<router-link
						to="/settings"
						class="flex items-center gap-3 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
						@click="closeMenu"
					>
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
						</svg>
						Settings
					</router-link>

					<a
						href="/app"
						class="flex items-center gap-3 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
					>
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
						</svg>
						Desk View
					</a>
				</div>

				<!-- Logout -->
				<div class="border-t border-slate-100 pt-1">
					<button
						@click="handleLogout"
						class="flex items-center gap-3 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
					>
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
						</svg>
						Sign out
					</button>
				</div>
			</div>
		</Transition>
	</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue"
import { useUserData } from "@/data/user"
import { session } from "@/data/session"

const { userName, userImage, userInitials, userId } = useUserData()

const menuRef = ref(null)
const isOpen = ref(false)

function toggleMenu() {
	isOpen.value = !isOpen.value
}

function closeMenu() {
	isOpen.value = false
}

function handleLogout() {
	closeMenu()
	session.logout.submit()
}

// Close menu on click outside
function handleClickOutside(event) {
	if (menuRef.value && !menuRef.value.contains(event.target)) {
		closeMenu()
	}
}

onMounted(() => {
	document.addEventListener("click", handleClickOutside)
})

onUnmounted(() => {
	document.removeEventListener("click", handleClickOutside)
})
</script>
