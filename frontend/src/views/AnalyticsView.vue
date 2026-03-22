<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAnalyticsStore } from '../stores/analytics';
import { useTransactionStore } from '../stores/transaction';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import Dialog from 'primevue/dialog';
import SelectButton from 'primevue/selectbutton';
import { Pie, Bar } from 'vue-chartjs';
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip
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
  } else {
    const day = date.getDay();
    const diff = date.getDate() - day + (day === 0 ? -6 : 1);
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
    `カテゴリ: ${selectedCategoryIds.value.length === 0 ? 'すべて' : `${selectedCategoryIds.value.length}件`}`
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
    ratio: totalAmount > 0 ? (payer.amount / totalAmount) * 100 : 0
  }));
});

const comparisonTone = computed(() => {
  const percentage = store.summary?.comparison_percentage;
  if (typeof percentage !== 'number') {
    return 'text-muted';
  }

  return percentage > 0 ? 'text-[#7b4f53]' : 'text-[#4f6f5e]';
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

const chartPalette = ['#274863', '#4f6f5e', '#7b4f53', '#7c8b9b', '#5f7489', '#9b7d68', '#3b586f', '#718b7c'];

const pieData = computed(() => {
  if (!store.summary?.categories) return { labels: [], datasets: [] };
  return {
    labels: store.summary.categories.map((category: any) => category.category_name),
    datasets: [{
      data: store.summary.categories.map((category: any) => category.amount),
      backgroundColor: store.summary.categories.map((_: any, index: number) => chartPalette[index % chartPalette.length]),
      borderColor: '#f7f8fa',
      borderWidth: 1
    }]
  };
});

const barData = computed(() => {
  if (!store.trend) return { labels: [], datasets: [] };
  return {
    labels: store.trend.map((item: any) => item.label),
    datasets: [{
      label: '支出額',
      data: store.trend.map((item: any) => item.amount),
      backgroundColor: '#274863',
      borderRadius: 0,
      maxBarThickness: 28
    }]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index' as const,
    intersect: false
  },
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: {
        boxWidth: 10,
        color: '#405468',
        font: {
          size: 10,
          family: 'IBM Plex Sans'
        }
      }
    }
  },
  scales: {
    x: {
      grid: {
        color: '#e3e8ee'
      },
      ticks: {
        color: '#697586',
        font: {
          size: 10,
          family: 'IBM Plex Sans'
        }
      }
    },
    y: {
      grid: {
        color: '#e3e8ee'
      },
      ticks: {
        color: '#697586',
        font: {
          size: 10,
          family: 'IBM Plex Mono'
        }
      }
    }
  }
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('ja-JP', { style: 'currency', currency: 'JPY' }).format(amount);
};

const actionButtonPt = {
  root: { class: 'fin-button rounded-[10px] px-3.5 py-2 flex items-center gap-2 cursor-pointer' },
  label: { class: 'text-[12px] font-semibold tracking-[-0.01em]' },
  icon: { class: 'text-[12px]' }
};

const primaryActionButtonPt = {
  root: { class: 'fin-button fin-button-primary rounded-[10px] px-3.5 py-2 flex items-center gap-2 cursor-pointer' },
  label: { class: 'text-[12px] font-semibold tracking-[-0.01em]' },
  icon: { class: 'text-[12px]' }
};

const periodSwitchPt = {
  root: { class: 'grid grid-cols-3 rounded-[10px] border border-line bg-surface p-1' },
  button: { class: 'rounded-[8px] px-3 py-1.5 text-[12px] font-semibold text-muted transition border-none bg-transparent hover:bg-panel hover:text-ink-soft data-[p-selected=true]:bg-panel data-[p-selected=true]:text-accent-strong' },
  label: { class: 'm-0' }
};

const filterDialogPt = {
  root: { class: 'fin-panel w-[calc(100vw-1.5rem)] max-w-[28rem] overflow-hidden rounded-[16px]' },
  header: { class: 'border-b fin-hairline bg-surface px-5 py-4' },
  title: { class: 'text-[15px] font-semibold tracking-[-0.02em] text-ink' },
  content: { class: 'bg-panel px-5 py-4 space-y-4' }
};

const checkboxPt = {
  root: { class: 'flex items-center' },
  box: { class: 'w-4 h-4 rounded border border-line flex items-center justify-center cursor-pointer data-[p-checked=true]:bg-accent data-[p-checked=true]:border-accent' },
  icon: { class: 'text-white text-[10px]' }
};
</script>

<template>
  <div class="fin-page min-h-screen px-3 py-3 sm:px-5 sm:py-5 lg:px-6">
    <div class="fin-frame flex min-h-[calc(100vh-1.5rem)] flex-col gap-3">
      <section class="fin-panel overflow-hidden rounded-panel">
        <div class="grid gap-4 border-b fin-hairline px-4 py-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-start">
          <div class="space-y-2">
            <div class="flex flex-wrap items-end gap-x-4 gap-y-1">
              <h1 class="fin-title text-[26px] font-semibold leading-none">分析レポート</h1>
              <span class="fin-label">Spending Intelligence</span>
            </div>
            <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-[12px] fin-subtle">
              <span>カテゴリ、時系列、支払者別に支出を確認</span>
              <span class="hidden h-3 w-px bg-line sm:block"></span>
              <span class="fin-value text-[12px] text-ink-soft">{{ selectedDate }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <Button icon="pi pi-arrow-left" label="ダッシュボードへ戻る" @click="router.push('/')" :pt="actionButtonPt" />
          </div>
        </div>

        <div class="grid gap-px bg-line lg:grid-cols-[auto_minmax(0,1fr)_auto]">
          <div class="fin-panel-muted px-4 py-3">
            <div class="fin-label">集計粒度</div>
            <div class="mt-2">
              <SelectButton v-model="periodType" :options="periodOptions" optionLabel="label" optionValue="value" :pt="periodSwitchPt" />
            </div>
          </div>
          <div class="grid gap-px bg-line md:grid-cols-[220px_minmax(0,1fr)]">
            <label class="fin-panel-muted flex flex-col gap-1 px-4 py-3">
              <span class="fin-label">基準日</span>
              <input v-model="selectedDate" type="date" class="fin-input rounded-[10px] px-3 py-2">
            </label>
            <div class="fin-panel-muted hidden px-4 py-3 md:block">
              <div class="fin-label">適用中条件</div>
              <div class="mt-2 flex flex-wrap gap-1.5">
                <span v-for="chip in filterSummaryChips" :key="chip" class="inline-flex items-center rounded-[999px] border border-line bg-panel px-2.5 py-1 text-[10px] font-semibold text-ink-soft">{{ chip }}</span>
              </div>
            </div>
          </div>
          <div class="fin-panel-muted flex items-center justify-between px-4 py-3 lg:justify-center">
            <div>
              <div class="fin-label">絞込</div>
              <div class="mt-1 text-[12px] text-ink-soft">{{ filterCount }}件</div>
            </div>
            <Button icon="pi pi-sliders-h" :label="filterCount > 0 ? `絞り込み ${filterCount}` : '絞り込み'" @click="isMobileFilterOpen = true" :pt="actionButtonPt" />
          </div>
        </div>
      </section>

      <section class="fin-panel rounded-panel px-4 py-4 hidden lg:block">
        <div class="grid gap-3 xl:grid-cols-[170px_170px_minmax(0,1fr)_auto]">
          <label class="flex flex-col gap-1.5">
            <span class="fin-label">支払者</span>
            <select v-model="selectedPayer" class="fin-select rounded-[10px] px-3 py-2">
              <option value="">すべて</option>
              <option v-for="payer in transactionStore.payers" :key="payer.id" :value="payer.name">{{ payer.name }}</option>
            </select>
          </label>
          <label class="flex flex-col gap-1.5">
            <span class="fin-label">支出タイプ</span>
            <select v-model="selectedExpenseTypeId" class="fin-select rounded-[10px] px-3 py-2">
              <option value="">すべて</option>
              <option v-for="expenseType in transactionStore.expenseTypes" :key="expenseType.id" :value="expenseType.id">{{ expenseType.name }}</option>
            </select>
          </label>
          <div class="flex flex-col gap-1.5">
            <span class="fin-label">カテゴリ</span>
            <div class="fin-panel-muted flex items-center justify-between rounded-[10px] px-3 py-2">
              <div>
                <div class="text-[12px] font-semibold text-ink-soft">{{ categoryButtonLabel }}</div>
                <div class="mt-1 text-[11px] text-muted">{{ categorySelectionSummary }}</div>
              </div>
              <Button icon="pi pi-list" label="選択" @click="openCategoryDialog" :pt="actionButtonPt" />
            </div>
          </div>
          <div class="flex items-end justify-end">
            <Button icon="pi pi-refresh" label="フィルタをリセット" @click="resetAllFilters" :pt="actionButtonPt" />
          </div>
        </div>
      </section>

      <section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-[1.45fr_1fr_1fr]">
        <article class="fin-panel-brand rounded-panel px-4 py-4 sm:col-span-2 xl:col-span-1">
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="fin-label">総支出</div>
              <div class="mt-2 fin-value text-[28px] font-semibold text-white">{{ formatCurrency(store.summary?.total_amount || 0) }}</div>
              <div class="mt-1 text-[12px] text-white/80">{{ store.summary?.period_label || '期間を集計中' }}</div>
            </div>
            <div class="text-right">
              <div class="fin-label">カテゴリ数</div>
              <div class="mt-2 fin-value text-[20px] font-semibold text-white">{{ store.summary?.categories?.length || 0 }}</div>
            </div>
          </div>
        </article>

        <article class="fin-panel rounded-panel px-4 py-4">
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="fin-label">前期間比</div>
              <div class="mt-2 text-[24px] font-semibold tracking-[-0.03em]" :class="comparisonTone">
                <template v-if="typeof store.summary?.comparison_percentage === 'number'">
                  {{ store.summary.comparison_percentage > 0 ? '+' : '' }}{{ store.summary.comparison_percentage.toFixed(1) }}%
                </template>
                <template v-else>--</template>
              </div>
              <div class="mt-1 text-[12px] text-muted">前期間との増減率</div>
            </div>
            <div class="rounded-[999px] border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] fin-status-negative">Compare</div>
          </div>
        </article>

        <article class="fin-panel rounded-panel px-4 py-4">
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="fin-label">支払者数</div>
              <div class="mt-2 fin-value text-[24px] font-semibold text-positive">{{ payerBreakdown.length }}</div>
              <div class="mt-1 text-[12px] text-muted">集計対象の支払者</div>
            </div>
            <div class="rounded-[999px] border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] fin-status-positive">Payers</div>
          </div>
        </article>
      </section>

      <section class="fin-panel rounded-panel p-3 lg:hidden">
        <div class="mb-3 flex items-center justify-between gap-3">
          <div>
            <div class="fin-label">Mobile Insight</div>
            <div class="mt-1 text-[14px] font-semibold text-ink">{{ activeInsightTitle }}</div>
          </div>
        </div>
        <div class="grid grid-cols-3 gap-1 rounded-[10px] border border-line bg-surface p-1">
          <button
            v-for="tab in insightTabs"
            :key="tab.value"
            type="button"
            class="rounded-[8px] px-2.5 py-1.5 text-[11px] font-semibold transition"
            :class="activeInsightView === tab.value ? 'bg-panel text-accent-strong' : 'text-muted'"
            @click="activeInsightView = tab.value"
          >
            {{ tab.label }}
          </button>
        </div>

        <div v-if="activeInsightView === 'breakdown'" class="mt-3 fin-panel-muted rounded-[12px] p-3">
          <div class="mb-2 flex items-center justify-between">
            <span class="fin-label">Breakdown</span>
            <span class="text-[12px] text-ink-soft">カテゴリ別支出内訳</span>
          </div>
          <div class="h-[220px]">
            <Pie :data="pieData" :options="chartOptions" />
          </div>
        </div>

        <div v-else-if="activeInsightView === 'trend'" class="mt-3 fin-panel-muted rounded-[12px] p-3">
          <div class="mb-2 flex items-center justify-between">
            <span class="fin-label">Trend</span>
            <span class="text-[12px] text-ink-soft">支出トレンド</span>
          </div>
          <div class="h-[220px]">
            <Bar :data="barData" :options="chartOptions" />
          </div>
        </div>

        <div v-else class="mt-3 space-y-2">
          <div v-for="payer in payerBreakdown" :key="payer.payer" class="fin-panel-muted rounded-[12px] px-3 py-3">
            <div class="flex items-center justify-between gap-3">
              <div>
                <div class="text-[12px] font-semibold text-ink">{{ payer.payer }}</div>
                <div class="mt-1 text-[11px] text-muted">{{ payer.ratio.toFixed(1) }}%</div>
              </div>
              <div class="fin-value text-[14px] font-semibold text-ink">{{ formatCurrency(payer.amount) }}</div>
            </div>
            <div class="mt-2 h-1.5 overflow-hidden rounded-full bg-line">
              <div class="h-full bg-accent" :style="{ width: `${payer.ratio}%` }"></div>
            </div>
          </div>
        </div>
      </section>

      <div class="hidden gap-3 lg:grid lg:grid-cols-2">
        <section class="fin-panel rounded-panel p-4">
          <div class="mb-3 flex items-center justify-between gap-3">
            <div>
              <div class="fin-label">Breakdown</div>
              <h2 class="mt-1 text-[15px] font-semibold text-ink">カテゴリ別支出内訳</h2>
            </div>
            <span class="text-[12px] text-muted">配色は低彩度トーン</span>
          </div>
          <div class="h-[260px] xl:h-[340px]">
            <Pie :data="pieData" :options="chartOptions" />
          </div>
        </section>

        <section class="fin-panel rounded-panel p-4">
          <div class="mb-3 flex items-center justify-between gap-3">
            <div>
              <div class="fin-label">Trend</div>
              <h2 class="mt-1 text-[15px] font-semibold text-ink">支出トレンド</h2>
            </div>
            <span class="text-[12px] text-muted">時系列推移</span>
          </div>
          <div class="h-[260px] xl:h-[340px]">
            <Bar :data="barData" :options="chartOptions" />
          </div>
        </section>
      </div>

      <section class="fin-panel rounded-panel p-4">
        <div class="mb-3 flex items-center justify-between gap-3">
          <div>
            <div class="fin-label">Payers</div>
            <h2 class="mt-1 text-[15px] font-semibold text-ink">支払者別集計</h2>
          </div>
          <span class="text-[12px] text-muted">負担比率と金額</span>
        </div>
        <div class="grid gap-2.5 md:grid-cols-2 xl:grid-cols-3">
          <article v-for="payer in payerBreakdown" :key="payer.payer" class="fin-panel-muted rounded-[12px] px-3 py-3">
            <div class="flex items-start justify-between gap-3">
              <div>
                <div class="fin-label">{{ payer.payer }}</div>
                <div class="mt-2 fin-value text-[20px] font-semibold text-ink">{{ formatCurrency(payer.amount) }}</div>
              </div>
              <span class="rounded-[999px] border border-line bg-panel px-2 py-1 text-[10px] font-semibold text-ink-soft">{{ payer.ratio.toFixed(1) }}%</span>
            </div>
            <div class="mt-3 h-2 overflow-hidden rounded-full bg-line">
              <div class="h-full bg-accent" :style="{ width: `${payer.ratio}%` }"></div>
            </div>
          </article>
        </div>
      </section>
    </div>

    <Dialog :visible="isMobileFilterOpen" modal header="絞り込み" :pt="filterDialogPt" @update:visible="(visible) => { isMobileFilterOpen = visible; }">
      <div class="space-y-4">
        <label class="flex flex-col gap-1.5">
          <span class="fin-label">支払者</span>
          <select v-model="selectedPayer" class="fin-select rounded-[10px] px-3 py-2">
            <option value="">すべて</option>
            <option v-for="payer in transactionStore.payers" :key="payer.id" :value="payer.name">{{ payer.name }}</option>
          </select>
        </label>

        <label class="flex flex-col gap-1.5">
          <span class="fin-label">支出タイプ</span>
          <select v-model="selectedExpenseTypeId" class="fin-select rounded-[10px] px-3 py-2">
            <option value="">すべて</option>
            <option v-for="expenseType in transactionStore.expenseTypes" :key="expenseType.id" :value="expenseType.id">{{ expenseType.name }}</option>
          </select>
        </label>

        <div class="space-y-1.5">
          <span class="fin-label">カテゴリ</span>
          <div class="fin-panel-muted rounded-[10px] px-3 py-3">
            <div class="text-[12px] font-semibold text-ink-soft">{{ categorySelectionSummary }}</div>
            <Button class="mt-2" icon="pi pi-list" :label="categoryButtonLabel" @click="openCategoryDialog" :pt="actionButtonPt" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-2 pt-1">
          <Button icon="pi pi-refresh" label="リセット" @click="resetAllFilters" :pt="actionButtonPt" />
          <Button icon="pi pi-check" label="閉じる" @click="isMobileFilterOpen = false" :pt="primaryActionButtonPt" />
        </div>
      </div>
    </Dialog>

    <Dialog :visible="isCategoryDialogOpen" modal header="カテゴリを選択" :pt="filterDialogPt" @update:visible="(visible) => { isCategoryDialogOpen = visible; }">
      <div class="space-y-4">
        <div class="flex items-center justify-between gap-3 rounded-[10px] border border-line bg-surface px-3 py-2.5">
          <div>
            <p class="fin-label">選択中</p>
            <p class="mt-1 text-[12px] font-semibold text-ink-soft">{{ draftCategoryIds.length === 0 ? 'すべて' : `${draftCategoryIds.length}件` }}</p>
          </div>
          <div class="flex gap-2">
            <Button label="全選択" @click="selectAllCategories" :pt="actionButtonPt" />
            <Button label="クリア" @click="clearDraftCategories" :pt="actionButtonPt" />
          </div>
        </div>

        <div class="grid max-h-[320px] gap-2 overflow-y-auto pr-1">
          <label
            v-for="category in transactionStore.categories"
            :key="category.id"
            class="flex cursor-pointer items-center justify-between rounded-[10px] border px-3 py-3 transition"
            :class="draftCategoryIds.includes(category.id) ? 'border-[color:var(--app-accent)] bg-[var(--app-accent-soft)]' : 'border-line bg-panel hover:border-line-strong hover:bg-surface'"
          >
            <span class="text-[12px] font-semibold text-ink-soft">{{ category.name }}</span>
            <Checkbox v-model="draftCategoryIds" :inputId="`category-${category.id}`" name="categories" :value="category.id" :pt="checkboxPt" />
          </label>
        </div>

        <div class="grid grid-cols-2 gap-2 pt-1">
          <Button label="キャンセル" @click="isCategoryDialogOpen = false" :pt="actionButtonPt" />
          <Button label="適用" icon="pi pi-check" @click="applyCategorySelection" :pt="primaryActionButtonPt" />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<style scoped>
.fin-page :deep(canvas) {
  font-family: 'IBM Plex Sans', 'Noto Sans JP', sans-serif;
}
</style>
