<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import Button from 'primevue/button';
import SelectButton from 'primevue/selectbutton';
import api from '../services/api';
import { useTransactionStore, type TransactionRecord } from '../stores/transaction';

type AllocationMode = 'percentage' | 'amount';

interface CategoryTotal {
  categoryId: number;
  categoryName: string;
  totalAmount: number;
  transactionCount: number;
}

interface AllocationState {
  mode: AllocationMode;
  shares: Record<string, number | ''>;
}

interface CategoryAllocationSummary {
  categoryId: number;
  categoryName: string;
  totalAmount: number;
  transactionCount: number;
  mode: AllocationMode;
  inputTotal: number;
  expectedTotal: number;
  isValid: boolean;
  helperText: string;
  burdenByPayer: Record<string, number>;
}

interface SettlementTransfer {
  from: string;
  to: string;
  amount: number;
}

const router = useRouter();
const transactionStore = useTransactionStore();

const modeOptions = [
  { label: '％', value: 'percentage' },
  { label: '金額', value: 'amount' },
];

const selectedMonth = ref(formatMonthInput(new Date()));
const monthlyTransactions = ref<TransactionRecord[]>([]);
const allocations = ref<Record<number, AllocationState>>({});
const isLoading = ref(false);
const loadError = ref('');

function formatMonthInput(value: Date) {
  const year = value.getFullYear();
  const month = `${value.getMonth() + 1}`.padStart(2, '0');
  return `${year}-${month}`;
}

function formatLocalDate(value: Date) {
  const year = value.getFullYear();
  const month = `${value.getMonth() + 1}`.padStart(2, '0');
  const day = `${value.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function getMonthRange(monthValue: string) {
  const [yearText, monthText] = monthValue.split('-');
  const year = Number(yearText);
  const month = Number(monthText) - 1;
  const start = new Date(year, month, 1);
  const end = new Date(year, month + 1, 0);

  return {
    startDate: formatLocalDate(start),
    endDate: formatLocalDate(end),
    label: `${year}年${month + 1}月`,
  };
}

function roundToOneDecimal(value: number) {
  return Math.round(value * 10) / 10;
}

function buildEqualPercentageShares(payerNames: string[]) {
  const nextShares: Record<string, number> = {};

  if (payerNames.length === 0) {
    return nextShares;
  }

  let remaining = 100;
  payerNames.forEach((payer, index) => {
    if (index === payerNames.length - 1) {
      nextShares[payer] = roundToOneDecimal(remaining);
      return;
    }

    const share = roundToOneDecimal(100 / payerNames.length);
    nextShares[payer] = share;
    remaining = roundToOneDecimal(remaining - share);
  });

  return nextShares;
}

function toNumber(value: number | '') {
  return typeof value === 'number' && Number.isFinite(value) ? value : 0;
}

function createZeroAmountMap(names: string[]) {
  const values: Record<string, number> = {};

  names.forEach((name) => {
    values[name] = 0;
  });

  return values;
}

function createRoundedAmountMap(entries: Array<{ payer: string; value: number }>) {
  const values: Record<string, number> = {};

  entries.forEach(({ payer, value }) => {
    values[payer] = Math.round(value);
  });

  return values;
}

const payerNames = computed(() => {
  const names = new Set<string>();

  transactionStore.payers.forEach((payer) => names.add(payer.name));
  monthlyTransactions.value.forEach((transaction) => {
    if (transaction.payer) {
      names.add(transaction.payer);
    }
  });

  return Array.from(names);
});

const commonExpenseTypeId = computed(() => {
  return transactionStore.expenseTypes.find((expenseType) => expenseType.name === '共通')?.id ?? 1;
});

const monthRange = computed(() => getMonthRange(selectedMonth.value));

const categoryTotals = computed<CategoryTotal[]>(() => {
  const categoryMap = new Map<number, CategoryTotal>();
  const categoryNameById = new Map(transactionStore.categories.map((category) => [category.id, category.name]));

  monthlyTransactions.value.forEach((transaction) => {
    const current = categoryMap.get(transaction.category_id);
    if (current) {
      current.totalAmount += transaction.amount;
      current.transactionCount += 1;
      return;
    }

    categoryMap.set(transaction.category_id, {
      categoryId: transaction.category_id,
      categoryName: categoryNameById.get(transaction.category_id) ?? `カテゴリ ${transaction.category_id}`,
      totalAmount: transaction.amount,
      transactionCount: 1,
    });
  });

  return Array.from(categoryMap.values()).sort((left, right) => right.totalAmount - left.totalAmount);
});

function syncAllocations() {
  const nextState: Record<number, AllocationState> = {};

  categoryTotals.value.forEach((category) => {
    const existing = allocations.value[category.categoryId];

    if (!existing) {
      nextState[category.categoryId] = {
        mode: 'percentage',
        shares: buildEqualPercentageShares(payerNames.value),
      };
      return;
    }

    const nextShares: Record<string, number | ''> = {};
    payerNames.value.forEach((payer) => {
      nextShares[payer] = existing.shares[payer] ?? (existing.mode === 'percentage' ? 0 : '');
    });

    nextState[category.categoryId] = {
      mode: existing.mode,
      shares: nextShares,
    };
  });

  allocations.value = nextState;
}

function apportionByPercentage(totalAmount: number, shares: Array<{ payer: string; share: number }>) {
  const burdens = createZeroAmountMap(shares.map(({ payer }) => payer));
  const rawAllocations = shares.map(({ payer, share }) => {
    const rawAmount = (totalAmount * share) / 100;
    const floored = Math.floor(rawAmount);
    return {
      payer,
      floored,
      remainder: rawAmount - floored,
    };
  });

  let remaining = totalAmount - rawAllocations.reduce((sum, current) => sum + current.floored, 0);

  rawAllocations
    .sort((left, right) => right.remainder - left.remainder)
    .forEach((entry, index) => {
      burdens[entry.payer] = entry.floored + (index < remaining ? 1 : 0);
    });

  return burdens;
}

const categoryAllocationSummaries = computed<CategoryAllocationSummary[]>(() => {
  return categoryTotals.value.map((category) => {
    const allocation = allocations.value[category.categoryId] ?? {
      mode: 'percentage',
      shares: buildEqualPercentageShares(payerNames.value),
    };

    const rawInputs = payerNames.value.map((payer) => ({
      payer,
      value: toNumber(allocation.shares[payer] ?? ''),
    }));

    const inputTotal = rawInputs.reduce((sum, current) => sum + current.value, 0);
    const expectedTotal = allocation.mode === 'percentage' ? 100 : category.totalAmount;
    const tolerance = allocation.mode === 'percentage' ? 0.11 : 0.5;
    const isValid = Math.abs(inputTotal - expectedTotal) <= tolerance;

    const burdenByPayer = allocation.mode === 'percentage'
      ? apportionByPercentage(
          category.totalAmount,
          rawInputs.map(({ payer, value }) => ({ payer, share: value })),
        )
      : createRoundedAmountMap(rawInputs);

    return {
      categoryId: category.categoryId,
      categoryName: category.categoryName,
      totalAmount: category.totalAmount,
      transactionCount: category.transactionCount,
      mode: allocation.mode,
      inputTotal,
      expectedTotal,
      isValid,
      helperText: allocation.mode === 'percentage'
        ? `合計が100%になるように入力してください。現在 ${inputTotal.toFixed(1)}%`
        : `合計がカテゴリ支出額と一致するように入力してください。現在 ${formatCurrency(Math.round(inputTotal))}`,
      burdenByPayer,
    };
  });
});

const isAllocationValid = computed(() => {
  return categoryAllocationSummaries.value.length > 0 && categoryAllocationSummaries.value.every((summary) => summary.isValid);
});

const totalCommonExpense = computed(() => {
  return categoryTotals.value.reduce((sum, category) => sum + category.totalAmount, 0);
});

const actualPaidByPayer = computed(() => {
  const paid = createZeroAmountMap(payerNames.value);

  monthlyTransactions.value.forEach((transaction) => {
    paid[transaction.payer] = (paid[transaction.payer] ?? 0) + transaction.amount;
  });

  return paid;
});

const finalBurdenByPayer = computed(() => {
  const burden = createZeroAmountMap(payerNames.value);

  categoryAllocationSummaries.value.forEach((summary) => {
    payerNames.value.forEach((payer) => {
      burden[payer] = (burden[payer] ?? 0) + (summary.burdenByPayer[payer] ?? 0);
    });
  });

  return burden;
});

const payerSettlementRows = computed(() => {
  return payerNames.value.map((payer) => {
    const paid = actualPaidByPayer.value[payer] ?? 0;
    const burden = finalBurdenByPayer.value[payer] ?? 0;
    const difference = paid - burden;

    return {
      payer,
      paid,
      burden,
      difference,
      status: difference > 0 ? '受取' : difference < 0 ? '支払' : '精算不要',
    };
  });
});

const settlementTransfers = computed<SettlementTransfer[]>(() => {
  if (!isAllocationValid.value) {
    return [];
  }

  const creditors = payerSettlementRows.value
    .filter((row) => row.difference > 0)
    .map((row) => ({ payer: row.payer, amount: row.difference }));
  const debtors = payerSettlementRows.value
    .filter((row) => row.difference < 0)
    .map((row) => ({ payer: row.payer, amount: Math.abs(row.difference) }));

  const transfers: SettlementTransfer[] = [];
  let creditorIndex = 0;
  let debtorIndex = 0;

  while (creditorIndex < creditors.length && debtorIndex < debtors.length) {
    const transferAmount = Math.min(creditors[creditorIndex].amount, debtors[debtorIndex].amount);
    const roundedTransfer = Math.round(transferAmount);

    if (roundedTransfer > 0) {
      transfers.push({
        from: debtors[debtorIndex].payer,
        to: creditors[creditorIndex].payer,
        amount: roundedTransfer,
      });
    }

    creditors[creditorIndex].amount -= roundedTransfer;
    debtors[debtorIndex].amount -= roundedTransfer;

    if (creditors[creditorIndex].amount <= 0) {
      creditorIndex += 1;
    }

    if (debtors[debtorIndex].amount <= 0) {
      debtorIndex += 1;
    }
  }

  return transfers;
});

async function fetchMonthlyTransactions() {
  isLoading.value = true;
  loadError.value = '';

  try {
    const response = await api.get('/transactions/', {
      params: {
        start_date: monthRange.value.startDate,
        end_date: monthRange.value.endDate,
        expense_type_id: commonExpenseTypeId.value,
        limit: 1000,
      },
    });

    monthlyTransactions.value = response.data;
    syncAllocations();
  } catch (error) {
    console.error(error);
    loadError.value = '対象月の共通支出を取得できませんでした。';
    monthlyTransactions.value = [];
    allocations.value = {};
  } finally {
    isLoading.value = false;
  }
}

function updateShare(categoryId: number, payer: string, value: string) {
  const state = allocations.value[categoryId];
  if (!state) {
    return;
  }

  const trimmedValue = value.trim();
  if (!trimmedValue) {
    state.shares[payer] = '';
    return;
  }

  const nextValue = Number(trimmedValue);
  state.shares[payer] = Number.isFinite(nextValue) ? nextValue : '';
}

function handleShareInput(categoryId: number, payer: string, event: Event) {
  const target = event.target as HTMLInputElement | null;
  updateShare(categoryId, payer, target?.value ?? '');
}

function updateAllocationMode(categoryId: number, nextMode: AllocationMode, totalAmount: number) {
  const state = allocations.value[categoryId];
  if (!state || state.mode === nextMode) {
    return;
  }

  const payerShareValues = payerNames.value.map((payer) => ({
    payer,
    value: toNumber(state.shares[payer] ?? ''),
  }));

  const nextShares: Record<string, number | ''> = {};

  if (nextMode === 'amount') {
    const burdens = apportionByPercentage(
      totalAmount,
      payerShareValues.map(({ payer, value }) => ({ payer, share: value })),
    );
    payerNames.value.forEach((payer) => {
      nextShares[payer] = burdens[payer] ?? 0;
    });
  } else {
    const total = payerShareValues.reduce((sum, entry) => sum + entry.value, 0) || totalAmount;
    payerNames.value.forEach((payer) => {
      const amount = toNumber(state.shares[payer] ?? '');
      nextShares[payer] = total > 0 ? roundToOneDecimal((amount / total) * 100) : 0;
    });
  }

  allocations.value[categoryId] = {
    mode: nextMode,
    shares: nextShares,
  };
}

function applyEqualSplit(categoryId: number, totalAmount: number) {
  const state = allocations.value[categoryId];
  if (!state) {
    return;
  }

  if (state.mode === 'percentage') {
    state.shares = buildEqualPercentageShares(payerNames.value);
    return;
  }

  const equalAmount = payerNames.value.length > 0 ? Math.floor(totalAmount / payerNames.value.length) : 0;
  let remaining = totalAmount;
  const nextShares: Record<string, number> = {};

  payerNames.value.forEach((payer, index) => {
    if (index === payerNames.value.length - 1) {
      nextShares[payer] = remaining;
      return;
    }

    nextShares[payer] = equalAmount;
    remaining -= equalAmount;
  });

  state.shares = nextShares;
}

onMounted(async () => {
  await Promise.all([
    transactionStore.fetchCategories(),
    transactionStore.fetchPayers(),
    transactionStore.fetchExpenseTypes(),
  ]);

  await fetchMonthlyTransactions();
});

watch([selectedMonth, commonExpenseTypeId], async () => {
  if (transactionStore.expenseTypes.length === 0) {
    return;
  }

  await fetchMonthlyTransactions();
});

watch([categoryTotals, payerNames], () => {
  syncAllocations();
});

function formatCurrency(amount: number) {
  return new Intl.NumberFormat('ja-JP', { style: 'currency', currency: 'JPY' }).format(amount);
}
</script>

<template>
  <div class="min-h-screen bg-[radial-gradient(circle_at_top,_#f7fbff,_#eef5fb_48%,_#e9edf5)] px-3 py-4 sm:px-5 lg:px-8">
    <div class="mx-auto flex max-w-7xl flex-col gap-3">
      <section class="rounded-[24px] border border-white/70 bg-white/90 p-4 shadow-[0_20px_60px_rgba(15,23,42,0.08)] backdrop-blur sm:p-5">
        <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div class="space-y-1.5">
            <div class="inline-flex items-center rounded-full border border-emerald-100 bg-emerald-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-emerald-700">
              Settlement Planner
            </div>
            <div>
              <h1 class="text-[1.8rem] font-black tracking-tight text-slate-900 sm:text-[2.1rem]">精算額計算</h1>
              <p class="mt-0.5 text-xs text-slate-500">月次の共通支出をもとに、カテゴリ別の最終負担額と受け渡し先を計算します。</p>
            </div>
          </div>

          <Button
            label="ダッシュボードへ戻る"
            icon="pi pi-arrow-left"
            text
            @click="router.push('/')"
            :pt="{
              root: { class: 'justify-center rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-50' }
            }"
          />
        </div>

        <div class="mt-3 grid gap-2.5 lg:grid-cols-[280px,1fr] lg:items-center">
          <label class="flex flex-col gap-1 rounded-xl border border-slate-200 bg-slate-50/90 px-3 py-2.5">
            <span class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">対象月</span>
            <input v-model="selectedMonth" type="month" class="bg-transparent text-sm font-semibold text-slate-700 outline-none">
          </label>

          <div class="grid gap-2 sm:grid-cols-3">
            <article class="rounded-xl border border-slate-100 bg-slate-50 px-3 py-2.5">
              <p class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">集計期間</p>
              <p class="mt-1 text-sm font-bold text-slate-900">{{ monthRange.label }}</p>
              <p class="mt-0.5 text-[11px] text-slate-500">{{ monthRange.startDate }} 〜 {{ monthRange.endDate }}</p>
            </article>
            <article class="rounded-xl border border-slate-100 bg-slate-50 px-3 py-2.5">
              <p class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">対象支出</p>
              <p class="mt-1 text-sm font-bold text-slate-900">共通のみ</p>
              <p class="mt-0.5 text-[11px] text-slate-500">{{ monthlyTransactions.length }}件の取引</p>
            </article>
            <article class="rounded-xl border border-slate-100 bg-slate-50 px-3 py-2.5">
              <p class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">共通支出合計</p>
              <p class="mt-1 text-sm font-bold text-slate-900">{{ formatCurrency(totalCommonExpense) }}</p>
              <p class="mt-0.5 text-[11px] text-slate-500">{{ categoryTotals.length }}カテゴリ</p>
            </article>
          </div>
        </div>
      </section>

      <div v-if="loadError" class="rounded-[20px] border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600">
        {{ loadError }}
      </div>

      <div v-if="isLoading" class="rounded-[20px] border border-white/70 bg-white/90 px-4 py-10 text-center text-sm font-semibold text-slate-500 shadow-sm">
        共通支出データを読み込み中です。
      </div>

      <template v-else>
        <div v-if="categoryTotals.length === 0" class="rounded-[20px] border border-white/70 bg-white/90 px-4 py-10 text-center text-sm font-semibold text-slate-500 shadow-sm">
          この月の共通支出は見つかりませんでした。
        </div>

        <template v-else>
          <section class="rounded-[24px] border border-white/70 bg-white/90 p-3 shadow-[0_16px_40px_rgba(15,23,42,0.07)] backdrop-blur sm:p-4">
            <div class="mb-3 flex items-center justify-between gap-3">
              <div>
                <h2 class="text-base font-black text-slate-900">カテゴリ別負担設定</h2>
                <p class="text-xs text-slate-500">各カテゴリごとに、支払者別の負担割合を％または金額で入力します。</p>
              </div>
              <span class="rounded-full bg-amber-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-amber-700">
                {{ payerNames.length }} payers
              </span>
            </div>

            <div class="space-y-3">
              <article v-for="summary in categoryAllocationSummaries" :key="summary.categoryId" class="rounded-[20px] border border-slate-100 bg-[linear-gradient(180deg,_#ffffff,_#f8fafc)] p-3.5 shadow-sm">
                <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <div class="flex flex-wrap items-center gap-2">
                      <h3 class="text-sm font-black text-slate-900">{{ summary.categoryName }}</h3>
                      <span class="rounded-full bg-sky-50 px-2 py-1 text-[10px] font-bold text-sky-700">{{ formatCurrency(summary.totalAmount) }}</span>
                      <span class="rounded-full bg-slate-100 px-2 py-1 text-[10px] font-bold text-slate-500">{{ summary.transactionCount }}件</span>
                    </div>
                    <p class="mt-1 text-[11px]" :class="summary.isValid ? 'text-emerald-600' : 'text-rose-500'">
                      {{ summary.helperText }}
                    </p>
                  </div>

                  <div class="flex items-center gap-2">
                    <SelectButton
                      :modelValue="summary.mode"
                      :options="modeOptions"
                      optionLabel="label"
                      optionValue="value"
                      @update:modelValue="(value) => updateAllocationMode(summary.categoryId, value, summary.totalAmount)"
                      :pt="{
                        root: { class: 'grid grid-cols-2 rounded-xl bg-slate-100 p-1' },
                        button: { class: 'rounded-lg px-3 py-1.5 text-xs font-bold text-slate-500 transition border-none bg-transparent hover:bg-white hover:text-slate-700 data-[p-selected=true]:bg-white data-[p-selected=true]:text-slate-900 data-[p-selected=true]:shadow-sm' },
                        label: { class: 'm-0' }
                      }"
                    />
                    <Button
                      label="等分"
                      icon="pi pi-percentage"
                      text
                      @click="applyEqualSplit(summary.categoryId, summary.totalAmount)"
                      :pt="{ root: { class: 'rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 shadow-sm' } }"
                    />
                  </div>
                </div>

                <div class="mt-3 grid gap-2 md:grid-cols-2 xl:grid-cols-4">
                  <label v-for="payer in payerNames" :key="`${summary.categoryId}-${payer}`" class="rounded-xl border border-slate-200 bg-white px-3 py-2 shadow-sm">
                    <span class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">{{ payer }}</span>
                    <div class="mt-1.5 flex items-end gap-2">
                      <input
                        :value="allocations[summary.categoryId]?.shares[payer] ?? ''"
                        type="number"
                        min="0"
                        :step="summary.mode === 'percentage' ? '0.1' : '1'"
                        class="w-full bg-transparent text-sm font-semibold text-slate-800 outline-none"
                        @input="handleShareInput(summary.categoryId, payer, $event)"
                      >
                      <span class="pb-0.5 text-xs font-bold text-slate-400">{{ summary.mode === 'percentage' ? '%' : '円' }}</span>
                    </div>
                    <p class="mt-1 text-[11px] text-slate-500">最終負担 {{ formatCurrency(summary.burdenByPayer[payer] ?? 0) }}</p>
                  </label>
                </div>
              </article>
            </div>
          </section>

          <div class="grid gap-3 xl:grid-cols-[1.15fr,0.85fr]">
            <section class="rounded-[24px] border border-white/70 bg-white/90 p-3.5 shadow-[0_16px_40px_rgba(15,23,42,0.07)] backdrop-blur sm:p-4">
              <div class="mb-3 flex items-center justify-between gap-3">
                <div>
                  <h2 class="text-base font-black text-slate-900">支払額と最終負担額</h2>
                  <p class="text-xs text-slate-500">実際の支払い合計とカテゴリ配分後の最終負担額との差分です。</p>
                </div>
                <span class="rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.18em]" :class="isAllocationValid ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-600'">
                  {{ isAllocationValid ? 'ready' : 'check inputs' }}
                </span>
              </div>

              <div class="overflow-x-auto">
                <table class="min-w-full border-separate border-spacing-y-2">
                  <thead>
                    <tr>
                      <th class="px-3 py-1 text-left text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">支払者</th>
                      <th class="px-3 py-1 text-right text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">支払合計</th>
                      <th class="px-3 py-1 text-right text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">最終負担額</th>
                      <th class="px-3 py-1 text-right text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">差分</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in payerSettlementRows" :key="row.payer" class="rounded-xl bg-slate-50">
                      <td class="rounded-l-xl px-3 py-3 text-sm font-bold text-slate-800">{{ row.payer }}</td>
                      <td class="px-3 py-3 text-right text-sm font-semibold text-slate-600">{{ formatCurrency(row.paid) }}</td>
                      <td class="px-3 py-3 text-right text-sm font-semibold text-slate-600">{{ formatCurrency(row.burden) }}</td>
                      <td class="rounded-r-xl px-3 py-3 text-right text-sm font-black" :class="row.difference > 0 ? 'text-emerald-600' : row.difference < 0 ? 'text-rose-500' : 'text-slate-400'">
                        {{ row.difference > 0 ? '+' : '' }}{{ formatCurrency(row.difference) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <section class="rounded-[24px] border border-white/70 bg-white/90 p-3.5 shadow-[0_16px_40px_rgba(15,23,42,0.07)] backdrop-blur sm:p-4">
              <div class="mb-3 flex items-center justify-between gap-3">
                <div>
                  <h2 class="text-base font-black text-slate-900">受け渡し結果</h2>
                  <p class="text-xs text-slate-500">誰が誰にいくら渡すかを、差分から自動算出します。</p>
                </div>
                <span class="rounded-full bg-indigo-50 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.18em] text-indigo-700">
                  {{ settlementTransfers.length }} transfers
                </span>
              </div>

              <div v-if="!isAllocationValid" class="rounded-xl border border-dashed border-rose-200 bg-rose-50 px-4 py-6 text-sm font-semibold text-rose-500">
                カテゴリごとの負担入力合計を正しくそろえると、精算結果を表示できます。
              </div>

              <div v-else-if="settlementTransfers.length === 0" class="rounded-xl border border-dashed border-emerald-200 bg-emerald-50 px-4 py-6 text-sm font-semibold text-emerald-600">
                精算は不要です。全員の支払額と最終負担額が一致しています。
              </div>

              <div v-else class="space-y-2">
                <article v-for="transfer in settlementTransfers" :key="`${transfer.from}-${transfer.to}-${transfer.amount}`" class="rounded-xl border border-slate-100 bg-[linear-gradient(135deg,_#f8fafc,_#eef4ff)] px-3.5 py-3 shadow-sm">
                  <div class="flex items-center justify-between gap-3">
                    <div>
                      <p class="text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">Transfer</p>
                      <p class="mt-1 text-sm font-black text-slate-900">{{ transfer.from }} → {{ transfer.to }}</p>
                    </div>
                    <p class="text-base font-black text-indigo-600">{{ formatCurrency(transfer.amount) }}</p>
                  </div>
                </article>
              </div>
            </section>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>