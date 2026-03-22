<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import Button from 'primevue/button';
import MultiSelect from 'primevue/multiselect';
import { useImportStore } from '../stores/useImportStore';
import { useTransactionStore } from '../stores/transaction';
import type { TransactionRecord } from '../stores/transaction';

const TransactionList = defineAsyncComponent(() => import('../components/TransactionList.vue').then((module: any) => module.default ?? module));
const TransactionForm = defineAsyncComponent(() => import('../components/TransactionForm.vue').then((module: any) => module.default ?? module));

const store = useTransactionStore();
const importStore = useImportStore();
const router = useRouter();

const isModalOpen = ref(false);
const modalMode = ref<'create' | 'edit'>('create');
const selectedTransaction = ref<TransactionRecord | null>(null);
const isFilterVisible = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);

const formatDateForInput = (date: Date) => {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, '0');
  const day = `${date.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const createCurrentMonthFilters = () => {
  const today = new Date();
  const start = new Date(today.getFullYear(), today.getMonth(), 1);
  const end = new Date(today.getFullYear(), today.getMonth() + 1, 0);

  return {
    start_date: formatDateForInput(start),
    end_date: formatDateForInput(end),
    category_ids: [] as number[],
    payer: '',
    expense_type_id: '' as number | '',
    keyword: ''
  };
};

const filters = ref({
  ...createCurrentMonthFilters()
});

const handleSearch = () => {
  const activeFilters = Object.entries(filters.value).reduce<Record<string, string | number | number[]>>((result, [key, value]) => {
    if (Array.isArray(value)) {
      if (value.length > 0) {
        result[key] = value;
      }
      return result;
    }

    if (value !== '' && value !== null) {
      result[key] = value;
    }

    return result;
  }, {});

  store.fetchTransactions(activeFilters);
};

const handleReset = () => {
  filters.value = createCurrentMonthFilters();
  handleSearch();
};

const triggerFileInput = () => {
  fileInput.value?.click();
};

const openCreateModal = () => {
  modalMode.value = 'create';
  selectedTransaction.value = null;
  isModalOpen.value = true;
};

const openEditModal = (transaction: TransactionRecord) => {
  modalMode.value = 'edit';
  selectedTransaction.value = transaction;
  isModalOpen.value = true;
};

const handleModalClose = () => {
  isModalOpen.value = false;
  selectedTransaction.value = null;
  modalMode.value = 'create';
};

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    const file = target.files[0];
    importStore.setFile(file);

    router.push('/import');

    importStore.analyzePdf().catch((error) => {
      console.error('Initial analysis failed', error);
    });
  }
  target.value = '';
};

onMounted(async () => {
  await Promise.all([
    store.fetchCategories(),
    store.fetchPayers(),
    store.fetchExpenseTypes()
  ]);
  handleSearch();
});

const totalAmount = computed(() => {
  return store.transactions.reduce((sum: number, current: any) => sum + current.amount, 0);
});

const activeFilterCount = computed(() => {
  let count = 0;
  if (filters.value.category_ids.length > 0) count += 1;
  if (filters.value.payer) count += 1;
  if (filters.value.expense_type_id) count += 1;
  if (filters.value.keyword.trim()) count += 1;
  return count;
});

const periodLabel = computed(() => {
  if (!filters.value.start_date || !filters.value.end_date) {
    return '期間未設定';
  }

  return `${filters.value.start_date} - ${filters.value.end_date}`;
});

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

const accentActionButtonPt = {
  root: { class: 'fin-button fin-button-accent rounded-[10px] px-3.5 py-2 flex items-center gap-2 cursor-pointer' },
  label: { class: 'text-[12px] font-semibold tracking-[-0.01em]' },
  icon: { class: 'text-[12px]' }
};

const mobileActionBase = 'fin-button rounded-[10px] min-h-[42px] justify-center px-2.5 py-2';

const multiSelectPt = {
  root: { class: 'fin-select rounded-[10px] px-2.5 py-1 bg-panel flex items-center' },
  labelContainer: { class: 'flex-1 overflow-hidden' },
  label: { class: 'truncate text-[12px] text-ink-soft' },
  dropdown: { class: 'w-4 text-muted' },
  trigger: { class: 'w-4 text-muted' },
  panel: { class: 'fin-panel rounded-[12px] mt-1 overflow-hidden text-[12px]' },
  header: { class: 'border-b border-line bg-surface px-3 py-2' },
  list: { class: 'py-1 max-h-56 overflow-auto' },
  option: { class: 'px-3 py-2 text-[12px] text-ink-soft hover:bg-[#eef2f6] data-[p-selected=true]:bg-[#e7eef5] data-[p-selected=true]:text-accent-strong' },
  token: { class: 'rounded-[8px] border border-[#d6dee7] bg-[#edf2f7] px-1.5 py-0.5 text-[10px] font-semibold text-[#35506a]' }
};
</script>

<template>
  <div class="fin-page h-screen overflow-hidden">
    <div class="fin-frame flex h-full flex-col gap-2 px-3 py-3 sm:px-5 sm:py-5 lg:px-6">
      <input type="file" ref="fileInput" accept="application/pdf" class="hidden" @change="handleFileUpload">

      <section class="fin-panel overflow-hidden rounded-panel">
        <div class="grid gap-2 border-b fin-hairline px-3 py-2.5 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center lg:px-4 lg:py-3">
          <div class="space-y-0.5">
            <div class="flex flex-wrap items-end gap-x-3 gap-y-1">
              <h1 class="fin-title text-[22px] font-semibold leading-none lg:text-[24px]">ダッシュボード</h1>
              <span class="fin-label">Household Ledger Console</span>
            </div>
            <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] fin-subtle lg:text-[12px]">
              <span>家計の記録と日次オペレーション</span>
              <span class="hidden h-3 w-px bg-line sm:block"></span>
              <span class="fin-value text-[12px] text-ink-soft">{{ periodLabel }}</span>
            </div>
          </div>

        </div>

        <div class="border-t fin-hairline px-3 py-2 lg:px-4">
          <div class="flex flex-wrap items-center gap-x-4 gap-y-2 text-[11px] lg:text-[12px]">
            <div class="min-w-0 flex items-center gap-2 lg:pr-2">
              <span class="fin-label text-accent-strong">対象期間</span>
              <span class="fin-value truncate text-[14px] font-semibold text-ink">{{ periodLabel }}</span>
              <span class="shrink-0 rounded-[999px] border border-[rgba(1,118,211,0.18)] bg-[rgba(1,118,211,0.06)] px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.12em] text-accent-strong">Monthly</span>
            </div>

            <span class="hidden h-4 w-px bg-line lg:block"></span>

            <div class="flex items-baseline gap-2">
              <span class="fin-label">総支出</span>
              <span class="fin-value text-[16px] font-semibold text-accent-strong">{{ formatCurrency(totalAmount) }}</span>
            </div>

            <span class="hidden h-4 w-px bg-line lg:block"></span>

            <div class="flex items-baseline gap-2">
              <span class="fin-label">登録件数</span>
              <span class="fin-value text-[16px] font-semibold text-positive">{{ store.transactions.length }}</span>
              <span class="text-[10px] text-muted">entries</span>
            </div>

            <span class="hidden h-4 w-px bg-line lg:block"></span>

            <div class="flex items-baseline gap-2">
              <span class="fin-label">フィルタ</span>
              <span class="fin-value text-[16px] text-ink">{{ activeFilterCount }}</span>
              <span class="text-[10px] text-muted">追加条件</span>
            </div>

            <div class="ml-auto overflow-x-auto">
              <div class="flex min-w-max items-center gap-1.5">
                <Button icon="pi pi-chart-bar" label="レポート" @click="router.push('/analytics')" :pt="{ root: { class: 'fin-button rounded-[8px] px-2 py-1 min-h-[30px] flex items-center gap-1 cursor-pointer' }, label: { class: 'text-[10px] font-semibold tracking-[-0.01em]' }, icon: { class: 'text-[10px]' } }" />
                <Button icon="pi pi-calculator" label="精算" @click="router.push('/settlement')" :pt="{ root: { class: 'fin-button rounded-[8px] px-2 py-1 min-h-[30px] flex items-center gap-1 cursor-pointer' }, label: { class: 'text-[10px] font-semibold tracking-[-0.01em]' }, icon: { class: 'text-[10px]' } }" />
                <Button :icon="isFilterVisible ? 'pi pi-filter-slash' : 'pi pi-filter'" :label="isFilterVisible ? '閉じる' : '絞込'" @click="isFilterVisible = !isFilterVisible" :pt="{ root: { class: ['fin-button rounded-[8px] px-2 py-1 min-h-[30px] flex items-center gap-1 cursor-pointer', isFilterVisible ? 'border-[color:var(--app-accent)] bg-[var(--app-accent-soft)] text-accent-strong' : ''] }, label: { class: 'text-[10px] font-semibold tracking-[-0.01em]' }, icon: { class: 'text-[10px]' } }" />
                <Button icon="pi pi-upload" label="PDF" @click="triggerFileInput" :pt="{ root: { class: 'fin-button fin-button-accent rounded-[8px] px-2 py-1 min-h-[30px] flex items-center gap-1 cursor-pointer' }, label: { class: 'text-[10px] font-semibold tracking-[-0.01em]' }, icon: { class: 'text-[10px]' } }" />
                <Button icon="pi pi-plus" label="新規" @click="openCreateModal" :pt="{ root: { class: 'fin-button fin-button-primary rounded-[8px] px-2 py-1 min-h-[30px] flex items-center gap-1 cursor-pointer' }, label: { class: 'text-[10px] font-semibold tracking-[-0.01em]' }, icon: { class: 'text-[10px]' } }" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="transform -translate-y-1 opacity-0"
        enter-to-class="transform translate-y-0 opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="transform translate-y-0 opacity-100"
        leave-to-class="transform -translate-y-1 opacity-0"
      >
        <section v-if="isFilterVisible" class="fin-panel rounded-panel px-3 py-3 sm:px-4 sm:py-3">
          <div class="flex flex-wrap items-center justify-between gap-2 border-b fin-hairline pb-2">
            <div class="min-w-0">
              <div class="fin-label">Search Conditions</div>
              <p class="mt-1 text-[11px] text-muted">期間と補助条件をここでまとめて指定します。</p>
            </div>
            <div class="flex items-center gap-2">
              <button class="rounded-[8px] border border-line bg-surface px-2.5 py-1.5 text-[11px] font-semibold text-ink-soft transition hover:border-line-strong hover:text-ink" @click="handleReset">
                <i class="pi pi-refresh mr-1 text-[10px]"></i>リセット
              </button>
              <Button label="検索" icon="pi pi-search" @click="handleSearch" :pt="{ root: { class: 'fin-button fin-button-primary rounded-[8px] px-2.5 py-1.5 flex items-center gap-1 cursor-pointer' }, label: { class: 'text-[11px] font-semibold tracking-[-0.01em]' }, icon: { class: 'text-[10px]' } }" />
              <Button label="閉じる" icon="pi pi-times" @click="isFilterVisible = false" :pt="{ root: { class: 'fin-button rounded-[8px] px-2.5 py-1.5 flex items-center gap-1 cursor-pointer' }, label: { class: 'text-[11px] font-semibold tracking-[-0.01em]' }, icon: { class: 'text-[10px]' } }" />
            </div>
          </div>

          <div class="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-6">
            <div class="space-y-1">
              <label class="fin-label">開始日</label>
              <input v-model="filters.start_date" type="date" class="fin-input rounded-[10px] px-3 py-2">
            </div>
            <div class="space-y-1">
              <label class="fin-label">終了日</label>
              <input v-model="filters.end_date" type="date" class="fin-input rounded-[10px] px-3 py-2">
            </div>
            <div class="space-y-1">
              <label class="fin-label">カテゴリ</label>
              <MultiSelect
                v-model="filters.category_ids"
                :options="store.categories"
                optionLabel="name"
                optionValue="id"
                placeholder="すべて"
                :maxSelectedLabels="2"
                class="w-full"
                :pt="multiSelectPt"
              />
            </div>
            <div class="space-y-1">
              <label class="fin-label">支払者</label>
              <select v-model="filters.payer" class="fin-select rounded-[10px] px-3 py-2">
                <option value="">すべて</option>
                <option v-for="payer in store.payers" :key="payer.id" :value="payer.name">{{ payer.name }}</option>
              </select>
            </div>
            <div class="space-y-1">
              <label class="fin-label">支出タイプ</label>
              <select v-model="filters.expense_type_id" class="fin-select rounded-[10px] px-3 py-2">
                <option value="">すべて</option>
                <option v-for="expenseType in store.expenseTypes" :key="expenseType.id" :value="expenseType.id">{{ expenseType.name }}</option>
              </select>
            </div>
            <div class="space-y-1 xl:col-span-2">
              <label class="fin-label">キーワード</label>
              <input v-model="filters.keyword" type="text" placeholder="店舗名・内容" class="fin-input rounded-[10px] px-3 py-2">
            </div>
          </div>
        </section>
      </Transition>

      <section v-if="store.error" class="fin-panel rounded-panel border-[#e3d2d3] bg-[#f6efef] px-4 py-3 text-[#7b4f53]">
        <div class="fin-label text-[#7b4f53]">System Notice</div>
        <p class="mt-1 text-[13px] font-medium">データの取得中にエラーが発生しました。</p>
      </section>

      <section v-if="store.isLoading" class="fin-panel rounded-panel flex items-center justify-center px-4 py-12">
        <div class="flex items-center gap-3 text-accent-strong">
          <svg class="h-6 w-6 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-80" fill="currentColor" d="M12 2a10 10 0 00-7.07 17.07l2.83-2.83A6 6 0 1112 18V2z"></path>
          </svg>
          <div>
            <div class="fin-label text-accent-strong">Loading Ledger</div>
            <div class="mt-1 text-[12px] text-ink-soft">最新の取引を同期しています。</div>
          </div>
        </div>
      </section>

      <section v-else class="fin-panel flex min-h-0 flex-1 flex-col overflow-hidden rounded-panel">
        <div class="flex items-center justify-between border-b fin-hairline bg-surface px-4 py-3">
          <div>
            <div class="fin-label">Transaction Ledger</div>
            <h2 class="mt-1 text-[14px] font-semibold tracking-[-0.02em] text-ink">取引履歴</h2>
          </div>
          <div class="text-right">
            <div class="fin-label">Sort</div>
            <div class="mt-1 text-[12px] text-ink-soft">最新順</div>
          </div>
        </div>
        <div class="min-h-0 flex-1 overflow-auto bg-[linear-gradient(180deg,_rgba(1,118,211,0.02),_rgba(255,255,255,0))]">
          <TransactionList
            :transactions="store.transactions"
            :categories="store.categories"
            @edit="openEditModal"
            @delete="store.deleteTransaction"
          />
        </div>
      </section>

      <TransactionForm
        :isOpen="isModalOpen"
        :mode="modalMode"
        :selectedTransaction="selectedTransaction"
        @close="handleModalClose"
      />
    </div>
  </div>
</template>

<style scoped>
/* Global theme utilities handle the visual system for this view. */
</style>
