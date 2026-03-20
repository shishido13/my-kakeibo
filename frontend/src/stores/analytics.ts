import { defineStore } from 'pinia'
import api from '../services/api'

export interface AnalyticsFilterParams {
  start_date: string;
  end_date: string;
  category_ids?: number[];
  expense_type_id?: number;
  payer?: string;
}

export interface AnalyticsSummaryParams extends AnalyticsFilterParams {
  compare?: boolean;
}

export interface AnalyticsTrendParams extends AnalyticsFilterParams {
  group_by: string;
}

export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    summary: null as any,
    trend: [] as any[],
    isLoading: false,
    error: null as any
  }),
  actions: {
    async fetchSummary(params: AnalyticsSummaryParams) {
      this.isLoading = true
      try {
        const response = await api.get('/analytics/summary', {
          params,
          paramsSerializer: {
            indexes: null
          }
        })
        this.summary = response.data
        this.error = null
      } catch (error) {
        this.error = error
      } finally {
        this.isLoading = false
      }
    },
    async fetchTrend(params: AnalyticsTrendParams) {
      this.isLoading = true
      try {
        const response = await api.get('/analytics/trend', {
          params,
          paramsSerializer: {
            indexes: null
          }
        })
        this.trend = response.data[0]?.data || []
        this.error = null
      } catch (error) {
        this.error = error
      } finally {
        this.isLoading = false
      }
    }
  }
})
