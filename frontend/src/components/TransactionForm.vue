<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useTransactionStore } from '../stores/transaction';
import type { TransactionRecord } from '../stores/transaction';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import DatePicker from 'primevue/datepicker';
import Select from 'primevue/select';
import Textarea from 'primevue/textarea';
import Checkbox from 'primevue/checkbox';
import Button from 'primevue/button';

const props = defineProps<{
  isOpen: boolean;
  mode: 'create' | 'edit';
  selectedTransaction: TransactionRecord | null;
}>();
const emit = defineEmits<{
  (e: 'close'): void
}>();
const store = useTransactionStore();
const DEFAULT_PAYER = '俊介';
const DEFAULT_EXPENSE_TYPE_ID = 1;

interface TransactionFormState {
  date: Date | null;
  amount: number | null;
  category_id: number | null;
  expense_type_id: number;
  shop: string;
  content: string;
  payer: string;
  description: string;
}

const toDate = (value: string) => {
  const [year, month, day] = value.split('-').map(Number);
  return new Date(year, month - 1, day);
};

const formatDateForApi = (value: Date | null) => {
  const source = value ?? new Date();
  const year = source.getFullYear();
  const month = `${source.getMonth() + 1}`.padStart(2, '0');
  const day = `${source.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const createEmptyForm = (overrides: Partial<TransactionFormState> = {}): TransactionFormState => ({
  date: new Date(),
  amount: null,
  category_id: null,
  expense_type_id: DEFAULT_EXPENSE_TYPE_ID,
  shop: '',
  content: '',
  payer: DEFAULT_PAYER,
  description: '',
  ...overrides,
});

const formData = ref<TransactionFormState>(createEmptyForm());

const isContinuous = ref(false);

const dialogTitle = computed(() => props.mode === 'edit' ? '取引を編集' : '新規登録');

const submitLabel = computed(() => props.mode === 'edit' ? '更新' : '保存');

const showContinuousOption = computed(() => props.mode === 'create');

const resetForm = (overrides: Partial<TransactionFormState> = {}) => {
  formData.value = createEmptyForm(overrides);
};

const populateForm = (transaction: TransactionRecord) => {
  formData.value = createEmptyForm({
    date: toDate(transaction.date),
    amount: transaction.amount,
    category_id: transaction.category_id,
    expense_type_id: transaction.expense_type_id,
    shop: transaction.shop,
    content: transaction.content,
    payer: transaction.payer,
    description: transaction.description ?? '',
  });
};

watch(
  () => [props.isOpen, props.mode, props.selectedTransaction] as const,
  ([isOpen, mode, selectedTransaction]) => {
    if (!isOpen) {
      resetForm();
      isContinuous.value = false;
      return;
    }

    if (mode === 'edit' && selectedTransaction) {
      populateForm(selectedTransaction);
      isContinuous.value = false;
      return;
    }

    resetForm();
    isContinuous.value = false;
  },
  { immediate: true }
);

const submitForm = async () => {
  const payload = {
    ...formData.value,
    date: formatDateForApi(formData.value.date),
  };

  const success = props.mode === 'edit' && props.selectedTransaction
    ? await store.updateTransaction(props.selectedTransaction.id, payload)
    : await store.addTransaction(payload);

  if (success) {
    if (props.mode === 'create' && isContinuous.value) {
      resetForm({
        date: formData.value.date,
        payer: formData.value.payer,
      });
    } else {
      closeModal();
    }
  } else {
    alert('保存に失敗しました。');
  }
};

const closeModal = () => {
  resetForm();
  isContinuous.value = false;
  emit('close');
};

const dialogPt = {
  root: { class: 'fin-panel w-[calc(100vw-0.75rem)] max-w-[34rem] overflow-hidden rounded-[14px] sm:w-full max-h-[calc(100vh-1rem)]' },
  header: { class: 'border-b fin-hairline bg-surface px-3.5 py-2.5 sm:px-4 sm:py-3 flex justify-between items-center' },
  title: { class: 'text-[15px] sm:text-[16px] font-semibold tracking-[-0.02em] text-ink' },
  closeButton: { class: 'text-muted hover:text-ink focus:outline-none rounded-full w-7 h-7 flex items-center justify-center' },
  closeIcon: { class: 'text-[12px]' },
  content: { class: 'bg-panel p-3 space-y-2.5 sm:p-3.5 sm:space-y-3 max-h-[calc(100vh-5.5rem)] overflow-y-auto' },
};

const inputPt = {
  root: { class: 'fin-input min-h-[34px] rounded-[9px] px-2.5 py-1.5 text-[12px]' },
};

const selectPt = {
  root: { class: 'fin-select min-h-[34px] rounded-[9px] px-2.5 py-1 text-[12px] cursor-pointer flex items-center justify-between' },
  label: { class: 'flex-1 truncate text-[12px] text-ink-soft' },
  dropdown: { class: 'ml-2 text-muted' },
  panel: { class: 'fin-panel mt-1 z-50 rounded-[12px] text-[12px]' },
  list: { class: 'py-1 max-h-60 overflow-auto' },
  option: { class: 'px-3 py-1.5 text-[12px] text-ink-soft hover:bg-[#eef2f6] cursor-pointer data-[p-focused=true]:bg-[#eef2f6] data-[p-selected=true]:bg-[#e7eef5] data-[p-selected=true]:text-accent-strong' },
};

const datePt = {
  root: { class: 'w-full border' },
  input: { class: 'fin-input min-h-[34px] rounded-[9px] px-2.5 py-1.5 text-[12px]' },
};

const textareaPt = {
  root: { class: 'fin-textarea w-full min-h-[68px] rounded-[9px] px-2.5 py-1.5 text-[12px] resize-none' },
};
</script>

<template>
  <Dialog
    :visible="isOpen"
    modal
    :header="dialogTitle"
    :closable="true"
    :pt="dialogPt"
    @update:visible="(v) => !v && closeModal()"
  >
    <form @submit.prevent="submitForm" class="space-y-2.5 sm:space-y-3">
      <div class="grid grid-cols-1 gap-2 sm:grid-cols-2 sm:gap-2.5">
        <div>
          <label class="fin-label mb-0.5 block">日付</label>
          <DatePicker
            v-model="formData.date"
            dateFormat="yy-mm-dd"
            showIcon
            :pt="datePt"
          />
        </div>
        <div>
          <label class="fin-label mb-0.5 block">金額</label>
          <InputNumber
            v-model="formData.amount"
            :min="1"
            mode="decimal"
            :useGrouping="false"
            required
            class="border"
            :pt="{ root: { class: 'w-full' }, input: `${inputPt.root.class} fin-table-cell-number text-right` }"
          />
        </div>
      </div>

      <div class="grid grid-cols-1 gap-2 sm:grid-cols-2 sm:gap-2.5">
        <div>
          <label class="fin-label mb-0.5 block">カテゴリ</label>
          <Select
            v-model="formData.category_id"
            :options="store.categories"
            optionLabel="name"
            optionValue="id"
            placeholder="選択してください"
            required
            :pt="selectPt"
          />
        </div>
        <div>
          <label class="fin-label mb-0.5 block">支出タイプ</label>
          <Select
            v-model="formData.expense_type_id"
            :options="store.expenseTypes"
            optionLabel="name"
            optionValue="id"
            placeholder="選択してください"
            required
            :pt="selectPt"
          />
        </div>
      </div>

      <div class="grid grid-cols-1 gap-2 sm:grid-cols-2 sm:gap-2.5">
        <div>
          <label class="fin-label mb-0.5 block">店舗名</label>
          <InputText
            v-model="formData.shop"
            required
            placeholder="例: スーパー◯◯"
            :pt="inputPt"
          />
        </div>
        <div>
          <label class="fin-label mb-0.5 block">商品・内容</label>
          <InputText
            v-model="formData.content"
            required
            placeholder="例: 食材まとめ買い"
            :pt="inputPt"
          />
        </div>
      </div>

      <div class="grid grid-cols-1 gap-2 sm:grid-cols-[180px_minmax(0,1fr)] sm:gap-2.5">
        <div>
          <label class="fin-label mb-0.5 block">支払者</label>
          <Select
            v-model="formData.payer"
            :options="store.payers"
            optionLabel="name"
            optionValue="name"
            placeholder="選択してください"
            required
            :pt="selectPt"
          />
        </div>
        <div>
          <label class="fin-label mb-0.5 block">備考</label>
          <Textarea
            v-model="formData.description"
            :rows="2"
            :pt="textareaPt"
          />
        </div>
      </div>

      <div class="mt-1 flex flex-col gap-2 border-t fin-hairline pt-2.5 sm:flex-row sm:items-center sm:justify-between">
        <label
          v-if="showContinuousOption"
          class="flex w-full cursor-pointer items-center gap-2 text-[12px] text-ink-soft sm:w-auto"
        >
          <Checkbox
            v-model="isContinuous"
            binary
            :pt="{
              root: { class: 'flex items-center' },
              box: { class: 'w-4 h-4 rounded border border-line flex items-center justify-center cursor-pointer data-[p-checked=true]:bg-accent data-[p-checked=true]:border-accent' },
              icon: { class: 'text-white text-xs' },
            }"
          />
          連続入力する
        </label>
        <span v-else class="text-[11px] text-muted">既存の取引を更新します</span>
        <div class="flex w-full gap-2 sm:w-auto">
          <Button
            type="button"
            label="キャンセル"
            @click="closeModal"
            :pt="{
              root: { class: 'fin-button flex-1 rounded-[9px] px-3 py-1.5 text-[12px] sm:flex-none cursor-pointer' },
            }"
          />
          <Button
            type="submit"
            :label="submitLabel"
            :pt="{
              root: { class: 'fin-button fin-button-primary flex-1 rounded-[9px] px-3 py-1.5 text-[12px] sm:flex-none cursor-pointer' },
            }"
          />
        </div>
      </div>
    </form>
  </Dialog>
</template>