<script setup lang="ts">
import { ref, watch } from 'vue';
import { useTransactionStore } from '../stores/transaction';

const props = defineProps<{
  isOpen: boolean;
}>();
const emit = defineEmits<{
  (e: 'close'): void
}>();
const store = useTransactionStore();

interface TransactionForm {
  date: string;
  amount: number | '';
  category_id: number | '';
  shop: string;
  content: string;
  payer: string;
  description: string;
}

const formData = ref<TransactionForm>({
  date: new Date().toISOString().split('T')[0],
  amount: '',
  category_id: '',
  shop: '',
  content: '',
  payer: '自分',
  description: '',
});

const isContinuous = ref(false);

const resetForm = () => {
    formData.value = {
      date: formData.value.date, // Keep the same date for continuous entry
      amount: '',
      category_id: '',
      shop: '',
      content: '',
      payer: formData.value.payer, // Keep payer
      description: '',
    };
};

const submitForm = async () => {
  const success = await store.addTransaction({...formData.value});
  if (success) {
    if (isContinuous.value) {
        resetForm();
    } else {
        closeModal();
    }
  } else {
    alert("保存に失敗しました。");
  }
};

const closeModal = () => {
    resetForm();
    emit('close');
};

</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md overflow-hidden">
      <!-- Header -->
      <div class="bg-blue-600 px-6 py-4 flex justify-between items-center text-white">
        <h2 class="text-xl font-bold">新規登録</h2>
        <button @click="closeModal" class="text-white hover:text-gray-200 focus:outline-none">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>
      </div>

      <!-- Form Body -->
      <form @submit.prevent="submitForm" class="p-6 space-y-4">
        
        <div class="grid grid-cols-2 gap-4">
           <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">日付</label>
            <input type="date" v-model="formData.date" required class="w-full border-gray-300 border rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">金額 (円)</label>
            <input type="number" v-model="formData.amount" required min="1" class="w-full border-gray-300 border rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500">
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">カテゴリ</label>
          <select v-model="formData.category_id" required class="w-full border-gray-300 border rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500 bg-white">
            <option disabled value="">選択してください</option>
            <option v-for="cat in store.categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>

        <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">店舗名</label>
              <input type="text" v-model="formData.shop" required placeholder="例: スーパー◯◯" class="w-full border-gray-300 border rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">商品・内容</label>
              <input type="text" v-model="formData.content" required placeholder="例: 食材まとめ買い" class="w-full border-gray-300 border rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500">
            </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">支払者</label>
          <input type="text" v-model="formData.payer" required class="w-full border-gray-300 border rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500">
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">備考</label>
          <textarea v-model="formData.description" rows="2" class="w-full border-gray-300 border rounded-md shadow-sm p-2 focus:ring-blue-500 focus:border-blue-500"></textarea>
        </div>

        <!-- Footer Actions -->
        <div class="flex items-center justify-between pt-4 border-t border-gray-200 mt-6">
           <label class="flex items-center text-sm text-gray-600">
              <input type="checkbox" v-model="isContinuous" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-2">
              連続入力する
           </label>
           <div class="space-x-3">
               <button type="button" @click="closeModal" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50">キャンセル</button>
               <button type="submit" class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700">保存</button>
           </div>
        </div>
      </form>

    </div>
  </div>
</template>
