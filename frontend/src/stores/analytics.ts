import { defineStore } from 'pinia'
import api from '../services/api'

export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    summary: null as any,
    trend: [] as any[],
    isLoading: false,
    error: null as any
  }),
  actions: {
    async fetchSummary(params: { start_date: string, end_date: string, compare?: boolean }) {
      this.isLoading = true
      try {
        const response = await api.get('/analytics/summary', { params })
        this.summary = response.data
      } catch (error) {
        this.error = error
      } finally {
        this.isLoading = false
      }
    },
    async fetchTrend(params: { start_date: string, end_date: string, group_by: string }) {
      this.isLoading = true
      try {
        const response = await api.get('/analytics/trend', { params })
        this.trend = response.data[0]?.data || []
      } catch (error) {
        this.error = error
      } finally {
        this.isLoading = false
      }
    }
  }
})
