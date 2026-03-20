<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAnalyticsStore } from '../stores/analytics';
import { useTransactionStore } from '../stores/transaction';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import Dialog from 'primevue/dialog';
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
const transactionStore = useTransactionStore();
type InsightView = 'breakdown' | 'trend' | 'payers';

const periodType = ref('monthly');
const periodOptions = [
  { label: '週次', value: 'weekly' },
  { label: '月次', value: 'monthly' },
  { label: '年次', value: 'yearly' }
];
const insightTabs: Array<{ label: string; value: InsightView }> = [
        { label: '内訳', value: 'breakdown' },
        { label: 'トレンド', value: 'trend' },
        { label: '支払者', value: 'payers' }
];

const formatLocalDate = (value: Date) => {
    const year = value.getFullYear();
    const month = `${value.getMonth() + 1}`.padStart(2, '0');
    const day = `${value.getDate()}`.padStart(2, '0');
    return `${year}-${month}-${day}`;
};

const selectedDate = ref(formatLocalDate(new Date()));
const selectedPayer = ref('');
const selectedExpenseTypeId = ref<number | ''>('');
const selectedCategoryIds = ref<number[]>([]);
const draftCategoryIds = ref<number[]>([]);
const activeInsightView = ref<InsightView>('breakdown');
const isMobileFilterOpen = ref(false);
const isCategoryDialogOpen = ref(false);

const fetchData = async () => {
    let start_date = '';
    let end_date = '';
    const date = new Date(selectedDate.value);

    if (periodType.value === 'monthly') {
        const year = date.getFullYear();
        const month = date.getMonth();
        start_date = formatLocalDate(new Date(year, month, 1));
        end_date = formatLocalDate(new Date(year, month + 1, 0));
    } else if (periodType.value === 'yearly') {
        const year = date.getFullYear();
        start_date = `${year}-01-01`;
        end_date = `${year}-12-31`;
    } else { // weekly
        const day = date.getDay();
        const diff = date.getDate() - day + (day === 0 ? -6 : 1); // Monday
        const monday = new Date(selectedDate.value);
        monday.setDate(diff);
        start_date = formatLocalDate(monday);
        const sunday = new Date(monday);
        sunday.setDate(monday.getDate() + 6);
        end_date = formatLocalDate(sunday);
    }

    const filterParams = {
        start_date,
        end_date,
        compare: true,
        ...(selectedPayer.value ? { payer: selectedPayer.value } : {}),
        ...(selectedExpenseTypeId.value ? { expense_type_id: selectedExpenseTypeId.value } : {}),
        ...(selectedCategoryIds.value.length > 0 ? { category_ids: selectedCategoryIds.value } : {})
    };

    await Promise.all([
        store.fetchSummary(filterParams),
        store.fetchTrend({
            ...filterParams,
            group_by: periodType.value === 'yearly' ? 'month' : 'day'
        })
    ]);
};

onMounted(async () => {
    await Promise.all([
        transactionStore.fetchCategories(),
        transactionStore.fetchPayers(),
        transactionStore.fetchExpenseTypes()
    ]);
    await fetchData();
});

watch([periodType, selectedDate, selectedPayer, selectedExpenseTypeId, selectedCategoryIds], fetchData, { deep: true });

const categorySelectionSummary = computed(() => {
    if (selectedCategoryIds.value.length === 0) {
        return 'すべて';
    }

    const names = transactionStore.categories
        .filter((category) => selectedCategoryIds.value.includes(category.id))
        .map((category) => category.name);

    return names.join('、');
});

const categoryButtonLabel = computed(() => {
    if (selectedCategoryIds.value.length === 0) {
        return 'カテゴリを選択';
    }

    const names = transactionStore.categories
        .filter((category) => selectedCategoryIds.value.includes(category.id))
        .map((category) => category.name);

    if (names.length <= 2) {
        return names.join(' / ');
    }

    return `${names.slice(0, 2).join(' / ')} ほか${names.length - 2}件`;
});

const filterSummaryChips = computed(() => {
    return [
        `期間: ${periodType.value === 'weekly' ? '週次' : periodType.value === 'yearly' ? '年次' : '月次'}`,
        `支払者: ${selectedPayer.value || 'すべて'}`,
        `支出タイプ: ${transactionStore.expenseTypes.find((item) => item.id === selectedExpenseTypeId.value)?.name || 'すべて'}`,
        `カテゴリ: ${selectedCategoryIds.value.length === 0 ? 'すべて' : `${selectedCategoryIds.value.length}件`}`,
    ];
});

const filterCount = computed(() => {
    let count = 0;
    if (selectedPayer.value) count += 1;
    if (selectedExpenseTypeId.value) count += 1;
    if (selectedCategoryIds.value.length > 0) count += 1;
    return count;
});

const payerBreakdown = computed(() => {
    const totalAmount = store.summary?.total_amount || 0;
    return (store.summary?.payers || []).map((payer: { payer: string; amount: number }) => ({
        ...payer,
        ratio: totalAmount > 0 ? (payer.amount / totalAmount) * 100 : 0,
    }));
});

const comparisonTone = computed(() => {
    const percentage = store.summary?.comparison_percentage;
    if (typeof percentage !== 'number') {
        return 'text-gray-400';
    }

    return percentage > 0 ? 'text-rose-500' : 'text-emerald-500';
});

const activeInsightTitle = computed(() => {
    if (activeInsightView.value === 'trend') return '支出トレンド';
    if (activeInsightView.value === 'payers') return '支払者別集計';
    return 'カテゴリ別支出内訳';
});

const openCategoryDialog = () => {
    draftCategoryIds.value = [...selectedCategoryIds.value];
    isCategoryDialogOpen.value = true;
};

const applyCategorySelection = () => {
    selectedCategoryIds.value = [...draftCategoryIds.value].sort((left, right) => left - right);
    isCategoryDialogOpen.value = false;
};

const resetAllFilters = () => {
    selectedPayer.value = '';
    selectedExpenseTypeId.value = '';
    selectedCategoryIds.value = [];
    draftCategoryIds.value = [];
};

const selectAllCategories = () => {
    draftCategoryIds.value = transactionStore.categories.map((category) => category.id);
};

const clearDraftCategories = () => {
    draftCategoryIds.value = [];
};

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
    interaction: {
        mode: 'index' as const,
        intersect: false,
    },
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

const filterDialogPt = {
    root: { class: 'bg-white rounded-2xl shadow-2xl w-[calc(100vw-1.5rem)] max-w-[28rem] overflow-hidden' },
    header: { class: 'px-5 py-4 border-b border-gray-100 bg-white' },
    title: { class: 'text-base font-bold text-gray-900' },
    content: { class: 'px-5 py-4 space-y-4' },
};
</script>

<template>
  <div class="min-h-screen bg-[radial-gradient(circle_at_top,_#f8fbff,_#eef3f8_55%,_#e8edf4)] px-2.5 py-3 sm:px-4 lg:px-6">
    <div class="mx-auto flex min-h-[calc(100vh-2rem)] max-w-7xl flex-col">
        <div class="mb-3 rounded-[24px] border border-white/70 bg-white/85 p-3 shadow-[0_20px_60px_rgba(15,23,42,0.07)] backdrop-blur sm:p-4 lg:p-4.5">
            <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div class="space-y-1.5">
                    <div class="inline-flex items-center rounded-full border border-sky-100 bg-sky-50 px-2.5 py-0.5 text-[10px] font-bold tracking-[0.18em] text-sky-700 uppercase">
                        Analytics Report
                    </div>
                    <div>
                        <h1 class="text-[1.7rem] font-black tracking-tight text-slate-900 sm:text-[2rem]">分析レポート</h1>
                        <p class="mt-0.5 text-xs text-slate-500">カテゴリ内訳・トレンド・支払者別を一画面で確認。</p>
                    </div>
                </div>
                <Button
                    label="ダッシュボードへ戻る"
                    icon="pi pi-arrow-left"
                    @click="router.push('/')"
                    text
                    :pt="{
                        root: { class: 'justify-center rounded-xl border border-sky-100 bg-white px-3.5 py-2 text-xs font-semibold text-sky-700 shadow-sm transition hover:border-sky-200 hover:bg-sky-50 lg:self-start' }
                    }"
                />
            </div>

            <div class="mt-3.5 grid gap-2.5 lg:grid-cols-[auto,1fr,auto] lg:items-center">
                <SelectButton
                    v-model="periodType"
                    :options="periodOptions"
                    optionLabel="label"
                    optionValue="value"
                    :pt="{
                        root: { class: 'grid grid-cols-3 rounded-xl bg-slate-100 p-1' },
                        button: { class: 'rounded-lg px-3 py-1.5 text-xs font-bold text-slate-500 transition border-none bg-transparent hover:bg-white hover:text-slate-700 data-[p-selected=true]:bg-white data-[p-selected=true]:text-slate-900 data-[p-selected=true]:shadow-sm' },
                        label: { class: 'm-0' }
                    }"
                />

                <div class="grid gap-2.5 md:grid-cols-[minmax(0,210px),1fr] lg:grid-cols-[minmax(0,220px),1fr]">
                    <label class="flex flex-col gap-1 rounded-xl border border-slate-200 bg-slate-50/80 px-3 py-2">
                        <span class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">基準日</span>
                        <input type="date" v-model="selectedDate" class="w-full bg-transparent text-[13px] font-semibold text-slate-700 outline-none">
                    </label>
                    <div class="hidden min-h-[60px] rounded-xl border border-slate-200 bg-slate-50/80 px-2.5 py-2 md:flex md:flex-wrap md:gap-1.5">
                        <span v-for="chip in filterSummaryChips" :key="chip" class="inline-flex h-fit items-center rounded-full border border-white bg-white px-2.5 py-1 text-[10px] font-bold text-slate-600 shadow-sm">
                            {{ chip }}
                        </span>
                    </div>
                </div>

                <div class="flex items-center gap-2 lg:hidden">
                    <Button
                        icon="pi pi-sliders-h"
                        :label="filterCount > 0 ? `絞り込み ${filterCount}` : '絞り込み'"
                        @click="isMobileFilterOpen = true"
                        :pt="{ root: { class: 'w-full justify-center rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 shadow-sm' } }"
                    />
                </div>
            </div>

            <div class="mt-2.5 flex flex-wrap gap-1.5 md:hidden">
                <span v-for="chip in filterSummaryChips" :key="chip" class="inline-flex items-center rounded-full border border-white bg-slate-100 px-2.5 py-1 text-[10px] font-bold text-slate-600 shadow-sm">
                    {{ chip }}
                </span>
            </div>

            <div class="mt-3 hidden rounded-[20px] border border-slate-200 bg-slate-50/90 p-2.5 lg:block">
                <div class="grid gap-2.5 xl:grid-cols-[minmax(0,170px),minmax(0,170px),minmax(0,1fr),auto]">
                    <label class="flex flex-col gap-1 rounded-xl bg-white px-3 py-2 shadow-sm">
                        <span class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">支払者</span>
                        <select v-model="selectedPayer" class="bg-transparent text-[13px] font-semibold text-slate-700 outline-none">
                            <option value="">すべて</option>
                            <option v-for="payer in transactionStore.payers" :key="payer.id" :value="payer.name">{{ payer.name }}</option>
                        </select>
                    </label>

                    <label class="flex flex-col gap-1 rounded-xl bg-white px-3 py-2 shadow-sm">
                        <span class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">支出タイプ</span>
                        <select v-model="selectedExpenseTypeId" class="bg-transparent text-[13px] font-semibold text-slate-700 outline-none">
                            <option value="">すべて</option>
                            <option v-for="expenseType in transactionStore.expenseTypes" :key="expenseType.id" :value="expenseType.id">{{ expenseType.name }}</option>
                        </select>
                    </label>

                    <div class="rounded-xl bg-white px-3 py-2 shadow-sm">
                        <div class="mb-1 flex items-center justify-between gap-3">
                            <span class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">カテゴリ</span>
                            <span class="text-xs font-semibold text-slate-500">{{ categorySelectionSummary }}</span>
                        </div>
                        <Button
                            :label="categoryButtonLabel"
                            icon="pi pi-list"
                            @click="openCategoryDialog"
                            :pt="{ root: { class: 'w-full justify-start rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-[13px] font-semibold text-slate-700' } }"
                        />
                    </div>

                    <div class="flex items-end justify-end">
                        <Button
                            label="フィルタをリセット"
                            icon="pi pi-refresh"
                            @click="resetAllFilters"
                            text
                            :pt="{ root: { class: 'rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-600 shadow-sm' } }"
                        />
                    </div>
                </div>
            </div>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto pb-2 custom-scrollbar">
            <div class="grid gap-2.5 sm:grid-cols-2 xl:grid-cols-[1.55fr,1fr,1fr]">
                <section class="rounded-[22px] border border-sky-100 bg-[linear-gradient(135deg,_#0f172a,_#1d4ed8_65%,_#38bdf8)] p-3.5 text-white shadow-[0_16px_32px_rgba(37,99,235,0.2)] sm:p-4">
                    <p class="text-[11px] font-bold uppercase tracking-[0.24em] text-sky-100/80">期間合計支出</p>
                    <div class="mt-2.5 flex flex-col gap-2.5 sm:flex-row sm:items-end sm:justify-between">
                        <div>
                            <p class="text-[1.95rem] font-black tracking-tight sm:text-[2.25rem]">{{ formatCurrency(store.summary?.total_amount || 0) }}</p>
                            <p class="mt-0.5 text-xs text-sky-100/80">{{ store.summary?.period_label || '期間を集計中' }}</p>
                        </div>
                        <div class="grid grid-cols-2 gap-2 text-left sm:w-[200px]">
                            <div class="rounded-xl bg-white/12 px-3 py-2 backdrop-blur">
                                <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-sky-100/70">カテゴリ</p>
                                <p class="mt-0.5 text-base font-black text-white">{{ store.summary?.categories?.length || 0 }}</p>
                            </div>
                            <div class="rounded-xl bg-white/12 px-3 py-2 backdrop-blur">
                                <p class="text-[10px] font-bold uppercase tracking-[0.18em] text-sky-100/70">支払者</p>
                                <p class="mt-0.5 text-base font-black text-white">{{ payerBreakdown.length }}</p>
                            </div>
                        </div>
                    </div>
                </section>

                <section class="rounded-[20px] border border-rose-100 bg-white p-3.5 shadow-sm sm:p-4">
                    <div class="flex items-start justify-between gap-3">
                        <div>
                            <p class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">前期間比</p>
                            <p class="mt-1 text-xs text-slate-500">前期間との増減</p>
                        </div>
                        <div class="rounded-full bg-rose-50 px-2.5 py-1 text-[11px] font-bold text-rose-500">Compare</div>
                    </div>
                    <div v-if="store.summary?.previous_total_amount" class="mt-3 space-y-1.5">
                        <p class="text-[1.8rem] font-black tracking-tight" :class="comparisonTone">
                            {{ store.summary.comparison_percentage > 0 ? '+' : '' }}{{ store.summary.comparison_percentage.toFixed(1) }}%
                        </p>
                        <p class="text-xs font-semibold text-slate-500">前期間 {{ formatCurrency(store.summary.previous_total_amount) }}</p>
                        <p class="text-xs font-semibold" :class="comparisonTone">
                            {{ formatCurrency(store.summary.total_amount - store.summary.previous_total_amount) }}
                            {{ store.summary.comparison_percentage > 0 ? '増加' : '減少' }}
                        </p>
                    </div>
                    <p v-else class="mt-3 text-xs italic text-slate-400">比較データなし</p>
                </section>

                <section class="rounded-[20px] border border-emerald-100 bg-white p-3.5 shadow-sm sm:p-4">
                    <div class="flex items-start justify-between gap-3">
                        <div>
                            <p class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">適用中フィルタ</p>
                            <p class="mt-1 text-xs text-slate-500">現在の集計条件</p>
                        </div>
                        <div class="rounded-full bg-emerald-50 px-2.5 py-1 text-[11px] font-bold text-emerald-600">{{ filterCount }}件</div>
                    </div>
                    <div class="mt-3 flex flex-wrap gap-1.5">
                        <span v-for="chip in filterSummaryChips" :key="chip" class="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-bold text-slate-600">
                            {{ chip }}
                        </span>
                    </div>
                </section>
            </div>

            <section class="mt-3 rounded-[22px] border border-white/70 bg-white/90 p-2.5 shadow-[0_16px_40px_rgba(15,23,42,0.07)] backdrop-blur sm:p-3 lg:hidden">
                <div class="mb-2.5 flex items-center justify-between gap-3">
                    <div>
                        <h2 class="text-sm font-black text-slate-900">{{ activeInsightTitle }}</h2>
                        <p class="text-[11px] text-slate-500">視点を切替</p>
                    </div>
                </div>
                <div class="mb-2.5 grid grid-cols-3 rounded-xl bg-slate-100 p-1">
                    <button
                        v-for="tab in insightTabs"
                        :key="tab.value"
                        type="button"
                        class="rounded-lg px-2.5 py-1.5 text-[11px] font-bold transition"
                        :class="activeInsightView === tab.value ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500'"
                        @click="activeInsightView = tab.value"
                    >
                        {{ tab.label }}
                    </button>
                </div>

                <div v-if="activeInsightView === 'breakdown'" class="rounded-[18px] border border-slate-100 bg-slate-50 p-2.5">
                    <div class="mb-2 flex items-center justify-between">
                        <span class="text-xs font-bold text-slate-700">カテゴリ別支出内訳</span>
                        <span class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">Breakdown</span>
                    </div>
                    <div class="h-[220px]">
                        <Pie :data="pieData" :options="chartOptions" />
                    </div>
                </div>

                <div v-else-if="activeInsightView === 'trend'" class="rounded-[18px] border border-slate-100 bg-slate-50 p-2.5">
                    <div class="mb-2 flex items-center justify-between">
                        <span class="text-xs font-bold text-slate-700">支出トレンド</span>
                        <span class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">Trend</span>
                    </div>
                    <div class="h-[220px]">
                        <Bar :data="barData" :options="chartOptions" />
                    </div>
                </div>

                <div v-else class="space-y-1.5">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-slate-700">支払者別集計</span>
                        <span class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">Payers</span>
                    </div>
                    <div v-for="payer in payerBreakdown" :key="payer.payer" class="rounded-[16px] border border-slate-100 bg-slate-50 px-3 py-2.5">
                        <div class="flex items-center justify-between gap-3">
                            <div>
                                <p class="text-[13px] font-black text-slate-800">{{ payer.payer }}</p>
                                <p class="text-[11px] text-slate-500">{{ payer.ratio.toFixed(1) }}%</p>
                            </div>
                            <p class="text-sm font-black text-slate-900">{{ formatCurrency(payer.amount) }}</p>
                        </div>
                        <div class="mt-1.5 h-1.5 overflow-hidden rounded-full bg-slate-200">
                            <div class="h-full rounded-full bg-[linear-gradient(90deg,_#0ea5e9,_#2563eb)]" :style="{ width: `${payer.ratio}%` }"></div>
                        </div>
                    </div>
                </div>
            </section>

            <div class="mt-3 hidden gap-3 lg:grid lg:grid-cols-2">
                <section class="rounded-[22px] border border-white/70 bg-white/90 p-4 shadow-[0_16px_40px_rgba(15,23,42,0.07)] backdrop-blur">
                    <div class="mb-3 flex items-center justify-between gap-3">
                        <div>
                            <h2 class="text-base font-black text-slate-900">カテゴリ別支出内訳</h2>
                            <p class="text-xs text-slate-500">選択中カテゴリだけで再計算。</p>
                        </div>
                        <span class="rounded-full bg-sky-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-sky-600">Breakdown</span>
                    </div>
                    <div class="h-[280px] xl:h-[320px]">
                        <Pie :data="pieData" :options="chartOptions" />
                    </div>
                </section>

                <section class="rounded-[22px] border border-white/70 bg-white/90 p-4 shadow-[0_16px_40px_rgba(15,23,42,0.07)] backdrop-blur">
                    <div class="mb-3 flex items-center justify-between gap-3">
                        <div>
                            <h2 class="text-base font-black text-slate-900">支出トレンド</h2>
                            <p class="text-xs text-slate-500">現在の条件だけで時系列を描画。</p>
                        </div>
                        <span class="rounded-full bg-indigo-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-indigo-600">Trend</span>
                    </div>
                    <div class="h-[280px] xl:h-[320px]">
                        <Bar :data="barData" :options="chartOptions" />
                    </div>
                </section>
            </div>

            <section class="mt-3 rounded-[22px] border border-white/70 bg-white/90 p-3.5 shadow-[0_16px_40px_rgba(15,23,42,0.07)] backdrop-blur sm:p-4">
                <div class="mb-3 flex items-center justify-between gap-3">
                    <div>
                        <h2 class="text-base font-black text-slate-900">支払者別集計</h2>
                        <p class="text-xs text-slate-500">支払者ごとの負担比率と金額。</p>
                    </div>
                    <span class="rounded-full bg-emerald-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-emerald-600">Payers</span>
                </div>
                <div class="grid gap-2.5 md:grid-cols-2 xl:grid-cols-3">
                    <article v-for="payer in payerBreakdown" :key="payer.payer" class="rounded-[18px] border border-slate-100 bg-[linear-gradient(180deg,_#ffffff,_#f8fafc)] p-3 shadow-sm">
                        <div class="flex items-start justify-between gap-2.5">
                            <div>
                                <p class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">{{ payer.payer }}</p>
                                <p class="mt-1.5 text-xl font-black tracking-tight text-slate-900">{{ formatCurrency(payer.amount) }}</p>
                            </div>
                            <span class="rounded-full bg-slate-100 px-2 py-1 text-[11px] font-bold text-slate-600">{{ payer.ratio.toFixed(1) }}%</span>
                        </div>
                        <div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-200">
                            <div class="h-full rounded-full bg-[linear-gradient(90deg,_#14b8a6,_#2563eb)]" :style="{ width: `${payer.ratio}%` }"></div>
                        </div>
                    </article>
                </div>
            </section>
        </div>
    </div>

    <Dialog
        :visible="isMobileFilterOpen"
        modal
        header="絞り込み"
        :pt="filterDialogPt"
        @update:visible="(visible) => { isMobileFilterOpen = visible; }"
    >
        <div class="space-y-4">
            <label class="flex flex-col gap-1.5 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5">
                <span class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">支払者</span>
                <select v-model="selectedPayer" class="bg-transparent text-sm font-semibold text-slate-700 outline-none">
                    <option value="">すべて</option>
                    <option v-for="payer in transactionStore.payers" :key="payer.id" :value="payer.name">{{ payer.name }}</option>
                </select>
            </label>

            <label class="flex flex-col gap-1.5 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5">
                <span class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">支出タイプ</span>
                <select v-model="selectedExpenseTypeId" class="bg-transparent text-sm font-semibold text-slate-700 outline-none">
                    <option value="">すべて</option>
                    <option v-for="expenseType in transactionStore.expenseTypes" :key="expenseType.id" :value="expenseType.id">{{ expenseType.name }}</option>
                </select>
            </label>

            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-3 py-3">
                <div class="mb-2 flex items-center justify-between gap-3">
                    <span class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">カテゴリ</span>
                    <span class="text-xs font-semibold text-slate-500">{{ categorySelectionSummary }}</span>
                </div>
                <Button
                    :label="categoryButtonLabel"
                    icon="pi pi-list"
                    @click="openCategoryDialog"
                    :pt="{ root: { class: 'w-full justify-start rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700' } }"
                />
            </div>

            <div class="grid grid-cols-2 gap-2 pt-1">
                <Button
                    label="リセット"
                    icon="pi pi-refresh"
                    @click="resetAllFilters"
                    text
                    :pt="{ root: { class: 'justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-600' } }"
                />
                <Button
                    label="閉じる"
                    icon="pi pi-check"
                    @click="isMobileFilterOpen = false"
                    :pt="{ root: { class: 'justify-center rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white' } }"
                />
            </div>
        </div>
    </Dialog>

    <Dialog
        :visible="isCategoryDialogOpen"
        modal
        header="カテゴリを選択"
        :pt="filterDialogPt"
        @update:visible="(visible) => { isCategoryDialogOpen = visible; }"
    >
        <div class="space-y-4">
            <div class="flex items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5">
                <div>
                    <p class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">選択中</p>
                    <p class="mt-1 text-sm font-semibold text-slate-700">{{ draftCategoryIds.length === 0 ? 'すべて' : `${draftCategoryIds.length}件` }}</p>
                </div>
                <div class="flex gap-2">
                    <Button
                        label="全選択"
                        @click="selectAllCategories"
                        text
                        :pt="{ root: { class: 'rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600' } }"
                    />
                    <Button
                        label="クリア"
                        @click="clearDraftCategories"
                        text
                        :pt="{ root: { class: 'rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600' } }"
                    />
                </div>
            </div>

            <div class="grid max-h-[320px] gap-2 overflow-y-auto pr-1">
                <label
                    v-for="category in transactionStore.categories"
                    :key="category.id"
                    class="flex cursor-pointer items-center justify-between rounded-2xl border border-slate-200 px-3 py-3 transition hover:border-sky-200 hover:bg-sky-50/60"
                    :class="draftCategoryIds.includes(category.id) ? 'border-sky-200 bg-sky-50/70' : 'bg-white'"
                >
                    <span class="text-sm font-semibold text-slate-700">{{ category.name }}</span>
                    <Checkbox v-model="draftCategoryIds" :inputId="`category-${category.id}`" name="categories" :value="category.id" />
                </label>
            </div>

            <div class="grid grid-cols-2 gap-2 pt-1">
                <Button
                    label="キャンセル"
                    @click="isCategoryDialogOpen = false"
                    text
                    :pt="{ root: { class: 'justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-600' } }"
                />
                <Button
                    label="適用"
                    icon="pi pi-check"
                    @click="applyCategorySelection"
                    :pt="{ root: { class: 'justify-center rounded-2xl bg-sky-600 px-4 py-2.5 text-sm font-semibold text-white' } }"
                />
            </div>
        </div>
    </Dialog>
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
