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

const actionButtonPt = {
  root: { class: 'fin-button rounded-[10px] px-3.5 py-2 flex items-center gap-2 cursor-pointer' },
  label: { class: 'text-[12px] font-semibold tracking-[-0.01em]' },
  icon: { class: 'text-[12px]' }
};

const modeSwitchPt = {
  root: { class: 'grid grid-cols-2 rounded-[10px] border border-line bg-surface p-1' },
  button: { class: 'rounded-[8px] px-3 py-1.5 text-[12px] font-semibold text-muted transition border-none bg-transparent hover:bg-panel hover:text-ink-soft data-[p-selected=true]:bg-panel data-[p-selected=true]:text-accent-strong' },
  label: { class: 'm-0' }
};
</script>

<template>
  <div class="fin-page min-h-screen px-3 py-3 sm:px-5 sm:py-5 lg:px-6">
    <div class="fin-frame flex flex-col gap-3">
      <section class="fin-panel overflow-hidden rounded-panel">
        <div class="grid gap-3 border-b fin-hairline px-4 py-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
          <div class="space-y-1">
            <div class="flex flex-wrap items-end gap-x-3 gap-y-1">
              <h1 class="fin-title text-[26px] font-semibold leading-none">精算額計算</h1>
              <span class="fin-label">Settlement Planner</span>
            </div>
            <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-[12px] fin-subtle">
              <span>月次の共通支出をもとに、カテゴリ別の負担と受け渡し先を整理します。</span>
            </div>
          </div>
          <Button label="ダッシュボードへ戻る" icon="pi pi-arrow-left" @click="router.push('/')" :pt="actionButtonPt" />
        </div>

        <div class="grid gap-px bg-line lg:grid-cols-[280px_1fr]">
          <label class="fin-panel-muted flex flex-col gap-1 px-4 py-3">
            <span class="fin-label">対象月</span>
            <input v-model="selectedMonth" type="month" class="fin-input rounded-[10px] px-3 py-2">
          </label>

          <div class="grid gap-px bg-line sm:grid-cols-3">
            <article class="fin-panel-muted px-4 py-3">
              <div class="fin-label">集計期間</div>
              <div class="mt-1 text-[14px] font-semibold text-ink">{{ monthRange.label }}</div>
              <div class="mt-1 text-[11px] text-muted">{{ monthRange.startDate }} 〜 {{ monthRange.endDate }}</div>
            </article>
            <article class="fin-panel-muted px-4 py-3">
              <div class="fin-label">対象支出</div>
              <div class="mt-1 text-[14px] font-semibold text-ink">共通のみ</div>
              <div class="mt-1 text-[11px] text-muted">{{ monthlyTransactions.length }}件の取引</div>
            </article>
            <article class="fin-panel-brand px-4 py-3">
              <div class="fin-label text-white/75">共通支出合計</div>
              <div class="mt-1 fin-value text-[20px] font-semibold text-white">{{ formatCurrency(totalCommonExpense) }}</div>
              <div class="mt-1 text-[11px] text-white/80">{{ categoryTotals.length }}カテゴリ</div>
            </article>
          </div>
        </div>
      </section>

      <div v-if="loadError" class="fin-panel rounded-panel border-[#e3d2d3] bg-[#f6efef] px-4 py-3 text-[13px] font-semibold text-[#7b4f53]">
        {{ loadError }}
      </div>

      <div v-if="isLoading" class="fin-panel rounded-panel px-4 py-12 text-center text-[13px] font-semibold text-muted">
        共通支出データを読み込み中です。
      </div>

      <template v-else>
        <div v-if="categoryTotals.length === 0" class="fin-panel rounded-panel px-4 py-12 text-center text-[13px] font-semibold text-muted">
          この月の共通支出は見つかりませんでした。
        </div>

        <template v-else>
          <section class="fin-panel rounded-panel p-3 sm:p-4">
            <div class="mb-3 flex items-center justify-between gap-3">
              <div>
                <h2 class="text-[15px] font-semibold text-ink">カテゴリ別負担設定</h2>
                <p class="text-[12px] text-muted">カテゴリごとに、支払者別の負担割合を％または金額で入力します。</p>
              </div>
              <span class="rounded-[999px] border border-line bg-surface px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-ink-soft">
                {{ payerNames.length }} payers
              </span>
            </div>

            <div class="space-y-3">
              <article v-for="summary in categoryAllocationSummaries" :key="summary.categoryId" class="rounded-[14px] border border-line bg-[linear-gradient(180deg,_#ffffff,_#f8fafc)] p-3.5">
                <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <div class="flex flex-wrap items-center gap-2">
                      <h3 class="text-[14px] font-semibold text-ink">{{ summary.categoryName }}</h3>
                      <span class="rounded-[999px] border border-line bg-panel px-2 py-1 text-[10px] font-semibold text-accent-strong">{{ formatCurrency(summary.totalAmount) }}</span>
                      <span class="rounded-[999px] border border-line bg-surface px-2 py-1 text-[10px] font-semibold text-muted">{{ summary.transactionCount }}件</span>
                    </div>
                    <p class="mt-1 text-[11px]" :class="summary.isValid ? 'text-positive' : 'text-[#7b4f53]'">
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
                      :pt="modeSwitchPt"
                    />
                    <Button
                      label="等分"
                      icon="pi pi-percentage"
                      @click="applyEqualSplit(summary.categoryId, summary.totalAmount)"
                      :pt="actionButtonPt"
                    />
                  </div>
                </div>

                <div class="mt-3 grid gap-2 md:grid-cols-2 xl:grid-cols-4">
                  <label v-for="payer in payerNames" :key="`${summary.categoryId}-${payer}`" class="rounded-[12px] border border-line bg-panel px-3 py-2">
                    <span class="fin-label">{{ payer }}</span>
                    <div class="mt-1.5 flex items-end gap-2">
                      <input
                        :value="allocations[summary.categoryId]?.shares[payer] ?? ''"
                        type="number"
                        min="0"
                        :step="summary.mode === 'percentage' ? '0.1' : '1'"
                        class="fin-input w-full rounded-[8px] px-2 py-1 text-[12px] font-semibold text-ink"
                        @input="handleShareInput(summary.categoryId, payer, $event)"
                      >
                      <span class="pb-0.5 text-[11px] font-semibold text-muted">{{ summary.mode === 'percentage' ? '%' : '円' }}</span>
                    </div>
                    <p class="mt-1 text-[11px] text-muted">最終負担 {{ formatCurrency(summary.burdenByPayer[payer] ?? 0) }}</p>
                  </label>
                </div>
              </article>
            </div>
          </section>

          <div class="grid gap-3 xl:grid-cols-[1.15fr,0.85fr]">
            <section class="fin-panel rounded-panel p-3.5 sm:p-4">
              <div class="mb-3 flex items-center justify-between gap-3">
                <div>
                  <h2 class="text-[15px] font-semibold text-ink">支払額と最終負担額</h2>
                  <p class="text-[12px] text-muted">実際の支払い合計とカテゴリ配分後の最終負担額との差分です。</p>
                </div>
                <span class="rounded-[999px] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em]" :class="isAllocationValid ? 'fin-status-positive border' : 'border border-[#e3d2d3] bg-[#f6efef] text-[#7b4f53]'">
                  {{ isAllocationValid ? 'ready' : 'check inputs' }}
                </span>
              </div>

              <div class="overflow-x-auto">
                <table class="min-w-full border-separate border-spacing-y-2">
                  <thead>
                    <tr>
                      <th class="px-3 py-1 text-left text-[10px] font-semibold uppercase tracking-[0.14em] text-muted">支払者</th>
                      <th class="px-3 py-1 text-right text-[10px] font-semibold uppercase tracking-[0.14em] text-muted">支払合計</th>
                      <th class="px-3 py-1 text-right text-[10px] font-semibold uppercase tracking-[0.14em] text-muted">最終負担額</th>
                      <th class="px-3 py-1 text-right text-[10px] font-semibold uppercase tracking-[0.14em] text-muted">差分</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="row in payerSettlementRows" :key="row.payer" class="rounded-[12px] bg-surface">
                      <td class="rounded-l-[12px] px-3 py-3 text-[13px] font-semibold text-ink">{{ row.payer }}</td>
                      <td class="px-3 py-3 text-right text-[13px] font-semibold text-ink-soft">{{ formatCurrency(row.paid) }}</td>
                      <td class="px-3 py-3 text-right text-[13px] font-semibold text-ink-soft">{{ formatCurrency(row.burden) }}</td>
                      <td class="rounded-r-[12px] px-3 py-3 text-right text-[13px] font-semibold" :class="row.difference > 0 ? 'text-positive' : row.difference < 0 ? 'text-[#7b4f53]' : 'text-muted'">
                        {{ row.difference > 0 ? '+' : '' }}{{ formatCurrency(row.difference) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <section class="fin-panel rounded-panel p-3.5 sm:p-4">
              <div class="mb-3 flex items-center justify-between gap-3">
                <div>
                  <h2 class="text-[15px] font-semibold text-ink">受け渡し結果</h2>
                  <p class="text-[12px] text-muted">誰が誰にいくら渡すかを差分から自動算出します。</p>
                </div>
                <span class="rounded-[999px] border border-line bg-surface px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-ink-soft">
                  {{ settlementTransfers.length }} transfers
                </span>
              </div>

              <div v-if="!isAllocationValid" class="rounded-[12px] border border-dashed border-[#e3d2d3] bg-[#f6efef] px-4 py-6 text-[13px] font-semibold text-[#7b4f53]">
                カテゴリごとの負担入力合計を正しくそろえると、精算結果を表示できます。
              </div>

              <div v-else-if="settlementTransfers.length === 0" class="rounded-[12px] border border-dashed border-[#cddfd3] bg-[#e8f5ee] px-4 py-6 text-[13px] font-semibold text-positive">
                精算は不要です。全員の支払額と最終負担額が一致しています。
              </div>

              <div v-else class="space-y-2">
                <article v-for="transfer in settlementTransfers" :key="`${transfer.from}-${transfer.to}-${transfer.amount}`" class="rounded-[12px] border border-line bg-[linear-gradient(135deg,_#f8fafc,_#eef4ff)] px-3.5 py-3">
                  <div class="flex items-center justify-between gap-3">
                    <div>
                      <p class="fin-label">Transfer</p>
                      <p class="mt-1 text-[13px] font-semibold text-ink">{{ transfer.from }} → {{ transfer.to }}</p>
                    </div>
                    <p class="fin-value text-[16px] font-semibold text-accent-strong">{{ formatCurrency(transfer.amount) }}</p>
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