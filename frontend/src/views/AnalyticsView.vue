<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAnalyticsStore } from '../stores/analytics';
import Button from 'primevue/button';
import SelectButton from 'primevue/selectbutton';
import { Pie, Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement
} from 'chart.js';

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement
);

const router = useRouter();
const store = useAnalyticsStore();

const periodType = ref('monthly');
const periodOptions = [
  { label: '週次', value: 'weekly' },
  { label: '月次', value: 'monthly' },
  { label: '年次', value: 'yearly' }
];

const selectedDate = ref(new Date().toISOString().split('T')[0]);

const fetchData = async () => {
    let start_date = '';
    let end_date = '';
    const date = new Date(selectedDate.value);

    if (periodType.value === 'monthly') {
        const year = date.getFullYear();
        const month = date.getMonth();
        start_date = new Date(year, month, 1).toISOString().split('T')[0];
        end_date = new Date(year, month + 1, 0).toISOString().split('T')[0];
    } else if (periodType.value === 'yearly') {
        const year = date.getFullYear();
        start_date = `${year}-01-01`;
        end_date = `${year}-12-31`;
    } else { // weekly
        const day = date.getDay();
        const diff = date.getDate() - day + (day === 0 ? -6 : 1); // Monday
        const monday = new Date(selectedDate.value);
        monday.setDate(diff);
        start_date = monday.toISOString().split('T')[0];
        const sunday = new Date(monday);
        sunday.setDate(monday.getDate() + 6);
        end_date = sunday.toISOString().split('T')[0];
    }

    await Promise.all([
        store.fetchSummary({ start_date, end_date, compare: true }),
        store.fetchTrend({ start_date, end_date, group_by: periodType.value === 'yearly' ? 'month' : 'day' })
    ]);
};

onMounted(fetchData);
watch([periodType, selectedDate], fetchData);

const pieData = computed(() => {
    if (!store.summary?.categories) return { labels: [], datasets: [] };
    return {
        labels: store.summary.categories.map((c: any) => c.category_name),
        datasets: [{
            data: store.summary.categories.map((c: any) => c.amount),
            backgroundColor: [
                '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', 
                '#EC4899', '#6B7280', '#06B6D4', '#84CC16', '#F43F5E'
            ]
        }]
    };
});

const barData = computed(() => {
    if (!store.trend) return { labels: [], datasets: [] };
    return {
        labels: store.trend.map((t: any) => t.label),
        datasets: [{
            label: '支出額',
            data: store.trend.map((t: any) => t.amount),
            backgroundColor: '#60A5FA',
            borderRadius: 4
        }]
    };
});

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'bottom' as const,
            labels: { boxWidth: 12, font: { size: 10 } }
        }
    }
};

const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ja-JP', { style: 'currency', currency: 'JPY' }).format(amount);
};
</script>

<template>
  <div class="h-screen bg-gray-50 flex flex-col py-6 px-4 sm:px-8 w-full overflow-hidden">
    <div class="max-w-[1440px] w-full mx-auto flex flex-col h-full">
        
        <!-- Header -->
        <div class="flex justify-between items-center mb-6 border-b border-gray-200 pb-4">
            <div>
                <h1 class="text-2xl font-bold text-gray-900">分析レポート</h1>
                <p class="text-xs text-gray-400 mt-0.5">支出の傾向と内訳を確認します</p>
            </div>
            <Button 
                label="ダッシュボードへ戻る" 
                icon="pi pi-arrow-left" 
                @click="router.push('/')" 
                size="small"
                text
                :pt="{
                    root: { class: 'text-blue-600 hover:text-blue-700 bg-white border border-blue-100 rounded-lg shadow-sm px-4 py-2 text-sm font-medium cursor-pointer' }
                }"
            />
        </div>

        <!-- Controls -->
        <div class="bg-white p-4 rounded-xl border border-gray-200 shadow-sm mb-6 flex flex-wrap gap-4 items-center">
            <SelectButton 
                v-model="periodType" 
                :options="periodOptions" 
                optionLabel="label" 
                optionValue="value" 
                :pt="{
                    root: { class: 'flex bg-gray-100 p-1 rounded-lg' },
                    button: { class: 'px-4 py-1.5 text-xs font-bold rounded-md transition-all border-none bg-transparent hover:bg-gray-200' },
                    label: { class: 'm-0' }
                }"
            />
            <div class="flex items-center gap-2">
                <label class="text-xs font-bold text-gray-400 uppercase tracking-wider">基準日:</label>
                <input type="date" v-model="selectedDate" class="border border-gray-200 rounded px-3 py-1.5 text-sm focus:ring-1 focus:ring-blue-400 outline-none hover:border-gray-300">
            </div>
        </div>

        <!-- Main Content (Grid) -->
        <div class="flex-1 min-h-0 overflow-y-auto pr-2 custom-scrollbar">
            
            <!-- Summary Stats -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <!-- Total Card -->
                <div class="bg-white p-6 rounded-2xl border-l-[6px] border-blue-500 shadow-sm flex flex-col justify-between">
                    <div>
                        <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">期間合計支出</h3>
                        <p class="text-3xl font-black text-gray-900">{{ formatCurrency(store.summary?.total_amount || 0) }}</p>
                    </div>
                </div>

                <!-- MoM/YoY Card -->
                <div class="bg-white p-6 rounded-2xl border-l-[6px] border-purple-500 shadow-sm">
                    <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">前期間比</h3>
                    <div v-if="store.summary?.previous_total_amount" class="flex items-end gap-3">
                        <p class="text-3xl font-black text-gray-900" :class="store.summary.comparison_percentage > 0 ? 'text-red-500' : 'text-green-500'">
                            {{ store.summary.comparison_percentage > 0 ? '+' : '' }}{{ store.summary.comparison_percentage.toFixed(1) }}%
                        </p>
                        <div class="mb-1">
                            <p class="text-[10px] text-gray-400 font-bold uppercase">前期間: {{ formatCurrency(store.summary.previous_total_amount) }}</p>
                            <p class="text-[10px] font-bold" :class="store.summary.comparison_percentage > 0 ? 'text-red-400' : 'text-green-400'">
                                {{ formatCurrency(store.summary.total_amount - store.summary.previous_total_amount) }} {{ store.summary.comparison_percentage > 0 ? '増加' : '減少' }}
                            </p>
                        </div>
                    </div>
                    <p v-else class="text-sm text-gray-400 italic">比較データなし</p>
                </div>

                <!-- Number of Transactions -->
                <div class="bg-white p-6 rounded-2xl border-l-[6px] border-green-500 shadow-sm">
                    <h3 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">取引件数</h3>
                    <p class="text-3xl font-black text-gray-900">{{ store.summary?.categories?.length || 0 }} <span class="text-sm font-medium text-gray-400">カテゴリ</span></p>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <!-- Pie Chart -->
                <div class="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm h-[400px] flex flex-col">
                    <h3 class="text-sm font-bold text-gray-700 mb-4 border-b pb-2">カテゴリ別支出内訳</h3>
                    <div class="flex-1 min-h-0">
                        <Pie :data="pieData" :options="chartOptions" />
                    </div>
                </div>

                <!-- Bar Chart -->
                <div class="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm h-[400px] flex flex-col">
                    <h3 class="text-sm font-bold text-gray-700 mb-4 border-b pb-2">支出トレンド</h3>
                    <div class="flex-1 min-h-0">
                        <Bar :data="barData" :options="chartOptions" />
                    </div>
                </div>
            </div>

            <!-- Payer Breakdown (Bonus but simple) -->
            <div class="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm mb-6">
                <h3 class="text-sm font-bold text-gray-700 mb-4 flex items-center justify-between">
                    <span>支払者別集計</span>
                    <span class="text-[10px] text-gray-400 uppercase tracking-widest">Payer Breakdown</span>
                </h3>
                <div class="flex flex-wrap gap-6">
                    <div v-for="p in store.summary?.payers" :key="p.payer" class="flex-1 min-w-[200px] bg-gray-50 p-4 rounded-xl border border-gray-100">
                        <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">{{ p.payer }}</p>
                        <p class="text-xl font-black text-gray-800">{{ formatCurrency(p.amount) }}</p>
                        <div class="w-full bg-gray-200 h-1.5 rounded-full mt-2 overflow-hidden">
                            <div class="bg-blue-400 h-full rounded-full" :style="{ width: `${(p.amount / store.summary.total_amount) * 100}%` }"></div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #E5E7EB;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #D1D5DB;
}
</style>
