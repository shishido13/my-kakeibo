<script setup lang="ts">
import { ref, onMounted, computed, defineAsyncComponent } from 'vue';
import { useTransactionStore } from '../stores/transaction';
import type { TransactionRecord } from '../stores/transaction';
import { useImportStore } from '../stores/useImportStore';
import { useRouter } from 'vue-router';
import Button from 'primevue/button';
import MultiSelect from 'primevue/multiselect';

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
      store.fetchExpenseTypes()
  ]);
   handleSearch();
});

const totalAmount = computed(() => {
    return store.transactions.reduce((sum: number, current: any) => sum + current.amount, 0);
});

const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ja-JP', { style: 'currency', currency: 'JPY' }).format(amount);
};

</script>

<template>
  <div class="h-screen bg-gray-50 flex flex-col py-6 px-4 sm:px-8 w-full overflow-hidden">
    <div class="max-w-[1440px] w-full mx-auto flex flex-col h-full bg-transparent">
        
       <!-- Header Section -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-end mb-4 gap-3 border-b border-gray-200 pb-4 md:mb-6 md:gap-4 md:pb-6">
          <div class="flex-1">
             <div class="flex items-center gap-3 md:gap-4">
                <h1 class="text-2xl font-bold text-gray-900">ダッシュボード</h1>
                <!-- Compact Stats Bar Integrated in Header -->
                <div class="hidden lg:flex items-center gap-6 ml-4 py-1 px-4 bg-gray-50 rounded-full border border-gray-200">
                   <div class="flex items-center gap-2">
                      <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">支出</span>
                      <span class="text-sm font-bold text-blue-600">{{ formatCurrency(totalAmount) }}</span>
                   </div>
                   <div class="w-px h-3 bg-gray-300"></div>
                   <div class="flex items-center gap-2">
                      <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">件数</span>
                      <span class="text-sm font-bold text-green-600">{{ store.transactions.length }}<span class="text-[10px] font-medium ml-0.5">件</span></span>
                   </div>
                </div>
             </div>
             <p class="mt-0.5 text-[11px] text-gray-400 md:text-xs">家計簿の履歴と管理</p>
          </div>

               <div class="hidden md:flex md:items-center md:gap-2 md:w-auto">
            <Button
              icon="pi pi-chart-bar"
              @click="router.push('/analytics')"
              label="レポート"
              :pt="{
                root: { class: 'bg-white hover:bg-gray-50 text-gray-700 font-medium py-2 px-4 rounded-lg border border-gray-200 transition duration-200 flex items-center gap-2 cursor-pointer shadow-sm' },
                label: { class: 'text-sm' },
                icon: { class: 'text-sm text-blue-500' }
              }"
            />
                  <Button
                     icon="pi pi-calculator"
                     @click="router.push('/settlement')"
                     label="精算"
                     :pt="{
                        root: { class: 'bg-white hover:bg-gray-50 text-gray-700 font-medium py-2 px-4 rounded-lg border border-gray-200 transition duration-200 flex items-center gap-2 cursor-pointer shadow-sm' },
                        label: { class: 'text-sm' },
                        icon: { class: 'text-sm text-emerald-500' }
                     }"
                  />
            <div class="h-8 w-px bg-gray-200 mx-1 hidden md:block"></div>
            <Button
              :icon="isFilterVisible ? 'pi pi-filter-slash' : 'pi pi-filter'"
              @click="isFilterVisible = !isFilterVisible"
              :pt="{
                root: { class: [
                  'p-2 rounded-lg border transition-all duration-200 cursor-pointer',
                  isFilterVisible ? 'bg-blue-50 border-blue-200 text-blue-600' : 'bg-white border-gray-200 text-gray-600 hover:border-gray-300 shadow-sm'
                ] }
              }"
            />

            <div class="h-8 w-px bg-gray-200 mx-1 hidden md:block"></div>
            <input type="file" ref="fileInput" accept="application/pdf" class="hidden" @change="handleFileUpload">
            <Button
              label="PDF登録"
              icon="pi pi-upload"
              @click="triggerFileInput"
              :pt="{
                root: { class: 'bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-medium py-2 px-4 rounded-lg transition duration-200 flex items-center gap-2 cursor-pointer border border-indigo-100' },
                label: { class: 'text-sm' },
                icon: { class: 'text-sm' },
              }"
            />
            <Button
              label="新規作成"
              icon="pi pi-plus"
                     @click="openCreateModal"
              :pt="{
                root: { class: 'bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-5 rounded-lg shadow-sm transition duration-200 flex items-center gap-2 cursor-pointer' },
                label: { class: 'text-sm' },
                icon: { class: 'text-sm' },
              }"
            />
          </div>

               <div class="grid w-full grid-cols-2 gap-1.5 md:hidden">
                  <Button
                     icon="pi pi-chart-bar"
                     @click="router.push('/analytics')"
                     label="レポート"
                     :pt="{
                        root: { class: 'min-h-[46px] justify-center rounded-xl border border-gray-200 bg-white px-2.5 py-2 text-gray-700 shadow-sm transition duration-200 hover:bg-gray-50' },
                        label: { class: 'text-[13px] font-semibold' },
                        icon: { class: 'text-[13px] text-blue-500 mr-1.5' }
                     }"
                  />
                  <Button
                     icon="pi pi-calculator"
                     @click="router.push('/settlement')"
                     label="精算"
                     :pt="{
                        root: { class: 'min-h-[46px] justify-center rounded-xl border border-gray-200 bg-white px-2.5 py-2 text-gray-700 shadow-sm transition duration-200 hover:bg-gray-50' },
                        label: { class: 'text-[13px] font-semibold' },
                        icon: { class: 'text-[13px] text-emerald-500 mr-1.5' }
                     }"
                  />
                  <Button
                     :icon="isFilterVisible ? 'pi pi-filter-slash' : 'pi pi-filter'"
                     @click="isFilterVisible = !isFilterVisible"
                     :label="isFilterVisible ? '絞り込みを閉じる' : '絞り込み'"
                     :pt="{
                        root: { class: [
                           'min-h-[46px] justify-center rounded-xl border px-2.5 py-2 shadow-sm transition duration-200',
                           isFilterVisible ? 'bg-blue-50 border-blue-200 text-blue-600' : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
                        ] },
                        label: { class: 'text-[13px] font-semibold' },
                        icon: { class: 'text-[13px] mr-1.5' }
                     }"
                  />
                  <Button
                     label="PDF登録"
                     icon="pi pi-upload"
                     @click="triggerFileInput"
                     :pt="{
                        root: { class: 'min-h-[46px] justify-center rounded-xl border border-indigo-100 bg-indigo-50 px-2.5 py-2 text-indigo-700 shadow-sm transition duration-200 hover:bg-indigo-100' },
                        label: { class: 'text-[13px] font-semibold' },
                        icon: { class: 'text-[13px] mr-1.5' },
                     }"
                  />
                  <input type="file" ref="fileInput" accept="application/pdf" class="hidden" @change="handleFileUpload">
                  <Button
                     label="新規作成"
                     icon="pi pi-plus"
                     @click="openCreateModal"
                     :pt="{
                        root: { class: 'col-span-2 min-h-[48px] justify-center rounded-xl bg-blue-600 px-3 py-2 text-white shadow-sm transition duration-200 hover:bg-blue-700' },
                        label: { class: 'text-[13px] font-semibold' },
                        icon: { class: 'text-[13px] mr-1.5' },
                     }"
                  />
               </div>
       </div>

       <!-- Mobile/Small Screen Stats Bar -->
      <div class="lg:hidden flex items-center justify-around bg-white border border-gray-200 rounded-lg py-1 px-3 shadow-sm mb-3">
          <div class="flex flex-col items-center">
             <span class="text-[9px] text-gray-400 font-bold uppercase tracking-[0.18em]">総合計支出</span>
             <span class="text-sm font-bold text-blue-600 leading-tight">{{ formatCurrency(totalAmount) }}</span>
          </div>
          <div class="w-px h-5 bg-gray-100"></div>
          <div class="flex flex-col items-center">
             <span class="text-[9px] text-gray-400 font-bold uppercase tracking-[0.18em]">登録件数</span>
             <span class="text-sm font-bold text-green-600 leading-tight">{{ store.transactions.length }}<span class="text-[9px] ml-0.5">件</span></span>
          </div>
       </div>

       <!-- Filter Section (Collapsible & Compact) -->
       <Transition
         enter-active-class="transition duration-200 ease-out"
         enter-from-class="transform -translate-y-2 opacity-0"
         enter-to-class="transform translate-y-0 opacity-100"
         leave-active-class="transition duration-150 ease-in"
         leave-from-class="transform translate-y-0 opacity-100"
         leave-to-class="transform -translate-y-2 opacity-0"
       >
         <div v-if="isFilterVisible" class="bg-white rounded-xl border border-blue-100 shadow-sm p-5 mb-8">
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3">
               <div class="flex flex-col gap-1">
                  <label class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">開始日</label>
                  <input type="date" v-model="filters.start_date" class="border border-gray-200 rounded px-2 py-1.5 text-sm focus:ring-1 focus:ring-blue-400 outline-none hover:border-gray-300">
               </div>
               <div class="flex flex-col gap-1">
                  <label class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">終了日</label>
                  <input type="date" v-model="filters.end_date" class="border border-gray-200 rounded px-2 py-1.5 text-sm focus:ring-1 focus:ring-blue-400 outline-none hover:border-gray-300">
               </div>
               <div class="flex flex-col gap-1">
                  <label class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">カテゴリ</label>
                  <MultiSelect 
                    v-model="filters.category_ids" 
                    :options="store.categories" 
                    optionLabel="name" 
                    optionValue="id" 
                    placeholder="カテゴリ選択" 
                    :maxSelectedLabels="3"
                    class="w-full text-sm"
                    :pt="{
                        root: { class: 'border border-gray-200 rounded px-2 py-0.5 text-sm focus:ring-1 focus:ring-blue-400 outline-none h-[34px] bg-white hover:border-gray-300 flex items-center' },
                        labelContainer: { class: 'flex-1 overflow-hidden' },
                        label: { class: 'text-xs truncate' },
                        trigger: { class: 'w-4' },
                        token: { class: 'bg-blue-50 text-blue-600 text-[10px] py-0.5 px-1.5 rounded border border-blue-100' }
                    }"
                  />
               </div>
               <div class="flex flex-col gap-1">
                  <label class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">支払者</label>
                  <select v-model="filters.payer" class="border border-gray-200 rounded px-2 py-1.5 text-sm focus:ring-1 focus:ring-blue-400 outline-none h-[34px] bg-white hover:border-gray-300">
                     <option value="">すべて</option>
                     <option v-for="p in store.payers" :key="p.id" :value="p.name">{{ p.name }}</option>
                  </select>
               </div>
               <div class="flex flex-col gap-1">
                  <label class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">支出タイプ</label>
                  <select v-model="filters.expense_type_id" class="border border-gray-200 rounded px-2 py-1.5 text-sm focus:ring-1 focus:ring-blue-400 outline-none h-[34px] bg-white hover:border-gray-300">
                     <option value="">すべて</option>
                     <option v-for="expenseType in store.expenseTypes" :key="expenseType.id" :value="expenseType.id">{{ expenseType.name }}</option>
                  </select>
               </div>
               <div class="flex flex-col gap-1">
                  <label class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">キーワード</label>
                  <input type="text" v-model="filters.keyword" placeholder="店舗名・内容" class="border border-gray-200 rounded px-2 py-1.5 text-sm focus:ring-1 focus:ring-blue-400 outline-none hover:border-gray-300">
               </div>
            </div>
            <div class="flex justify-end mt-4 gap-2">
               <button 
                  class="text-xs font-semibold text-gray-500 hover:text-gray-700 px-3 py-1.5 transition-colors"
                  @click="handleReset"
               >
                  <i class="pi pi-refresh text-[10px] mr-1"></i> リセット
               </button>
               <Button 
                  label="この条件で検索" 
                  icon="pi pi-search" 
                  @click="handleSearch"
                  size="small"
                  :pt="{
                     root: { class: 'bg-blue-600 hover:bg-blue-700 text-white font-medium py-1.5 px-4 rounded shadow-sm text-xs cursor-pointer' },
                     icon: { class: 'mr-1 text-[10px]' }
                  }"
               />
            </div>
         </div>
       </Transition>

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

        <!-- Main List Section (With Height Management) -->
        <div class="flex-1 flex flex-col min-h-0 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div class="px-5 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
             <h2 class="text-sm font-bold text-gray-700">取引履歴</h2>
             <span class="text-[10px] text-gray-400 font-bold uppercase tracking-wider">最新順</span>
          </div>
          <div class="flex-1 overflow-hidden relative">
             <TransactionList 
               :transactions="store.transactions" 
               :categories="store.categories"
                      @edit="openEditModal"
               @delete="store.deleteTransaction"
             />
          </div>
        </div>

    </div>

    <!-- Modal Form -->
    <TransactionForm 
      :isOpen="isModalOpen" 
         :mode="modalMode"
         :selectedTransaction="selectedTransaction"
         @close="handleModalClose" 
    />
  </div>
</template>

<style scoped>
/* Tailwind handles the styles */
</style>
