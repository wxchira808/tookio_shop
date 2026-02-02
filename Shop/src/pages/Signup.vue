<template>
	<div class="min-h-screen flex bg-white">
		<!-- Left Side - Branding Panel (Hidden on mobile) -->
		<div class="hidden lg:flex lg:w-1/2 xl:w-3/5 bg-gradient-to-br from-tookio-600 via-tookio-500 to-tookio-700 relative overflow-hidden">
			<!-- Decorative Elements -->
			<div class="absolute inset-0">
				<div class="absolute top-1/4 left-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse-slow"></div>
				<div class="absolute bottom-1/4 right-1/4 w-80 h-80 bg-tookio-300/20 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 1s"></div>
				<div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.5) 1px, transparent 0); background-size: 40px 40px;"></div>
			</div>
			
			<!-- Content -->
			<div class="relative z-10 flex flex-col justify-center px-12 xl:px-20">
				<div class="mb-8">
					<div class="w-20 h-20 rounded-2xl shadow-lg bg-white p-3 flex items-center justify-center">
						<svg class="w-12 h-12 text-tookio-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
							<path stroke-linecap="round" stroke-linejoin="round" d="M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.016a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72L4.318 3.44A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.75c0 .415.336.75.75.75z" />
						</svg>
					</div>
				</div>
				
				<h1 class="text-4xl xl:text-5xl font-bold text-white mb-4 leading-tight">
					Start selling today.<br/>
					<span class="text-tookio-100">It's free to begin.</span>
				</h1>
				
				<p class="text-lg text-tookio-100/80 max-w-md mb-10">
					Create your shop in minutes. Track inventory, manage sales, and grow your business with Tookio Shop.
				</p>

				<div class="flex flex-wrap gap-3">
					<span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 text-white text-sm backdrop-blur-sm">
						<svg class="w-4 h-4 text-tookio-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
						</svg>
						Free to start
					</span>
					<span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 text-white text-sm backdrop-blur-sm">
						<svg class="w-4 h-4 text-tookio-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						Setup in 2 minutes
					</span>
					<span class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 text-white text-sm backdrop-blur-sm">
						<svg class="w-4 h-4 text-tookio-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
						</svg>
						WhatsApp ready
					</span>
				</div>
			</div>
		</div>
		
		<!-- Right Side - Signup Form -->
		<div class="w-full lg:w-1/2 xl:w-2/5 flex flex-col items-center justify-center p-6 sm:p-10 bg-white">
			<div class="w-full max-w-md">
				<!-- Mobile Logo -->
				<div class="lg:hidden text-center mb-10">
					<div class="inline-flex w-16 h-16 rounded-xl shadow-md mb-4 bg-tookio-500 items-center justify-center">
						<svg class="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
							<path stroke-linecap="round" stroke-linejoin="round" d="M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.016a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72L4.318 3.44A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.75c0 .415.336.75.75.75z" />
						</svg>
					</div>
					<h1 class="text-2xl font-bold text-slate-900">Tookio Shop</h1>
					<p class="text-slate-500 text-sm mt-1">Create your free account</p>
				</div>
				
				<!-- Desktop Header -->
				<div class="hidden lg:block mb-8">
					<h2 class="text-2xl font-bold text-slate-900">Create your account</h2>
					<p class="text-slate-500 mt-1">Start managing your shop today</p>
				</div>

				<!-- Success Message -->
				<div v-if="signupSuccess" class="rounded-xl bg-tookio-50 border border-tookio-200 p-6 text-center">
					<div class="w-16 h-16 mx-auto mb-4 rounded-full bg-tookio-100 flex items-center justify-center">
						<svg class="w-8 h-8 text-tookio-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
							<path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
						</svg>
					</div>
					<h3 class="text-lg font-semibold text-slate-900 mb-2">Check your email</h3>
					<p class="text-slate-600 text-sm">
						We've sent a verification link to <strong>{{ signupForm.email }}</strong>. Click the link to set your password and activate your account.
					</p>
					<router-link 
						to="/login" 
						class="inline-block mt-6 text-tookio-600 font-semibold hover:text-tookio-500 transition-colors"
					>
						← Back to login
					</router-link>
				</div>
				
				<!-- Signup Form -->
				<form v-else class="space-y-5" @submit.prevent="submit">
					<!-- Error Alert -->
					<div v-if="errorMessage" class="rounded-xl bg-red-50 border border-red-200 p-4">
						<div class="flex items-start gap-3">
							<svg class="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
								<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
							</svg>
							<p class="text-sm text-red-600">{{ errorMessage }}</p>
						</div>
					</div>

					<!-- Full Name Input -->
					<div>
						<label class="block text-sm font-medium text-slate-700 mb-2">
							Full Name
						</label>
						<input
							v-model="signupForm.fullName"
							required
							name="full_name"
							type="text"
							placeholder="John Doe"
							:disabled="isLoading"
							class="w-full px-4 py-3.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:border-tookio-500 focus:ring-2 focus:ring-tookio-500/20 focus:outline-none transition-all disabled:opacity-50"
						/>
					</div>

					<!-- Email Input -->
					<div>
						<label class="block text-sm font-medium text-slate-700 mb-2">
							Email Address
						</label>
						<input
							v-model="signupForm.email"
							required
							name="email"
							type="email"
							placeholder="you@example.com"
							:disabled="isLoading"
							class="w-full px-4 py-3.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:border-tookio-500 focus:ring-2 focus:ring-tookio-500/20 focus:outline-none transition-all disabled:opacity-50"
						/>
					</div>

					<!-- Sign Up Button -->
					<button
						type="submit"
						:disabled="isLoading"
						class="w-full py-4 px-6 rounded-xl text-base font-semibold text-white bg-gradient-to-r from-tookio-500 to-tookio-600 hover:from-tookio-400 hover:to-tookio-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-tookio-500 shadow-lg shadow-tookio-500/25 hover:shadow-xl hover:shadow-tookio-500/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
					>
						<svg v-if="isLoading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
						{{ isLoading ? 'Creating account...' : 'Create account' }}
					</button>

					<!-- Terms -->
					<p class="text-xs text-slate-500 text-center">
						By signing up, you agree to our 
						<a href="/privacy-policy" class="text-tookio-600 hover:underline">Privacy Policy</a>
						and 
						<a href="/terms" class="text-tookio-600 hover:underline">Terms of Service</a>
					</p>
				</form>

				<!-- Login Link -->
				<div v-if="!signupSuccess" class="mt-6 text-center">
					<p class="text-slate-500 text-sm">
						Already have an account?
						<router-link to="/login" class="text-tookio-600 font-semibold hover:text-tookio-500 transition-colors">
							Sign in
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
import { reactive, ref } from "vue"
import { createResource } from "frappe-ui"

const signupForm = reactive({
	fullName: "",
	email: "",
})

const isLoading = ref(false)
const signupSuccess = ref(false)
const errorMessage = ref("")

// Signup resource
const signupResource = createResource({
	url: "tookio_shop.api.auth.signup",
	onSuccess() {
		isLoading.value = false
		signupSuccess.value = true
		errorMessage.value = ""
	},
	onError(error) {
		isLoading.value = false
		errorMessage.value = error.messages?.[0] || error.message || "Failed to create account. Please try again."
	},
})

function submit() {
	if (!signupForm.fullName || !signupForm.email) {
		return
	}

	errorMessage.value = ""
	isLoading.value = true

	signupResource.submit({
		full_name: signupForm.fullName.trim(),
		email: signupForm.email.trim().toLowerCase(),
	})
}
</script>
