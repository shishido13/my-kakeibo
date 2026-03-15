<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useTransactionStore } from '../stores/transaction';
import { useImportStore } from '../stores/useImportStore';
import { useRouter } from 'vue-router';
import TransactionList from '../components/TransactionList.vue';
import TransactionForm from '../components/TransactionForm.vue';
import Button from 'primevue/button';

const store = useTransactionStore();
const importStore = useImportStore();
const router = useRouter();
const isModalOpen = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);

const triggerFileInput = () => {
    fileInput.value?.click();
};

const handleFileUpload = async (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
        const file = target.files[0];
        importStore.setFile(file);
        
        // Navigate to the import verify view
        router.push('/import');
        
        // Start analyzing implicitly
        importStore.analyzePdf().catch(e => {
             console.error('Initial analysis failed', e);
             // Error state is handled within the view
        });
    }
    target.value = '';
};

onMounted(async () => {
  await Promise.all([
    store.fetchCategories(),
    store.fetchPayers(),
    store.fetchTransactions()
  ]);
});

const totalAmount = computed(() => {
    return store.transactions.reduce((sum: number, current: any) => sum + current.amount, 0);
});

const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ja-JP', { style: 'currency', currency: 'JPY' }).format(amount);
};

</script>

<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center py-10 px-4 w-full">
    <div class="max-w-5xl w-full">
        
       <!-- Header Section -->
       <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
         <div>
            <h1 class="text-3xl font-extrabold text-gray-900">ダッシュボード</h1>
            <p class="text-gray-500 mt-1">家計簿の履歴と管理</p>
         </div>
         <div class="flex gap-3">
           <input type="file" ref="fileInput" accept="application/pdf" class="hidden" @change="handleFileUpload">
           <Button
             label="PDF一括登録"
             icon="pi pi-upload"
             @click="triggerFileInput"
             :pt="{
               root: { class: 'bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition duration-200 flex items-center gap-2 cursor-pointer' },
               label: { class: 'font-semibold' },
               icon: { class: 'text-base' },
             }"
           />
           <Button
             label="新規作成"
             icon="pi pi-plus"
             @click="isModalOpen = true"
             :pt="{
               root: { class: 'bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg shadow-md transition duration-200 flex items-center gap-2 cursor-pointer' },
               label: { class: 'font-semibold' },
               icon: { class: 'text-base' },
             }"
           />
         </div>
       </div>

       <!-- Summary Cards -->
       <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="bg-white rounded-xl shadow p-6 border-l-4 border-blue-500">
             <h3 class="text-sm font-medium text-gray-500 uppercase">総合計支出</h3>
             <p class="mt-2 text-3xl font-bold text-gray-900">{{ formatCurrency(totalAmount) }}</p>
          </div>
          <div class="bg-white rounded-xl shadow p-6 border-l-4 border-green-500">
             <h3 class="text-sm font-medium text-gray-500 uppercase">登録件数</h3>
             <p class="mt-2 text-3xl font-bold text-gray-900">{{ store.transactions.length }} <span class="text-base font-normal text-gray-500">件</span></p>
          </div>
          <div class="bg-white rounded-xl shadow p-6 border-l-4 border-purple-500">
             <h3 class="text-sm font-medium text-gray-500 uppercase">カテゴリ数</h3>
             <p class="mt-2 text-3xl font-bold text-gray-900">{{ store.categories.length }} <span class="text-base font-normal text-gray-500">種類</span></p>
          </div>
       </div>

       <!-- Error state if failed to load -->
       <div v-if="store.error" class="bg-red-50 border-l-4 border-red-500 p-4 mb-8 rounded-r text-red-700">
          <p class="font-bold">エラーが発生しました</p>
          
       </div>

       <!-- Loading state -->
       <div v-if="store.isLoading" class="flex justify-center my-12">
            <svg class="animate-spin h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
       </div>

       <!-- Main List Section -->
       <div v-else>
         <h2 class="text-xl font-bold text-gray-800 mb-4">取引履歴</h2>
         <TransactionList 
           :transactions="store.transactions" 
           :categories="store.categories"
           @delete="store.deleteTransaction"
         />
       </div>

    </div>

    <!-- Modal Form -->
    <TransactionForm 
      :isOpen="isModalOpen" 
      @close="isModalOpen = false" 
    />
  </div>
</template>

<style scoped>
/* Tailwind handles the styles */
</style>
