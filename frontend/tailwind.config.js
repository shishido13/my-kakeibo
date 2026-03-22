export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    // PrimeVueのコンポーネントをスキャン対象に含める
    "./node_modules/primevue/**/*.{vue,js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        canvas: 'var(--app-canvas)',
        surface: 'var(--app-surface)',
        panel: 'var(--app-panel)',
        'panel-strong': 'var(--app-panel-strong)',
        line: 'var(--app-line)',
        'line-strong': 'var(--app-line-strong)',
        ink: 'var(--app-ink)',
        'ink-soft': 'var(--app-ink-soft)',
        muted: 'var(--app-muted)',
        accent: 'var(--app-accent)',
        'accent-strong': 'var(--app-accent-strong)',
        positive: 'var(--app-positive)',
        negative: 'var(--app-negative)'
      },
      fontFamily: {
        sans: ['Noto Sans JP', 'IBM Plex Sans', 'sans-serif'],
        mono: ['IBM Plex Mono', 'monospace']
      },
      boxShadow: {
        hairline: '0 1px 0 rgba(26, 43, 60, 0.03)'
      },
      borderRadius: {
        panel: '14px'
      },
      letterSpacing: {
        dense: '-0.03em'
      }
    },
  },
  plugins: [],
}