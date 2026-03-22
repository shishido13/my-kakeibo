<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useImportStore } from '../stores/useImportStore'
import { useTransactionStore } from '../stores/transaction'
import Button from 'primevue/button'
import Select from 'primevue/select'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Checkbox from 'primevue/checkbox'

const router = useRouter()
const importStore = useImportStore()
const transactionStore = useTransactionStore()
const workspaceScroller = ref<HTMLElement | null>(null)

const alignWorkspaceForMobile = () => {
  if (typeof window === 'undefined') {
    return
  }

  const container = workspaceScroller.value
  if (!container) {
    return
  }

  if (window.innerWidth < 768) {
    container.scrollLeft = Math.max(0, container.scrollWidth - container.clientWidth)
    return
  }

  container.scrollLeft = 0
}

onMounted(async () => {
    // Ensure masters are loaded
    if (transactionStore.categories.length === 0) {
        await transactionStore.fetchCategories()
    }
    if (transactionStore.payers.length === 0) {
        await transactionStore.fetchPayers()
    }
  if (transactionStore.expenseTypes.length === 0) {
    await transactionStore.fetchExpenseTypes()
  }
    
    // If we land here and no file is set, redirect to home
    if (!importStore.originalFile) {
        router.push('/')
    }

    await nextTick()
    alignWorkspaceForMobile()

    if (typeof window !== 'undefined') {
      window.addEventListener('resize', alignWorkspaceForMobile)
    }
})

onUnmounted(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', alignWorkspaceForMobile)
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

const selectedCount = computed(() => selectedRows.value.size)

const bulkCategory = ref<number | ''>('')
const bulkPayer = ref<string>('')
const bulkExpenseType = ref<number | ''>('')

const applyBulkChanges = () => {
    if (selectedRows.value.size === 0) return alert('適用する行を選択してください')
    
    selectedRows.value.forEach(index => {
        const item = importStore.pendingTransactions[index]
        if (bulkCategory.value) item.category_id = bulkCategory.value as number
        if (bulkPayer.value) item.payer = bulkPayer.value
    if (bulkExpenseType.value) item.expense_type_id = bulkExpenseType.value as number
    })
    
    bulkCategory.value = ''
    bulkPayer.value = ''
  bulkExpenseType.value = ''
}

/** Shared pt definitions */
const checkboxPt = {
  root: { class: 'flex items-center' },
  box: { class: 'w-4 h-4 rounded border border-line flex items-center justify-center cursor-pointer data-[p-checked=true]:bg-accent data-[p-checked=true]:border-accent' },
  icon: { class: 'text-white text-xs' },
}
const selectPt = {
  root: { class: 'fin-select min-h-[32px] rounded-[9px] px-2 py-1 text-[12px] bg-panel cursor-pointer flex items-center gap-1 min-w-[120px]' },
  label: { class: 'text-[12px] text-ink-soft flex-1' },
  panel: { class: 'fin-panel rounded-[12px] shadow-lg z-50 text-[12px]' },
  list: { class: 'py-1 max-h-48 overflow-auto' },
  option: { class: 'px-3 py-1.5 hover:bg-[#eef2f6] cursor-pointer data-[p-selected=true]:bg-[#e7eef5] data-[p-selected=true]:text-accent-strong' },
}
const inlineInputPt = { root: { class: 'fin-input w-full rounded-[8px] px-2 py-1 text-[12px]' } }

const inlineSelectPt = {
  root: { class: 'fin-select w-full min-h-[32px] rounded-[8px] px-2 py-1 bg-panel cursor-pointer flex items-center gap-1 text-[12px]' },
  label: { class: 'flex-1 text-[12px] text-ink-soft' },
  panel: { class: 'fin-panel rounded-[12px] shadow-lg z-50 text-[12px]' },
  list: { class: 'py-1 max-h-48 overflow-auto' },
  option: { class: 'px-3 py-1.5 hover:bg-[#eef2f6] cursor-pointer data-[p-selected=true]:bg-[#e7eef5]' },
}

const buttonPt = {
  root: { class: 'fin-button rounded-[9px] px-2.5 py-1.5 text-[12px] font-semibold cursor-pointer' },
}

const primaryButtonPt = {
  root: { class: 'fin-button fin-button-primary rounded-[9px] px-2.5 py-1.5 text-[12px] font-semibold cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed' },
}

const accentButtonPt = {
  root: { class: 'fin-button fin-button-accent rounded-[9px] px-2.5 py-1.5 text-[12px] font-semibold cursor-pointer' },
}
</script>

<template>
  <div class="fin-page h-screen overflow-hidden">
    <div class="fin-frame flex h-full flex-col gap-2 px-3 py-3 sm:px-5 sm:py-5 lg:px-6">
      <section class="fin-panel flex min-h-0 flex-1 flex-col overflow-hidden rounded-panel">
        <div class="grid shrink-0 gap-2 border-b fin-hairline px-4 py-2.5 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
          <div class="space-y-1">
            <div class="flex flex-wrap items-end gap-x-3 gap-y-1">
              <h1 class="fin-title text-[22px] font-semibold leading-none">データ化確認</h1>
              <span class="fin-label">Import Verification Workspace</span>
            </div>
            <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] fin-subtle">
              <span>{{ importStore.originalFile?.name || 'アップロードファイル未設定' }}</span>
              <span class="hidden h-3 w-px bg-line sm:block"></span>
              <span>{{ importStore.pendingTransactions.length }}行</span>
              <span class="hidden h-3 w-px bg-line sm:block"></span>
              <span>{{ selectedCount }}行を選択</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <Button icon="pi pi-arrow-left" label="戻る" @click="goBack" :pt="buttonPt" />
            <Button :label="importStore.isAnalyzing ? '処理中...' : 'DBへ登録'" :disabled="importStore.isAnalyzing || importStore.pendingTransactions.length === 0" @click="confirmAndSave" :pt="primaryButtonPt" />
          </div>
        </div>

        <div ref="workspaceScroller" class="min-h-0 flex-1 overflow-auto">
          <div class="grid min-h-full min-w-[900px] gap-px bg-line grid-cols-[220px_minmax(680px,1fr)] lg:min-w-[1120px] lg:grid-cols-[340px_minmax(780px,1fr)]">
          <section class="flex min-h-0 flex-col bg-panel">
            <div class="flex items-center justify-between border-b fin-hairline bg-surface px-4 py-2.5">
              <div>
                <div class="fin-label">Original Preview</div>
                <div class="mt-1 text-[12px] font-semibold text-ink-soft">原本プレビュー</div>
              </div>
              <span class="text-[11px] text-muted">PDF</span>
            </div>
            <div class="min-h-0 flex-1 overflow-hidden bg-[linear-gradient(180deg,_rgba(1,118,211,0.03),_rgba(255,255,255,0))]">
              <object v-if="importStore.pdfUrl" :data="importStore.pdfUrl" type="application/pdf" class="h-full w-full"></object>
              <div v-else class="flex h-full items-center justify-center text-[12px] text-muted">PDFが見つかりません</div>
            </div>
          </section>

          <section class="flex min-h-0 flex-col bg-panel">
            <div class="grid shrink-0 gap-2 border-b fin-hairline bg-surface px-3 py-2 grid-cols-[auto_repeat(3,minmax(126px,1fr))_auto] items-center lg:px-4 lg:py-2.5 lg:grid-cols-[auto_repeat(3,minmax(150px,1fr))_auto]">
              <div>
                <div class="fin-label">Bulk Edit</div>
                <div class="mt-1 text-[11px] font-semibold text-ink-soft">選択行へ一括反映</div>
              </div>
              <Select v-model="bulkCategory" :options="transactionStore.categories" optionLabel="name" optionValue="id" placeholder="カテゴリ変更" :pt="selectPt" />
              <Select v-model="bulkPayer" :options="transactionStore.payers" optionLabel="name" optionValue="name" placeholder="支払者変更" :pt="selectPt" />
              <Select v-model="bulkExpenseType" :options="transactionStore.expenseTypes" optionLabel="name" optionValue="id" placeholder="支出タイプ変更" :pt="selectPt" />
              <div class="flex items-center gap-2 xl:justify-end">
                <Button label="適用" @click="applyBulkChanges" :pt="accentButtonPt" />
              </div>
            </div>

            <div class="min-h-0 flex-1 overflow-auto">
              <div v-if="importStore.isAnalyzing" class="flex h-full flex-col items-center justify-center px-6 text-accent-strong">
                <svg class="mb-4 h-10 w-10 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <p class="text-[16px] font-semibold text-ink">AIがPDFを解析しています...</p>
                <p class="mt-2 text-[12px] text-muted">通常は数秒から十数秒で完了します。</p>
              </div>

              <div v-else class="h-full overflow-auto">
                <table class="min-w-[680px] w-full border-collapse text-left lg:min-w-[780px]">
                  <thead class="sticky top-0 z-10 bg-surface">
                    <tr>
                      <th class="w-9 border-b border-line px-2 py-2">
                        <Checkbox :modelValue="allSelected" binary @change="toggleAll" :pt="checkboxPt" />
                      </th>
                      <th class="w-28 border-b border-line px-2 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted">日付</th>
                      <th class="w-32 border-b border-line px-2 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted">カテゴリ</th>
                      <th class="w-24 border-b border-line px-2 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted">金額</th>
                      <th class="w-28 border-b border-line px-2 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted">支出タイプ</th>
                      <th class="border-b border-line px-2 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted">店舗</th>
                      <th class="border-b border-line px-2 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted">商品・サービス</th>
                      <th class="w-24 border-b border-line px-2 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted">支払者</th>
                      <th class="w-12 border-b border-line px-2 py-2"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in importStore.pendingTransactions" :key="index" class="border-b border-line transition-colors hover:bg-[#f7f9fb]" :class="selectedRows.has(index) ? 'bg-[var(--app-accent-soft)]/60' : ''">
                      <td class="px-2 py-2 align-top">
                        <Checkbox :modelValue="selectedRows.has(index)" binary @change="toggleRow(index)" :pt="checkboxPt" />
                      </td>
                      <td class="px-2 py-2 align-top">
                        <InputText v-model="item.date" type="date" :pt="inlineInputPt" />
                      </td>
                      <td class="px-2 py-2 align-top">
                        <Select v-model="item.category_id" :options="transactionStore.categories" optionLabel="name" optionValue="id" :pt="inlineSelectPt" />
                      </td>
                      <td class="px-2 py-2 align-top">
                        <InputNumber v-model="item.amount" :useGrouping="false" :pt="{ root: { class: 'w-full' }, input: { class: 'fin-input fin-table-cell-number w-full rounded-[8px] px-2 py-1 text-right text-[12px]' } }" />
                      </td>
                      <td class="px-2 py-2 align-top">
                        <Select v-model="item.expense_type_id" :options="transactionStore.expenseTypes" optionLabel="name" optionValue="id" :pt="inlineSelectPt" />
                      </td>
                      <td class="px-2 py-2 align-top">
                        <InputText v-model="item.shop" :pt="inlineInputPt" />
                      </td>
                      <td class="px-2 py-2 align-top">
                        <InputText v-model="item.content" :pt="inlineInputPt" />
                      </td>
                      <td class="px-2 py-2 align-top">
                        <InputText v-model="item.payer" :pt="inlineInputPt" />
                      </td>
                      <td class="px-2 py-2 text-center align-top">
                        <Button icon="pi pi-trash" title="削除" @click="removeRow(index)" :pt="{ root: { class: 'rounded-[8px] border border-transparent p-1.5 text-muted transition-all cursor-pointer hover:border-[#e3d2d3] hover:bg-[#f2e7e7] hover:text-[#7b4f53]' }, icon: { class: 'text-[11px]' } }" />
                      </td>
                    </tr>
                    <tr v-if="importStore.pendingTransactions.length === 0 && !importStore.isAnalyzing">
                      <td colspan="9" class="px-6 py-16 text-center">
                        <div class="mx-auto flex max-w-[320px] flex-col items-center justify-center rounded-[12px] border border-dashed border-line bg-surface px-6 py-10">
                          <i class="pi pi-inbox mb-3 text-[28px] text-muted"></i>
                          <span class="fin-label">No Draft Rows</span>
                          <span class="mt-2 text-[12px] text-muted">データが見つかりません。再解析または手動修正を行ってください。</span>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
