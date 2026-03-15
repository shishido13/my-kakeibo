<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useImportStore } from '@/stores/useImportStore'
import { useTransactionStore } from '@/stores/transaction'
import Button from 'primevue/button'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Checkbox from 'primevue/checkbox'

const router = useRouter()
const importStore = useImportStore()
const transactionStore = useTransactionStore()

onMounted(async () => {
    // Ensure masters are loaded
    if (transactionStore.categories.length === 0) {
        await transactionStore.fetchCategories()
    }
    if (transactionStore.payers.length === 0) {
        await transactionStore.fetchPayers()
    }
    
    // If we land here and no file is set, redirect to home
    if (!importStore.originalFile) {
        router.push('/')
    }
})

const goBack = () => {
    importStore.clearDrafts()
    router.push('/')
}

const confirmAndSave = async () => {
    try {
        await importStore.registerAll()
        alert('登録が完了しました！')
        router.push('/')
    } catch (e) {
        alert('登録中にエラーが発生しました')
    }
}

const removeRow = (index: number) => {
    importStore.pendingTransactions.splice(index, 1)
}

const selectedRows = ref<Set<number>>(new Set())

const toggleRow = (index: number) => {
    if (selectedRows.value.has(index)) {
        selectedRows.value.delete(index)
    } else {
        selectedRows.value.add(index)
    }
}

const toggleAll = (e: Event) => {
    const checked = (e.target as HTMLInputElement).checked
    if (checked) {
        importStore.pendingTransactions.forEach((_, i) => selectedRows.value.add(i))
    } else {
        selectedRows.value.clear()
    }
}

const allSelected = computed(() => {
    return importStore.pendingTransactions.length > 0 && selectedRows.value.size === importStore.pendingTransactions.length
})

const bulkCategory = ref<number | ''>('')
const bulkPayer = ref<string>('')

const applyBulkChanges = () => {
    if (selectedRows.value.size === 0) return alert('適用する行を選択してください')
    
    selectedRows.value.forEach(index => {
        const item = importStore.pendingTransactions[index]
        if (bulkCategory.value) item.category_id = bulkCategory.value as number
        if (bulkPayer.value) item.payer = bulkPayer.value
    })
    
    bulkCategory.value = ''
    bulkPayer.value = ''
}

/** Shared pt definitions */
const checkboxPt = {
  root: { class: 'flex items-center' },
  box: { class: 'w-4 h-4 rounded border border-gray-300 flex items-center justify-center cursor-pointer data-[p-checked=true]:bg-blue-600 data-[p-checked=true]:border-blue-600' },
  icon: { class: 'text-white text-xs' },
}
const selectPt = {
  root: { class: 'text-sm border border-gray-300 rounded p-1 bg-white cursor-pointer flex items-center gap-1 min-w-[120px]' },
  label: { class: 'text-sm text-gray-700 flex-1' },
  panel: { class: 'bg-white border border-gray-200 rounded shadow-lg z-50 text-sm' },
  list: { class: 'py-1 max-h-48 overflow-auto' },
  option: { class: 'px-3 py-1.5 hover:bg-blue-50 cursor-pointer data-[p-selected=true]:bg-blue-100 data-[p-selected=true]:text-blue-700' },
}
const inlineInputPt = { root: { class: 'w-full border border-gray-300 rounded p-1 focus:ring focus:ring-blue-200 outline-none text-sm' } }
</script>

<template>
  <div class="h-screen flex flex-col bg-gray-100">
    <!-- Header -->
    <header class="bg-blue-600 text-white px-4 py-3 flex justify-between items-center shrink-0">
      <div class="flex items-center space-x-4">
        <Button
          icon="pi pi-arrow-left"
          aria-label="戻る"
          @click="goBack"
          :pt="{
            root: { class: 'text-white hover:text-gray-200 cursor-pointer rounded p-1' },
            icon: { class: 'text-lg' },
          }"
        />
        <h1 class="text-lg font-bold">データ化確認 ({{ importStore.originalFile?.name }})</h1>
      </div>
      <div>
        <Button
          :label="importStore.isAnalyzing ? '処理中...' : 'DBへ登録'"
          :disabled="importStore.isAnalyzing || importStore.pendingTransactions.length === 0"
          @click="confirmAndSave"
          :pt="{
            root: { class: 'bg-green-500 hover:bg-green-600 px-4 py-2 rounded font-bold disabled:opacity-50 transition-colors cursor-pointer text-white' },
          }"
        />
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 flex overflow-hidden">
        
       <!-- Left Pane: PDF Viewer -->
       <section class="w-1/3 border-r border-gray-300 bg-gray-50 flex flex-col">
           <div class="p-2 bg-gray-200 text-sm font-semibold text-gray-700 shrink-0">原本プレビュー</div>
           <div class="flex-1 overflow-hidden">
               <object v-if="importStore.pdfUrl" :data="importStore.pdfUrl" type="application/pdf" class="w-full h-full"></object>
               <div v-else class="flex h-full items-center justify-center text-gray-400">PDFが見つかりません</div>
           </div>
       </section>

       <!-- Right Pane: Data Table -->
       <section class="w-2/3 flex flex-col bg-white">
           <!-- Toolbar -->
           <div class="p-3 bg-gray-50 border-b border-gray-200 flex items-center space-x-4 shrink-0">
               <span class="text-sm font-semibold text-gray-700 mr-2">一括操作:</span>
               <Select
                 v-model="bulkCategory"
                 :options="transactionStore.categories"
                 optionLabel="name"
                 optionValue="id"
                 placeholder="カテゴリ変更..."
                 :pt="selectPt"
               />
               <Select
                 v-model="bulkPayer"
                 :options="transactionStore.payers"
                 optionLabel="name"
                 optionValue="name"
                 placeholder="支払者変更..."
                 :pt="selectPt"
               />
               <Button
                 label="適用"
                 @click="applyBulkChanges"
                 :pt="{
                   root: { class: 'text-sm bg-gray-200 hover:bg-gray-300 px-4 py-1.5 rounded text-black font-semibold cursor-pointer' },
                 }"
               />
           </div>
           
           <div class="flex-1 overflow-auto p-4">
               
               <div v-if="importStore.isAnalyzing" class="flex flex-col items-center justify-center h-full text-blue-600">
                   <svg class="animate-spin h-10 w-10 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                   </svg>
                   <p class="font-bold text-lg">AIがPDFを解析しています...</p>
                   <p class="text-sm text-gray-500 mt-2">しばらくお待ちください（通常数秒〜十数秒かかります）</p>
               </div>

               <table v-else class="min-w-full text-sm">
                   <thead>
                       <tr class="bg-gray-100 text-left">
                           <th class="p-2 w-8 border-b">
                             <Checkbox
                               :modelValue="allSelected"
                               binary
                               @change="toggleAll"
                               :pt="checkboxPt"
                             />
                           </th>
                           <th class="p-2 w-32 border-b">日付</th>
                           <th class="p-2 w-32 border-b">カテゴリ</th>
                           <th class="p-2 w-24 border-b">金額</th>
                           <th class="p-2 border-b">店舗</th>
                           <th class="p-2 border-b">商品・サービス</th>
                           <th class="p-2 w-24 border-b">支払者</th>
                           <th class="p-2 w-10 border-b"></th>
                       </tr>
                   </thead>
                   <tbody>
                       <tr
                         v-for="(item, index) in importStore.pendingTransactions"
                         :key="index"
                         class="border-b hover:bg-gray-50 transition-colors"
                         :class="{'bg-blue-50': selectedRows.has(index)}"
                       >
                           <td class="p-2">
                             <Checkbox
                               :modelValue="selectedRows.has(index)"
                               binary
                               @change="toggleRow(index)"
                               :pt="checkboxPt"
                             />
                           </td>
                           <td class="p-2">
                             <InputText
                               v-model="item.date"
                               type="date"
                               :pt="inlineInputPt"
                             />
                           </td>
                           <td class="p-2">
                             <Select
                               v-model="item.category_id"
                               :options="transactionStore.categories"
                               optionLabel="name"
                               optionValue="id"
                               :pt="{
                                 root: { class: 'w-full border border-gray-300 rounded p-1 bg-white cursor-pointer flex items-center gap-1 text-sm' },
                                 label: { class: 'flex-1 text-sm text-gray-700' },
                                 panel: { class: 'bg-white border border-gray-200 rounded shadow-lg z-50 text-sm' },
                                 list: { class: 'py-1 max-h-48 overflow-auto' },
                                 option: { class: 'px-3 py-1.5 hover:bg-blue-50 cursor-pointer data-[p-selected=true]:bg-blue-100' },
                               }"
                             />
                           </td>
                           <td class="p-2">
                             <InputNumber
                               v-model="item.amount"
                               :useGrouping="false"
                               :pt="{
                                 root: { class: 'w-full' },
                                 input: { class: 'w-full border border-gray-300 rounded p-1 text-right focus:ring focus:ring-blue-200 outline-none text-sm' },
                               }"
                             />
                           </td>
                           <td class="p-2">
                             <InputText v-model="item.shop" :pt="inlineInputPt" />
                           </td>
                           <td class="p-2">
                             <InputText v-model="item.content" :pt="inlineInputPt" />
                           </td>
                           <td class="p-2">
                             <InputText v-model="item.payer" :pt="inlineInputPt" />
                           </td>
                           <td class="p-2 text-center">
                             <Button
                               label="✕"
                               title="削除"
                               @click="removeRow(index)"
                               :pt="{
                                 root: { class: 'text-red-500 hover:text-red-700 font-bold px-2 py-1 rounded hover:bg-red-100 cursor-pointer' },
                               }"
                             />
                           </td>
                       </tr>
                       <tr v-if="importStore.pendingTransactions.length === 0 && !importStore.isAnalyzing">
                           <td colspan="8" class="text-center p-8 text-gray-500">データが見つかりません。再解析するか手動で追加してください。</td>
                       </tr>
                   </tbody>
               </table>
           </div>
       </section>
    </main>
  </div>
</template>
