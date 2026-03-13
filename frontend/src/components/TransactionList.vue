<script setup lang="ts">

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
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200 text-left">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">日付</th>
            <th scope="col" class="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">カテゴリ</th>
            <th scope="col" class="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">店舗 / 内容</th>
            <th scope="col" class="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider text-right">金額</th>
            <th scope="col" class="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">支払者</th>
            <th scope="col" class="relative px-6 py-3"><span class="sr-only">操作</span></th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-if="transactions.length === 0">
             <td colspan="6" class="px-6 py-10 text-center text-gray-500">データがありません。</td>
          </tr>
          <tr v-for="transaction in transactions" :key="transaction.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ transaction.date }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
               <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                 {{ getCategoryName(transaction.category_id) }}
               </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
               <div class="font-medium">{{ transaction.shop }}</div>
               <div class="text-xs text-gray-500">{{ transaction.content }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900 text-right">{{ formatCurrency(transaction.amount) }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ transaction.payer }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
               <button @click="emit('delete', transaction.id)" class="text-red-600 hover:text-red-900 p-1">
                 <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
               </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
