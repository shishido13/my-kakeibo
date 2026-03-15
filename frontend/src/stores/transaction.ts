import { defineStore } from 'pinia'
import api from '../services/api'

interface Category { id: number; name: string; }
interface Payer { id: number; name: string; }

export const useTransactionStore = defineStore('transactions', {
  state: () => ({
    transactions: [] as any[],
    categories: [] as Category[],
    payers: [] as Payer[],
    isLoading: false,
    error: null as any
  }),
  actions: {
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
    async addTransaction(transactionData: any) {
      try {
        const response = await api.post('/transactions/', transactionData)
        this.transactions.unshift(response.data) // Add new item to front of list
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
        return true
       } catch (error) {
        this.error = error
        return false
       }
    }
  }
})
