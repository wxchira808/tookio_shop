<template>
	<div class="flex items-center justify-center" :class="containerClass">
		<svg
			class="animate-spin"
			:class="[sizeClass, colorClass]"
			fill="none"
			viewBox="0 0 24 24"
		>
			<circle
				class="opacity-25"
				cx="12"
				cy="12"
				r="10"
				stroke="currentColor"
				stroke-width="4"
			></circle>
			<path
				class="opacity-75"
				fill="currentColor"
				d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
			></path>
		</svg>
		<span v-if="text" class="ml-2" :class="textClass">{{ text }}</span>
	</div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
	size: {
		type: String,
		default: "md",
		validator: (v) => ["sm", "md", "lg", "xl"].includes(v),
	},
	color: {
		type: String,
		default: "tookio",
	},
	text: {
		type: String,
		default: "",
	},
	fullPage: {
		type: Boolean,
		default: false,
	},
})

const sizeClass = computed(() => {
	const sizes = {
		sm: "w-4 h-4",
		md: "w-6 h-6",
		lg: "w-8 h-8",
		xl: "w-12 h-12",
	}
	return sizes[props.size]
})

const colorClass = computed(() => {
	const colors = {
		tookio: "text-tookio-500",
		white: "text-white",
		gray: "text-gray-500",
	}
	return colors[props.color] || "text-tookio-500"
})

const textClass = computed(() => {
	const sizes = {
		sm: "text-xs",
		md: "text-sm",
		lg: "text-base",
		xl: "text-lg",
	}
	return sizes[props.size]
})

const containerClass = computed(() => {
	return props.fullPage ? "min-h-screen" : ""
})
</script>
