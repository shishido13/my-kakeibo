import PrimeUI from 'tailwindcss-primeui';
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    // PrimeVueのコンポーネントをスキャン対象に含める
    "./node_modules/primevue/**/*.{vue,js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
    },
    plugins: [PrimeUI], // エラーが出るプラグインは一旦空にする
  }
}