import { defineStore } from 'pinia'
import api from '../services/api'

export interface Category { id: number; name: string; }
export interface Payer { id: number; name: string; }
export interface ExpenseType { id: number; name: string; }

export interface TransactionRecord {
  id: number;
  date: string;
  amount: number;
  category_id: number;
  expense_type_id: number;
  expense_type_name: string;
  shop: string;
  content: string;
  payer: string;
  description?: string | null;
  source_type?: string;
  created_at?: string;
}

export const useTransactionStore = defineStore('transactions', {
  state: () => ({
    transactions: [] as TransactionRecord[],
    categories: [] as Category[],
    payers: [] as Payer[],
    expenseTypes: [] as ExpenseType[],
    isLoading: false,
    error: null as any
  }),
  actions: {
    syncTransaction(transaction: TransactionRecord) {
      const existingIndex = this.transactions.findIndex((current) => current.id === transaction.id)

      if (existingIndex === -1) {
        this.transactions.unshift(transaction)
        return
      }

      this.transactions.splice(existingIndex, 1, transaction)
    },
    async fetchTransactions(filters: any = {}) {
      this.isLoading = true
      try {
        const response = await api.get('/transactions/', { 
          params: filters,
          paramsSerializer: {
            indexes: null // Serialize arrays as category_ids=1&category_ids=2
          }
        })
        this.transactions = response.data
        this.error = null
      } catch (error) {
        this.error = error
      } finally {
        this.isLoading = false
      }
    },
    async fetchCategories() {
      try {
        const response = await api.get('/categories/')
        this.categories = response.data
      } catch (error) {
        console.error(error)
      }
    },
    async fetchPayers() {
      try {
        const response = await api.get('/payers/')
        this.payers = response.data
      } catch (error) {
        console.error(error)
      }
    },
    async fetchExpenseTypes() {
      try {
        const response = await api.get('/expense-types/')
        this.expenseTypes = response.data
      } catch (error) {
        console.error(error)
      }
    },
    async addTransaction(transactionData: any) {
      try {
        const response = await api.post('/transactions/', transactionData)
        this.syncTransaction(response.data)
        this.transactions.sort((left, right) => right.date.localeCompare(left.date))
        // Add new item to front of list
        this.error = null
        return true
      } catch (error) {
        this.error = error
        return false
      }
    },
    async updateTransaction(id: number, transactionData: any) {
      try {
        const response = await api.put(`/transactions/${id}`, transactionData)
        this.syncTransaction(response.data)
        this.transactions.sort((left, right) => right.date.localeCompare(left.date))
        this.error = null
        return true
      } catch (error) {
        this.error = error
        return false
      }
    },
    async deleteTransaction(id: number) {
       try {
        await api.delete(`/transactions/${id}`)
         // Remove from local state
        this.transactions = this.transactions.filter(t => t.id !== id)
        this.error = null
        return true
       } catch (error) {
        this.error = error
        return false
       }
    }
  }
})
