<script setup lang="ts">
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Button from 'primevue/button';
import type { Category, TransactionRecord } from '../stores/transaction';

const props = defineProps<{
  transactions: TransactionRecord[];
  categories: Category[];
}>();

const emit = defineEmits<{
  (e: 'delete', id: number): void
  (e: 'edit', transaction: TransactionRecord): void
}>();

const getCategoryName = (id: number) => {
  const category = props.categories.find((c: Category) => c.id === id);
  return category ? category.name : '不明';
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('ja-JP', { style: 'currency', currency: 'JPY' }).format(amount);
};

</script>

<template>
  <div class="h-full w-full overflow-x-auto">
    <DataTable
      :value="transactions"
      stripedRows
      scrollable
      size="small"
      :pt="{
        root: { class: 'flex min-w-[760px] flex-col md:h-full md:min-w-full' },
        table: { class: 'min-w-[760px] border-collapse text-left md:min-w-full' },
        thead: { class: 'sticky top-0 z-10 bg-surface' },
        tbody: { class: 'bg-panel flex-1' },
        row: { class: 'border-b border-line transition-colors hover:bg-[#f7f9fb] group' },
        emptyMessage: { class: 'text-center' },
      }"
    >
      <Column
        field="date"
        header="日付"
        :pt="{
          headerCell: { class: 'border-b border-line bg-surface px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted md:px-4 md:py-2.5' },
          bodyCell: { class: 'px-3 py-2 whitespace-nowrap text-[11px] font-medium text-ink-soft fin-table-cell-number md:px-4 md:py-2.5 md:text-[12px]' },
        }"
      />
      <Column
        header="カテゴリ"
        :pt="{
          headerCell: { class: 'border-b border-line bg-surface px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted md:px-4 md:py-2.5' },
          bodyCell: { class: 'px-3 py-2 whitespace-nowrap text-[11px] text-ink-soft md:px-4 md:py-2.5 md:text-[12px]' },
        }"
      >
        <template #body="{ data }">
          <Tag
            :value="getCategoryName(data.category_id)"
            :pt="{
              root: { class: 'inline-flex rounded-[8px] border border-[#d6dee7] bg-[#edf2f7] px-2 py-0.5 text-[10px] font-semibold leading-4 text-[#35506a]' },
            }"
          />
        </template>
      </Column>
      <Column
        header="店舗 / 内容"
        :pt="{
          headerCell: { class: 'border-b border-line bg-surface px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted md:px-4 md:py-2.5' },
          bodyCell: { class: 'max-w-[240px] px-3 py-2 text-[11px] text-ink md:max-w-[320px] md:px-4 md:py-2.5 md:text-[12px]' },
        }"
      >
        <template #body="{ data }">
          <div class="truncate text-[12px] font-semibold tracking-[-0.015em] text-ink">{{ data.shop }}</div>
          <div class="mt-0.5 truncate text-[10px] text-muted">{{ data.content }}</div>
        </template>
      </Column>
      <Column
        header="金額"
        :pt="{
          headerCell: { class: 'border-b border-line bg-surface px-3 py-2 text-right text-[10px] font-semibold uppercase tracking-[0.12em] text-muted md:px-4 md:py-2.5' },
          bodyCell: { class: 'fin-table-cell-number px-3 py-2 whitespace-nowrap text-right text-[12px] font-semibold text-ink md:px-4 md:py-2.5 md:text-[13px]' },
        }"
      >
        <template #body="{ data }">{{ formatCurrency(data.amount) }}</template>
      </Column>
      <Column
        field="payer"
        header="支払者"
        :pt="{
          headerCell: { class: 'border-b border-line bg-surface px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted md:px-4 md:py-2.5' },
          bodyCell: { class: 'px-3 py-2 whitespace-nowrap text-[11px] font-medium text-ink-soft md:px-4 md:py-2.5 md:text-[12px]' },
        }"
      />
      <Column
        header="支出タイプ"
        :pt="{
          headerCell: { class: 'border-b border-line bg-surface px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-muted md:px-4 md:py-2.5' },
          bodyCell: { class: 'px-3 py-2 whitespace-nowrap text-[11px] font-medium text-ink-soft md:px-4 md:py-2.5 md:text-[12px]' },
        }"
      >
        <template #body="{ data }">
          <Tag
            :value="data.expense_type_name"
            :pt="{
              root: { class: 'inline-flex rounded-[8px] border border-[#d3dfd5] bg-[#e8efe9] px-2 py-0.5 text-[10px] font-semibold leading-4 text-[#4f6f5e]' },
            }"
          />
        </template>
      </Column>
      <Column
        header=""
        :pt="{
          headerCell: { class: 'w-20 border-b border-line bg-surface px-3 py-2 md:w-24 md:px-4 md:py-2.5' },
          bodyCell: { class: 'px-3 py-2 whitespace-nowrap text-right text-[11px] md:px-4 md:py-2.5 md:text-[12px]' },
        }"
      >
        <template #body="{ data }">
          <div class="flex items-center justify-end gap-1">
            <Button
              icon="pi pi-pencil"
              aria-label="編集"
              @click="emit('edit', data)"
              plain
              text
              :pt="{
                root: { class: 'rounded-[8px] border border-transparent p-1.5 text-muted transition-all cursor-pointer hover:border-[#d6dee7] hover:bg-[#edf2f7] hover:text-[#35506a]' },
                icon: { class: 'text-[11px]' },
              }"
            />
            <Button
              icon="pi pi-trash"
              aria-label="削除"
              @click="emit('delete', data.id)"
              plain
              text
              :pt="{
                root: { class: 'rounded-[8px] border border-transparent p-1.5 text-muted transition-all cursor-pointer hover:border-[#e3d2d3] hover:bg-[#f2e7e7] hover:text-[#7b4f53]' },
                icon: { class: 'text-[11px]' },
              }"
            />
          </div>
        </template>
      </Column>

      <template #empty>
        <div class="mx-4 my-8 flex flex-col items-center justify-center rounded-[12px] border border-dashed border-line bg-surface px-6 py-16">
           <i class="pi pi-inbox mb-3 text-[28px] text-muted"></i>
           <span class="fin-label">No Transactions</span>
           <span class="mt-2 text-[12px] text-muted">表示できるデータがありません。</span>
        </div>
      </template>
    </DataTable>
  </div>
</template>
