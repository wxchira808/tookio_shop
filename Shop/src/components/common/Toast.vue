<template>
	<Teleport to="body">
		<TransitionGroup
			tag="div"
			class="fixed bottom-4 right-4 z-[9999] flex flex-col gap-2"
			enter-active-class="transition-all duration-300 ease-out"
			enter-from-class="translate-x-full opacity-0"
			enter-to-class="translate-x-0 opacity-100"
			leave-active-class="transition-all duration-200 ease-in"
			leave-from-class="translate-x-0 opacity-100"
			leave-to-class="translate-x-full opacity-0"
		>
			<div
				v-for="toast in toasts"
				:key="toast.id"
				class="flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg min-w-[280px] max-w-sm"
				:class="getToastClasses(toast.type)"
			>
				<component :is="getIcon(toast.type)" class="w-5 h-5 flex-shrink-0" />
				<p class="text-sm font-medium flex-1">{{ toast.message }}</p>
				<button
					@click="removeToast(toast.id)"
					class="p-1 rounded-lg hover:bg-black/10 transition-colors"
				>
					<XIcon class="w-4 h-4" />
				</button>
			</div>
		</TransitionGroup>
	</Teleport>
</template>

<script setup>
import { ref, h, defineComponent } from "vue"

// Toast store
const toasts = ref([])
let toastId = 0

// Icons as inline SVG components
const CheckCircleIcon = defineComponent({
	render() {
		return h("svg", { 
			fill: "none", 
			viewBox: "0 0 24 24", 
			"stroke-width": "2", 
			stroke: "currentColor" 
		}, [
			h("path", { 
				"stroke-linecap": "round", 
				"stroke-linejoin": "round", 
				d: "M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
			})
		])
	}
})

const XCircleIcon = defineComponent({
	render() {
		return h("svg", { 
			fill: "none", 
			viewBox: "0 0 24 24", 
			"stroke-width": "2", 
			stroke: "currentColor" 
		}, [
			h("path", { 
				"stroke-linecap": "round", 
				"stroke-linejoin": "round", 
				d: "M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
			})
		])
	}
})

const ExclamationIcon = defineComponent({
	render() {
		return h("svg", { 
			fill: "none", 
			viewBox: "0 0 24 24", 
			"stroke-width": "2", 
			stroke: "currentColor" 
		}, [
			h("path", { 
				"stroke-linecap": "round", 
				"stroke-linejoin": "round", 
				d: "M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" 
			})
		])
	}
})

const InfoIcon = defineComponent({
	render() {
		return h("svg", { 
			fill: "none", 
			viewBox: "0 0 24 24", 
			"stroke-width": "2", 
			stroke: "currentColor" 
		}, [
			h("path", { 
				"stroke-linecap": "round", 
				"stroke-linejoin": "round", 
				d: "M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" 
			})
		])
	}
})

const XIcon = defineComponent({
	render() {
		return h("svg", { 
			fill: "none", 
			viewBox: "0 0 24 24", 
			"stroke-width": "2", 
			stroke: "currentColor" 
		}, [
			h("path", { 
				"stroke-linecap": "round", 
				"stroke-linejoin": "round", 
				d: "M6 18L18 6M6 6l12 12" 
			})
		])
	}
})

function getToastClasses(type) {
	switch (type) {
		case "success":
			return "bg-tookio-500 text-white"
		case "error":
			return "bg-red-500 text-white"
		case "warning":
			return "bg-amber-500 text-white"
		case "info":
		default:
			return "bg-slate-700 text-white"
	}
}

function getIcon(type) {
	switch (type) {
		case "success":
			return CheckCircleIcon
		case "error":
			return XCircleIcon
		case "warning":
			return ExclamationIcon
		case "info":
		default:
			return InfoIcon
	}
}

function addToast(message, type = "info", duration = 4000) {
	const id = ++toastId
	toasts.value.push({ id, message, type })

	if (duration > 0) {
		setTimeout(() => {
			removeToast(id)
		}, duration)
	}

	return id
}

function removeToast(id) {
	const index = toasts.value.findIndex((t) => t.id === id)
	if (index > -1) {
		toasts.value.splice(index, 1)
	}
}

// Expose toast functions globally
if (typeof window !== "undefined") {
	window.$toast = {
		success: (msg, duration) => addToast(msg, "success", duration),
		error: (msg, duration) => addToast(msg, "error", duration),
		warning: (msg, duration) => addToast(msg, "warning", duration),
		info: (msg, duration) => addToast(msg, "info", duration),
	}
}

// Export for use in Vue components
export { addToast, removeToast }
</script>
