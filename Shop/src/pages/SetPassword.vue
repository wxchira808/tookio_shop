<template>
	<div class="min-h-screen flex bg-white">
		<!-- Left Side - Branding Panel (Hidden on mobile) -->
		<div class="hidden lg:flex lg:w-1/2 xl:w-3/5 bg-gradient-to-br from-tookio-600 via-tookio-500 to-tookio-700 relative overflow-hidden">
			<div class="absolute inset-0">
				<div class="absolute top-1/4 left-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-pulse-slow"></div>
				<div class="absolute bottom-1/4 right-1/4 w-80 h-80 bg-tookio-300/20 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 1s"></div>
				<div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.5) 1px, transparent 0); background-size: 40px 40px;"></div>
			</div>
			
			<div class="relative z-10 flex flex-col justify-center px-12 xl:px-20">
				<div class="mb-8">
					<div class="w-20 h-20 rounded-2xl shadow-lg bg-white p-3 flex items-center justify-center">
						<svg class="w-12 h-12 text-tookio-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
							<path stroke-linecap="round" stroke-linejoin="round" d="M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.016a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72L4.318 3.44A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.75c0 .415.336.75.75.75z" />
						</svg>
					</div>
				</div>
				
				<h1 class="text-4xl xl:text-5xl font-bold text-white mb-4 leading-tight">
					Almost there!<br/>
					<span class="text-tookio-100">Set your password.</span>
				</h1>
				
				<p class="text-lg text-tookio-100/80 max-w-md">
					Create a secure password to complete your account setup and start using Tookio Shop.
				</p>
			</div>
		</div>
		
		<!-- Right Side - Set Password Form -->
		<div class="w-full lg:w-1/2 xl:w-2/5 flex flex-col items-center justify-center p-6 sm:p-10 bg-white">
			<div class="w-full max-w-md">
				<!-- Mobile Logo -->
				<div class="lg:hidden text-center mb-10">
					<div class="inline-flex w-16 h-16 rounded-xl shadow-md mb-4 bg-tookio-500 items-center justify-center">
						<svg class="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
							<path stroke-linecap="round" stroke-linejoin="round" d="M13.5 21v-7.5a.75.75 0 01.75-.75h3a.75.75 0 01.75.75V21m-4.5 0H2.36m11.14 0H18m0 0h3.64m-1.39 0V9.349m-16.5 11.65V9.35m0 0a3.001 3.001 0 003.75-.615A2.993 2.993 0 009.75 9.75c.896 0 1.7-.393 2.25-1.016a2.993 2.993 0 002.25 1.016c.896 0 1.7-.393 2.25-1.016a3.001 3.001 0 003.75.614m-16.5 0a3.004 3.004 0 01-.621-4.72L4.318 3.44A1.5 1.5 0 015.378 3h13.243a1.5 1.5 0 011.06.44l1.19 1.189a3 3 0 01-.621 4.72m-13.5 8.65h3.75a.75.75 0 00.75-.75V13.5a.75.75 0 00-.75-.75H6.75a.75.75 0 00-.75.75v3.75c0 .415.336.75.75.75z" />
						</svg>
					</div>
					<h1 class="text-2xl font-bold text-slate-900">Set Password</h1>
					<p class="text-slate-500 text-sm mt-1">Create your account password</p>
				</div>
				
				<!-- Desktop Header -->
				<div class="hidden lg:block mb-8">
					<h2 class="text-2xl font-bold text-slate-900">Set your password</h2>
					<p class="text-slate-500 mt-1">Create a secure password for your account</p>
				</div>

				<!-- Invalid Key Message -->
				<div v-if="invalidKey" class="rounded-xl bg-red-50 border border-red-200 p-6 text-center">
					<div class="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
						<svg class="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
							<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
						</svg>
					</div>
					<h3 class="text-lg font-semibold text-slate-900 mb-2">Invalid or Expired Link</h3>
					<p class="text-slate-600 text-sm">
						This password reset link is invalid or has expired. Please request a new one.
					</p>
					<router-link 
						to="/signup" 
						class="inline-block mt-6 text-tookio-600 font-semibold hover:text-tookio-500 transition-colors"
					>
						← Back to signup
					</router-link>
				</div>

				<!-- Success Message -->
				<div v-else-if="passwordSet" class="rounded-xl bg-tookio-50 border border-tookio-200 p-6 text-center">
					<div class="w-16 h-16 mx-auto mb-4 rounded-full bg-tookio-100 flex items-center justify-center">
						<svg class="w-8 h-8 text-tookio-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
							<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
						</svg>
					</div>
					<h3 class="text-lg font-semibold text-slate-900 mb-2">Password Set Successfully!</h3>
					<p class="text-slate-600 text-sm">
						Your account is now active. You can sign in with your email and password.
					</p>
					<router-link 
						to="/login" 
						class="inline-block mt-6 px-6 py-3 rounded-xl text-white bg-tookio-500 hover:bg-tookio-600 font-semibold transition-colors"
					>
						Sign in now
					</router-link>
				</div>
				
				<!-- Set Password Form -->
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

					<!-- Password Input -->
					<div>
						<label class="block text-sm font-medium text-slate-700 mb-2">
							New Password
						</label>
						<div class="relative">
							<input
								v-model="passwordForm.password"
								required
								name="password"
								:type="showPassword ? 'text' : 'password'"
								placeholder="Enter your password"
								:disabled="isLoading"
								minlength="8"
								class="w-full px-4 py-3.5 pe-12 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:border-tookio-500 focus:ring-2 focus:ring-tookio-500/20 focus:outline-none transition-all disabled:opacity-50"
							/>
							<button
								type="button"
								@click="showPassword = !showPassword"
								class="absolute inset-y-0 end-0 flex items-center pe-4 text-slate-500 hover:text-tookio-500 transition-colors focus:outline-none"
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
						<p class="mt-1 text-xs text-slate-500">Must be at least 8 characters</p>
					</div>

					<!-- Confirm Password Input -->
					<div>
						<label class="block text-sm font-medium text-slate-700 mb-2">
							Confirm Password
						</label>
						<input
							v-model="passwordForm.confirmPassword"
							required
							name="confirm_password"
							:type="showPassword ? 'text' : 'password'"
							placeholder="Confirm your password"
							:disabled="isLoading"
							class="w-full px-4 py-3.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:border-tookio-500 focus:ring-2 focus:ring-tookio-500/20 focus:outline-none transition-all disabled:opacity-50"
						/>
					</div>

					<!-- Submit Button -->
					<button
						type="submit"
						:disabled="isLoading"
						class="w-full py-4 px-6 rounded-xl text-base font-semibold text-white bg-gradient-to-r from-tookio-500 to-tookio-600 hover:from-tookio-400 hover:to-tookio-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-tookio-500 shadow-lg shadow-tookio-500/25 hover:shadow-xl hover:shadow-tookio-500/30 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
					>
						<svg v-if="isLoading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
							<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
							<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
						</svg>
						{{ isLoading ? 'Setting password...' : 'Set password' }}
					</button>
				</form>

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
import { onMounted, reactive, ref } from "vue"
import { useRoute } from "vue-router"
import { createResource } from "frappe-ui"

const route = useRoute()

const passwordForm = reactive({
	password: "",
	confirmPassword: "",
})

const isLoading = ref(false)
const passwordSet = ref(false)
const invalidKey = ref(false)
const errorMessage = ref("")
const showPassword = ref(false)

// Get the key from URL
const key = ref("")

onMounted(() => {
	key.value = route.query.key || ""
	if (!key.value) {
		invalidKey.value = true
	}
})

// Set password resource
const setPasswordResource = createResource({
	url: "tookio_shop.api.auth.set_password",
	onSuccess() {
		isLoading.value = false
		passwordSet.value = true
		errorMessage.value = ""
	},
	onError(error) {
		isLoading.value = false
		if (error.message?.includes("Invalid") || error.message?.includes("expired")) {
			invalidKey.value = true
		} else {
			errorMessage.value = error.messages?.[0] || error.message || "Failed to set password. Please try again."
		}
	},
})

function submit() {
	if (!passwordForm.password || !passwordForm.confirmPassword) {
		return
	}

	if (passwordForm.password !== passwordForm.confirmPassword) {
		errorMessage.value = "Passwords do not match"
		return
	}

	if (passwordForm.password.length < 8) {
		errorMessage.value = "Password must be at least 8 characters"
		return
	}

	errorMessage.value = ""
	isLoading.value = true

	setPasswordResource.submit({
		key: key.value,
		password: passwordForm.password,
	})
}
</script>
