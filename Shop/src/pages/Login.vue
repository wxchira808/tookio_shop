<template>
	<div class="min-h-screen flex bg-white">
		<!-- Left Side - Branding Panel (Hidden on mobile) -->
		<div class="hidden lg:flex lg:w-1/2 xl:w-3/5 bg-gradient-to-br from-tookio-600 via-tookio-500 to-tookio-700 relative overflow-hidden">
			<!-- Decorative Elements -->
			<div class="absolute inset-0">
				<!-- Gradient Orbs -->
				<div class="absolute top-1/4 left-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse-slow"></div>
				<div class="absolute bottom-1/4 right-1/4 w-80 h-80 bg-tookio-300/20 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 1s"></div>
				
				<!-- Grid Pattern -->
				<div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.5) 1px, transparent 0); background-size: 40px 40px;"></div>
			</div>
			
			<!-- Content -->
			<div class="relative z-10 flex flex-col justify-center px-12 xl:px-20">
				<!-- Logo -->
				<div class="mb-8">
					<div class="w-20 h-20 rounded-2xl shadow-lg bg-white p-3 flex items-center justify-center">
						<svg class="w-12 h-12 text-tookio-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
							<path stroke-linecap="round" stroke-linejoin="round" d="M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.016a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72L4.318 3.44A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.75c0 .415.336.75.75.75z" />
						</svg>
					</div>
				</div>
				
				<!-- Headline -->
				<h1 class="text-4xl xl:text-5xl font-bold text-white mb-4 leading-tight">
					Manage your shop.<br/>
					<span class="text-tookio-100">Grow your business.</span>
				</h1>
				
				<p class="text-lg text-tookio-100/80 max-w-md mb-10">
					Simple inventory and sales management for WhatsApp and Instagram sellers. Track products, manage stock, and create invoices easily.
				</p>
				
				<!-- Feature Pills -->
				<div class="flex flex-wrap gap-3">
					<span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 text-white text-sm backdrop-blur-sm">
						<svg class="w-4 h-4 text-tookio-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
						</svg>
						Inventory Tracking
					</span>
					<span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 text-white text-sm backdrop-blur-sm">
						<svg class="w-4 h-4 text-tookio-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						</svg>
						Easy Invoicing
					</span>
					<span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 text-white text-sm backdrop-blur-sm">
						<svg class="w-4 h-4 text-tookio-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
						</svg>
						Sales Reports
					</span>
				</div>
			</div>
		</div>
		
		<!-- Right Side - Login Form -->
		<div class="w-full lg:w-1/2 xl:w-2/5 flex flex-col items-center justify-center p-6 sm:p-10 bg-white">
			<div class="w-full max-w-md">
				<!-- Mobile Logo (visible only on mobile) -->
				<div class="lg:hidden text-center mb-10">
					<div class="inline-flex w-16 h-16 rounded-xl shadow-md mb-4 bg-tookio-500 items-center justify-center">
						<svg class="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
							<path stroke-linecap="round" stroke-linejoin="round" d="M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.016a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72L4.318 3.44A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.75c0 .415.336.75.75.75z" />
						</svg>
					</div>
					<h1 class="text-2xl font-bold text-slate-900">Tookio Shop</h1>
					<p class="text-slate-500 text-sm mt-1">Sign in to continue</p>
				</div>
				
				<!-- Desktop Header -->
				<div class="hidden lg:block mb-8">
					<h2 class="text-2xl font-bold text-slate-900">Welcome back</h2>
					<p class="text-slate-500 mt-1">Sign in to your account to continue</p>
				</div>
				
				<!-- Login Form -->
				<form class="space-y-5" @submit.prevent="submit">
					<!-- Error Alert -->
					<div v-if="session.login.error" class="rounded-xl bg-red-50 border border-red-200 p-4">
						<div class="flex items-start gap-3">
							<svg class="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
								<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
							</svg>
							<p class="text-sm text-red-600">
								{{ session.login.error.messages?.join('\n') || 'Invalid email or password' }}
							</p>
						</div>
					</div>

					<!-- Email Input -->
					<div>
						<label class="block text-sm font-medium text-slate-700 mb-2">
							Email or Username
						</label>
						<input
							v-model="loginForm.email"
							required
							name="email"
							type="text"
							placeholder="you@example.com"
							:disabled="session.login.loading"
							class="w-full px-4 py-3.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:border-tookio-500 focus:ring-2 focus:ring-tookio-500/20 focus:outline-none transition-all disabled:opacity-50"
						/>
					</div>

					<!-- Password Input -->
					<div>
						<label class="block text-sm font-medium text-slate-600 mb-2">
							Password
						</label>
						<div class="relative">
							<input
								v-model="loginForm.password"
								required
								name="password"
								:type="showPassword ? 'text' : 'password'"
								placeholder="Enter your password"
								:disabled="session.login.loading"
								class="w-full px-4 py-3.5 pe-12 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:border-tookio-500 focus:ring-2 focus:ring-tookio-500/20 focus:outline-none transition-all disabled:opacity-50"
							/>
							<button
								type="button"
								@click="showPassword = !showPassword"
								class="absolute inset-y-0 end-0 flex items-center pe-4 text-slate-500 hover:text-tookio-500 transition-colors focus:outline-none"
								:disabled="session.login.loading"
								tabindex="-1"
							>
								<svg v-if="showPassword" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
								</svg>
								<svg v-else class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
									<path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
									<path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
								</svg>
							</button>
						</div>
					</div>

					<!-- Sign In Button -->
					<button
						type="submit"
						:disabled="session.login.loading"
						class="w-full py-4 px-6 rounded-xl text-base font-semibold text-white bg-gradient-to-r from-tookio-500 to-tookio-600 hover:from-tookio-400 hover:to-tookio-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-tookio-500 shadow-lg shadow-tookio-500/25 hover:shadow-xl hover:shadow-tookio-500/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
					>
						<svg v-if="session.login.loading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
						{{ session.login.loading ? 'Signing in...' : 'Sign in' }}
					</button>
				</form>

				<!-- Signup Link -->
				<div class="mt-6 text-center">
					<p class="text-slate-500 text-sm">
						Don't have an account?
						<router-link to="/signup" class="text-tookio-600 font-semibold hover:text-tookio-500 transition-colors">
							Sign up
						</router-link>
					</p>
				</div>

				<!-- Footer -->
				<div class="mt-10 text-center">
					<p class="text-slate-400 text-sm">
						Powered by <span class="text-tookio-500 font-semibold">Tookio</span>
					</p>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from "vue"
import { useRouter } from "vue-router"
import { session } from "@/data/session"

const router = useRouter()

const loginForm = reactive({
	email: "",
	password: "",
})

const showPassword = ref(false)

// Reset state when login page mounts
onMounted(() => {
	loginForm.email = ""
	loginForm.password = ""
	showPassword.value = false

	if (session.login.error) {
		session.login.reset()
	}
})

function submit() {
	if (!loginForm.email || !loginForm.password) {
		return
	}

	session.login.submit({
		email: loginForm.email.trim(),
		password: loginForm.password,
	})
}

// Clear error when user starts typing
watch([() => loginForm.email, () => loginForm.password], () => {
	if (session.login.error) {
		session.login.reset()
	}
})
</script>
