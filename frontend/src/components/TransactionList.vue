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
  <div class="bg-white shadow rounded-lg overflow-hidden">
    <DataTable
      :value="transactions"
      stripedRows
      :pt="{
        root: { class: 'w-full' },
        table: { class: 'min-w-full divide-y divide-gray-200 text-left' },
        thead: { class: 'bg-gray-50' },
        tbody: { class: 'bg-white divide-y divide-gray-200' },
        row: { class: 'hover:bg-gray-50 transition-colors' },
        emptyMessage: { class: 'text-center' },
      }"
    >
      <Column
        field="date"
        header="日付"
        :pt="{
          headerCell: { class: 'px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider' },
          bodyCell: { class: 'px-6 py-2 whitespace-nowrap text-sm text-gray-900' },
        }"
      />
      <Column
        header="カテゴリ"
        :pt="{
          headerCell: { class: 'px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider' },
          bodyCell: { class: 'px-6 py-2 whitespace-nowrap text-sm text-gray-500' },
        }"
      >
        <template #body="{ data }">
          <Tag
            :value="getCategoryName(data.category_id)"
            :pt="{
              root: { class: 'px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800' },
            }"
          />
        </template>
      </Column>
      <Column
        header="店舗 / 内容"
        :pt="{
          headerCell: { class: 'px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider' },
          bodyCell: { class: 'px-6 py-2 whitespace-nowrap text-sm text-gray-900' },
        }"
      >
        <template #body="{ data }">
          <div class="font-medium">{{ data.shop }}</div>
          <div class="text-xs text-gray-500">{{ data.content }}</div>
        </template>
      </Column>
      <Column
        header="金額"
        :pt="{
          headerCell: { class: 'px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider text-right' },
          bodyCell: { class: 'px-6 py-2 whitespace-nowrap text-sm font-semibold text-gray-900 text-right' },
        }"
      >
        <template #body="{ data }">{{ formatCurrency(data.amount) }}</template>
      </Column>
      <Column
        field="payer"
        header="支払者"
        :pt="{
          headerCell: { class: 'px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider' },
          bodyCell: { class: 'px-6 py-2 whitespace-nowrap text-sm text-gray-500' },
        }"
      />
      <Column
        header=""
        :pt="{
          headerCell: { class: 'relative px-6 py-3' },
          bodyCell: { class: 'px-6 py-2 whitespace-nowrap text-right text-sm font-medium' },
        }"
      >
        <template #body="{ data }">
          <Button
            icon="pi pi-trash"
            aria-label="削除"
            @click="emit('delete', data.id)"
            :pt="{
              root: { class: 'text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50 transition-colors cursor-pointer' },
              icon: { class: 'text-base' },
            }"
          />
        </template>
      </Column>

      <template #empty>
        <td colspan="6" class="px-6 py-10 text-center text-gray-500">データがありません。</td>
      </template>
    </DataTable>
  </div>
</template>
