<script setup lang="ts">
import { ref } from 'vue';
import { useTransactionStore } from '../stores/transaction';
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
}>();
const emit = defineEmits<{
  (e: 'close'): void
}>();
const store = useTransactionStore();

interface TransactionForm {
  date: Date | null;
  amount: number | null;
  category_id: number | null;
  shop: string;
  content: string;
  payer: string;
  description: string;
}

const formData = ref<TransactionForm>({
  date: new Date(),
  amount: null,
  category_id: null,
  shop: '',
  content: '',
  payer: '俊介',
  description: '',
});

const isContinuous = ref(false);

const resetForm = () => {
  formData.value = {
    date: formData.value.date,
    amount: null,
    category_id: null,
    shop: '',
    content: '',
    payer: formData.value.payer,
    description: '',
  };
};

const submitForm = async () => {
  const payload = {
    ...formData.value,
    date: formData.value.date
      ? formData.value.date.toISOString().split('T')[0]
      : new Date().toISOString().split('T')[0],
  };
  const success = await store.addTransaction(payload);
  if (success) {
    if (isContinuous.value) {
      resetForm();
    } else {
      closeModal();
    }
  } else {
    alert('保存に失敗しました。');
  }
};

const closeModal = () => {
  resetForm();
  emit('close');
};

const dialogPt = {
  root: { class: 'bg-white rounded-lg shadow-xl w-[calc(100vw-1rem)] max-w-[36rem] sm:w-full overflow-hidden' },
  header: { class: 'bg-blue-600 px-4 py-3 sm:px-5 sm:py-3.5 flex justify-between items-center text-white' },
  title: { class: 'text-base sm:text-lg font-bold text-white' },
  closeButton: { class: 'text-white hover:text-gray-200 focus:outline-none rounded-full w-7 h-7 flex items-center justify-center' },
  closeIcon: { class: 'text-white' },
  content: { class: 'p-3.5 space-y-3 sm:p-4 sm:space-y-3.5' },
};

const inputPt = {
  root: { class: 'w-full border-gray-300 border shadow-sm px-3 py-2 sm:py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm' },
};

const selectPt = {
  root: { class: 'w-full min-h-[38px] sm:min-h-[40px] border-gray-300 border shadow-sm px-3 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-sm cursor-pointer flex items-center justify-between' },
  label: { class: 'flex-1 text-sm text-gray-700 truncate' },
  dropdown: { class: 'ml-2 text-gray-400' },
  panel: { class: 'bg-white border border-gray-200 shadow-lg mt-1 z-50 text-sm' },
  list: { class: 'py-1 max-h-60 overflow-auto' },
  option: { class: 'px-3 py-2 hover:bg-blue-50 cursor-pointer text-gray-700 data-[p-focused=true]:bg-blue-50 data-[p-selected=true]:bg-blue-100 data-[p-selected=true]:text-blue-700' },
};

const datePt = {
  root: { class: 'w-full border' },
  input: { class: 'w-full border border-gray-300 shadow-sm px-3 py-2 sm:py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm' },
};

const textareaPt = {
  root: { class: 'w-full border border-gray-300 shadow-sm px-3 py-2 sm:py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-sm resize-none' },
};
</script>

<template>
  <Dialog
    :visible="isOpen"
    modal
    header="新規登録"
    :closable="true"
    :pt="dialogPt"
    @update:visible="(v) => !v && closeModal()"
  >
    <form @submit.prevent="submitForm" class="space-y-3 sm:space-y-3.5">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3">
        <div>
          <label class="block text-[11px] sm:text-xs font-medium text-gray-700 mb-0.5">日付</label>
          <DatePicker
            v-model="formData.date"
            dateFormat="yy-mm-dd"
            showIcon
            :pt="datePt"
          />
        </div>
        <div>
          <label class="block text-[11px] sm:text-xs font-medium text-gray-700 mb-0.5">金額 (円)</label>
          <InputNumber
            v-model="formData.amount"
            :min="1"
            mode="decimal"
            :useGrouping="false"
            required
            class="border"
            :pt="{ root: { class: 'w-full' }, input: inputPt.root }"
          />
        </div>
      </div>
    
      <div>
        <label class="block text-[11px] sm:text-xs font-medium text-gray-700 mb-0.5">カテゴリ</label>
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
    
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 sm:gap-3">
        <div>
          <label class="block text-[11px] sm:text-xs font-medium text-gray-700 mb-0.5">店舗名</label>
          <InputText
            v-model="formData.shop"
            required
            placeholder="例: スーパー◯◯"
            :pt="inputPt"
          />
        </div>
        <div>
          <label class="block text-[11px] sm:text-xs font-medium text-gray-700 mb-0.5">商品・内容</label>
          <InputText
            v-model="formData.content"
            required
            placeholder="例: 食材まとめ買い"
            :pt="inputPt"
          />
        </div>
      </div>
    
      <div>
        <label class="block text-[11px] sm:text-xs font-medium text-gray-700 mb-0.5">支払者</label>
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
        <label class="block text-[11px] sm:text-xs font-medium text-gray-700 mb-0.5">備考</label>
        <Textarea
          v-model="formData.description"
          :rows="2"
          :pt="textareaPt"
        />
      </div>
    
      <div class="flex flex-col gap-3 pt-3 border-t border-gray-200 mt-1 sm:flex-row sm:items-center sm:justify-between">
        <label class="flex items-center text-sm text-gray-600 gap-2 cursor-pointer w-full sm:w-auto">
          <Checkbox
            v-model="isContinuous"
            binary
            :pt="{
              root: { class: 'flex items-center' },
              box: { class: 'w-4 h-4 rounded border border-gray-300 flex items-center justify-center cursor-pointer data-[p-checked=true]:bg-blue-600 data-[p-checked=true]:border-blue-600' },
              icon: { class: 'text-white text-xs' },
            }"
          />
          連続入力する
        </label>
        <div class="flex w-full gap-2 sm:w-auto">
          <Button
            type="button"
            label="キャンセル"
            @click="closeModal"
            :pt="{
              root: { class: 'flex-1 sm:flex-none px-3.5 py-2 sm:py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 shadow-sm hover:bg-gray-50 cursor-pointer' },
            }"
          />
          <Button
            type="submit"
            label="保存"
            :pt="{
              root: { class: 'flex-1 sm:flex-none px-3.5 py-2 sm:py-1.5 text-sm font-medium text-white bg-blue-600 border border-transparent shadow-sm hover:bg-blue-700 cursor-pointer' },
            }"
          />
        </div>
      </div>
    </form>
  </Dialog>
</template>