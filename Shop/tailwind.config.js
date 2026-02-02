import frappeUIPreset from "frappe-ui/tailwind"

export default {
	presets: [frappeUIPreset],
	content: [
		"./index.html",
		"./src/**/*.{vue,js,ts,jsx,tsx}",
		"./node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}",
	],
	darkMode: 'class',
	theme: {
		extend: {
			colors: {
				// Tookio Shop Brand - Teal/Emerald theme
				tookio: {
					50: '#f0fdfa',
					100: '#ccfbf1',
					200: '#99f6e4',
					300: '#5eead4',
					400: '#2dd4bf',
					500: '#14b8a6',
					600: '#0d9488',
					700: '#0f766e',
					800: '#115e59',
					900: '#134e4a',
					950: '#042f2e',
				},
				// Surface colors - Light/clean theme
				surface: {
					50: '#fafafa',
					100: '#f5f5f5',
					200: '#e5e5e5',
					300: '#d4d4d4',
					400: '#a3a3a3',
					500: '#737373',
					600: '#525252',
					700: '#404040',
					800: '#262626',
					850: '#1f1f1f',
					900: '#171717',
					950: '#0a0a0a',
				},
				// Accent - Warm amber for CTAs and highlights
				accent: {
					50: '#fffbeb',
					100: '#fef3c7',
					200: '#fde68a',
					300: '#fcd34d',
					400: '#fbbf24',
					500: '#f59e0b',
					600: '#d97706',
					700: '#b45309',
					800: '#92400e',
					900: '#78350f',
					950: '#451a03',
				},
				// Status colors
				success: {
					50: '#f0fdf4',
					100: '#dcfce7',
					400: '#4ade80',
					500: '#22c55e',
					600: '#16a34a',
				},
				warning: {
					50: '#fffbeb',
					100: '#fef3c7',
					400: '#fbbf24',
					500: '#f59e0b',
					600: '#d97706',
				},
				danger: {
					50: '#fef2f2',
					100: '#fee2e2',
					400: '#f87171',
					500: '#ef4444',
					600: '#dc2626',
				},
			},
			fontFamily: {
				sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
				mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
			},
			boxShadow: {
				'glass': '0 8px 32px rgba(0, 0, 0, 0.08)',
				'glass-lg': '0 16px 48px rgba(0, 0, 0, 0.12)',
				'glow': '0 0 20px rgba(20, 184, 166, 0.2)',
				'glow-accent': '0 0 20px rgba(245, 158, 11, 0.2)',
				'inner-glass': 'inset 0 1px 0 rgba(255, 255, 255, 0.5)',
				'card': '0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04)',
				'card-hover': '0 10px 25px rgba(0, 0, 0, 0.1)',
				'premium': '0 4px 20px rgba(0, 0, 0, 0.06)',
			},
			borderRadius: {
				'2xl': '1rem',
				'3xl': '1.5rem',
				'4xl': '2rem',
			},
			animation: {
				'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
				'float': 'float 3s ease-in-out infinite',
				'glow': 'glow 2s ease-in-out infinite alternate',
			},
			keyframes: {
				float: {
					'0%, 100%': { transform: 'translateY(0)' },
					'50%': { transform: 'translateY(-5px)' },
				},
				glow: {
					'0%': { boxShadow: '0 0 5px rgba(20, 184, 166, 0.2)' },
					'100%': { boxShadow: '0 0 20px rgba(20, 184, 166, 0.4)' },
				},
			},
		},
	},
	plugins: [],
}
