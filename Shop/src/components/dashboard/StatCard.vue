<template>
	<div class="bg-white rounded-2xl border border-slate-200 p-6">
		<div class="flex items-center justify-between">
			<div>
				<p class="text-sm text-slate-500">{{ title }}</p>
				<div class="mt-1">
					<span v-if="loading" class="inline-block h-8 w-20 bg-slate-200 rounded animate-pulse"></span>
					<p v-else class="text-2xl font-bold text-slate-900">{{ value }}</p>
				</div>
			</div>
			<div
				class="w-12 h-12 rounded-xl flex items-center justify-center"
				:class="iconBgClass"
			>
				<component :is="iconComponent" class="w-6 h-6" :class="iconColorClass" />
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed, h, defineComponent } from "vue"

const props = defineProps({
	title: String,
	value: [String, Number],
	icon: String,
	color: {
		type: String,
		default: "tookio",
	},
	loading: Boolean,
})

const iconBgClass = computed(() => {
	const classes = {
		tookio: "bg-tookio-100",
		green: "bg-green-100",
		blue: "bg-blue-100",
		amber: "bg-amber-100",
		red: "bg-red-100",
		purple: "bg-purple-100",
	}
	return classes[props.color] || classes.tookio
})

const iconColorClass = computed(() => {
	const classes = {
		tookio: "text-tookio-600",
		green: "text-green-600",
		blue: "text-blue-600",
		amber: "text-amber-600",
		red: "text-red-600",
		purple: "text-purple-600",
	}
	return classes[props.color] || classes.tookio
})

// Icons
const PackageIcon = defineComponent({
	render() {
		return h("svg", { fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "2" }, [
			h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" })
		])
	}
})

const TrendingUpIcon = defineComponent({
	render() {
		return h("svg", { fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "2" }, [
			h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" })
		])
	}
})

const FileTextIcon = defineComponent({
	render() {
		return h("svg", { fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "2" }, [
			h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" })
		])
	}
})

const StoreIcon = defineComponent({
	render() {
		return h("svg", { fill: "none", viewBox: "0 0 24 24", stroke: "currentColor", "stroke-width": "2" }, [
			h("path", { "stroke-linecap": "round", "stroke-linejoin": "round", d: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" })
		])
	}
})

const iconComponent = computed(() => {
	const icons = {
		package: PackageIcon,
		"trending-up": TrendingUpIcon,
		"file-text": FileTextIcon,
		store: StoreIcon,
	}
	return icons[props.icon] || PackageIcon
})
</script>
