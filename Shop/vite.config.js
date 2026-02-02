import path from "node:path"
import vue from "@vitejs/plugin-vue"
import frappeui from "frappe-ui/vite"
import { defineConfig } from "vite"

// Get build version from environment or use timestamp
const buildVersion = process.env.TOOKIO_SHOP_BUILD_VERSION || Date.now().toString()
const enableSourceMap = process.env.TOOKIO_SHOP_ENABLE_SOURCEMAP === "true"

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [
		frappeui({
			frappeProxy: true,
			jinjaBootData: true,
			lucideIcons: true,
			buildConfig: {
				indexHtmlPath: "../tookio_shop/www/shop.html",
				outDir: "../tookio_shop/public/shop",
				emptyOutDir: true,
				sourcemap: enableSourceMap,
			},
		}),
		vue(),
	],
	build: {
		chunkSizeWarningLimit: 1500,
		outDir: "../tookio_shop/public/shop",
		emptyOutDir: true,
		target: "es2015",
		sourcemap: enableSourceMap,
	},
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "src"),
			"tailwind.config.js": path.resolve(__dirname, "tailwind.config.js"),
		},
	},
	define: {
		__BUILD_VERSION__: JSON.stringify(buildVersion),
	},
	optimizeDeps: {
		include: [
			"feather-icons",
			"showdown",
		],
	},
	server: {
		allowedHosts: true,
		port: 8081,
		proxy: {
			"^/(app|api|assets|files|printview)": {
				target: "http://127.0.0.1:8000",
				ws: true,
				changeOrigin: true,
				secure: false,
				cookieDomainRewrite: "localhost",
				router: (req) => {
					const site_name = req.headers.host.split(":")[0]
					const isLocalhost = site_name === "localhost" || site_name === "127.0.0.1"
					const targetHost = isLocalhost ? "127.0.0.1" : site_name
					return `http://${targetHost}:8000`
				},
			},
		},
	},
})
