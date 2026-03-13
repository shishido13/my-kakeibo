import { defineStore } from 'pinia'
import api from '../services/api'

export const useTransactionStore = defineStore('transactions', {
  state: () => ({
    transactions: [],
    categories: [],
    payers: [],
    isLoading: false,
    error: null
  }),
  actions: {
    async fetchTransactions() {
      this.isLoading = true
      try {
        const response = await api.get('/transactions/')
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
    async addTransaction(transactionData) {
      try {
        const response = await api.post('/transactions/', transactionData)
        this.transactions.unshift(response.data) // Add new item to front of list
        return true
      } catch (error) {
        this.error = error
        return false
      }
    },
    async deleteTransaction(id) {
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
