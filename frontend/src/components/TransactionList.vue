<script setup lang="ts">
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Button from 'primevue/button';

interface Transaction {
  id: number;
  date: string;
  category_id: number;
  shop: string;
  content: string;
  amount: number;
  payer: string;
}

interface Category {
  id: number;
  name: string;
}

const props = defineProps<{
  transactions: Transaction[];
  categories: Category[];
}>();

const emit = defineEmits<{
  (e: 'delete', id: number): void
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
  <div class="h-full w-full">
    <DataTable
      :value="transactions"
      stripedRows
      scrollable
      scrollHeight="flex"
      size="small"
      :pt="{
        root: { class: 'w-full h-full flex flex-col' },
        table: { class: 'min-w-full divide-y divide-gray-200 text-left border-collapse' },
        thead: { class: 'sticky top-0 z-10 bg-gray-50' },
        tbody: { class: 'bg-white divide-y divide-gray-200 flex-1' },
        row: { class: 'hover:bg-blue-50/30 transition-colors group' },
        emptyMessage: { class: 'text-center' },
      }"
    >
      <Column
        field="date"
        header="日付"
        :pt="{
          headerCell: { class: 'px-4 py-3 text-[10px] font-bold text-gray-400 uppercase tracking-widest bg-gray-50 border-b border-gray-200' },
          bodyCell: { class: 'px-4 py-2.5 whitespace-nowrap text-xs text-gray-600 font-medium' },
        }"
      />
      <Column
        header="カテゴリ"
        :pt="{
          headerCell: { class: 'px-4 py-3 text-[10px] font-bold text-gray-400 uppercase tracking-widest bg-gray-50 border-b border-gray-200' },
          bodyCell: { class: 'px-4 py-2.5 whitespace-nowrap text-xs text-gray-500' },
        }"
      >
        <template #body="{ data }">
          <Tag
            :value="getCategoryName(data.category_id)"
            :pt="{
              root: { class: 'px-2 py-0.5 inline-flex text-[10px] leading-4 font-bold rounded bg-blue-50 text-blue-600 border border-blue-100' },
            }"
          />
        </template>
      </Column>
      <Column
        header="店舗 / 内容"
        :pt="{
          headerCell: { class: 'px-4 py-3 text-[10px] font-bold text-gray-400 uppercase tracking-widest bg-gray-50 border-b border-gray-200' },
          bodyCell: { class: 'px-4 py-2.5 text-xs text-gray-900 max-w-[300px]' },
        }"
      >
        <template #body="{ data }">
          <div class="font-bold text-gray-800 truncate">{{ data.shop }}</div>
          <div class="text-[10px] text-gray-400 truncate mt-0.5">{{ data.content }}</div>
        </template>
      </Column>
      <Column
        header="金額"
        :pt="{
          headerCell: { class: 'px-4 py-3 text-[10px] font-bold text-gray-400 uppercase tracking-widest bg-gray-50 border-b border-gray-200 text-right' },
          bodyCell: { class: 'px-4 py-2.5 whitespace-nowrap text-sm font-black text-gray-900 text-right font-mono' },
        }"
      >
        <template #body="{ data }">{{ formatCurrency(data.amount) }}</template>
      </Column>
      <Column
        field="payer"
        header="支払者"
        :pt="{
          headerCell: { class: 'px-4 py-3 text-[10px] font-bold text-gray-400 uppercase tracking-widest bg-gray-50 border-b border-gray-200' },
          bodyCell: { class: 'px-4 py-2.5 whitespace-nowrap text-xs text-gray-500 font-medium' },
        }"
      />
      <Column
        header=""
        :pt="{
          headerCell: { class: 'px-4 py-3 bg-gray-50 border-b border-gray-200 w-12' },
          bodyCell: { class: 'px-4 py-2.5 whitespace-nowrap text-right text-xs' },
        }"
      >
        <template #body="{ data }">
          <Button
            icon="pi pi-trash"
            aria-label="削除"
            @click="emit('delete', data.id)"
            plain
            text
            :pt="{
              root: { class: 'text-gray-300 hover:text-red-500 p-1.5 rounded-full hover:bg-red-50 transition-all cursor-pointer' },
              icon: { class: 'text-xs' },
            }"
          />
        </template>
      </Column>

      <template #empty>
        <div class="flex flex-col items-center justify-center py-20 bg-gray-50/30 rounded-lg mx-4 my-8 border border-dashed border-gray-200">
           <i class="pi pi-inbox text-3xl text-gray-300 mb-3"></i>
           <span class="text-sm font-medium text-gray-400 uppercase tracking-widest">データがありません</span>
        </div>
      </template>
    </DataTable>
  </div>
</template>
