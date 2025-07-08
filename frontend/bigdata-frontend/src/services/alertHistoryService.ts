import api from './api'

const API_BASE_URL = '/api'

export interface AlertHistoryQuery {
  page?: number
  size?: number
  category?: string
  level?: string
  status?: string
  rule_name?: string
  start_time?: string
  end_time?: string
}

export interface AlertHistoryStats {
  days?: number
  category?: string
}

export interface AlertHistoryItem {
  id: number
  rule_id: number
  rule_name: string
  category: string
  level: string
  alert_value: string
  condition: string
  labels: string
  status: string
  fired_at: string
  resolved_at: string | null
  created_at: string
}

export interface AlertHistoryResponse {
  items: AlertHistoryItem[]
  total: number
  page: number
  size: number
  pages: number
}

export interface AlertHistoryStatsResponse {
  total_alerts: number
  firing_alerts: number
  resolved_alerts: number
  category_stats: Array<{
    category: string
    total_count: number
    firing_count: number
    resolved_count: number
  }>
  level_stats: Array<{
    level: string
    count: number
  }>
  daily_stats: Array<{
    date: string
    total_count: number
    firing_count: number
    resolved_count: number
  }>
}

export const alertHistoryService = {
  // 获取告警历史列表
  async getHistoryList(params: AlertHistoryQuery): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/alert/history?${new URLSearchParams(params as any)}`)
    return response.json()
  },

  // 获取告警历史统计
  async getHistoryStats(params: AlertHistoryStats): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/alert/history/stats?${new URLSearchParams(params as any)}`)
    return response.json()
  },

  // 手动解决告警
  async resolveAlert(historyId: number, reason?: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/alert/history/${historyId}/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason })
    })
    return response.json()
  },

  // 确认告警
  async acknowledgeAlert(historyId: number, acknowledgedBy: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/alert/history/${historyId}/acknowledge?acknowledged_by=${acknowledgedBy}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    return response.json()
  }
} 