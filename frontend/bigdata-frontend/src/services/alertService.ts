import ApiService from './api'
import type { 
  AlertRule, 
  AlertNotifyTemplate, 
  AlertHistory, 
  AlertRuleForm, 
  AlertTemplateForm,
  PaginatedResponse 
} from '@/types'

interface EngineStatus {
  running: boolean
  uptime?: number
  last_check?: string
}

interface RuleListParams {
  page?: number
  size?: number
  category?: string
  level?: string
  enabled?: boolean
  alert_state?: string
  name?: string
}

export class AlertService {
  // 告警规则相关 - 优化后的分页查询
  static async getRules(params: RuleListParams = {}): Promise<{
    items: AlertRule[]
    total: number
    page: number
    size: number
  }> {
    try {
      const queryParams = new URLSearchParams()
      
      // 设置默认分页参数
      queryParams.append('page', String(params.page || 1))
      queryParams.append('size', String(params.size || 20))
      
      // 添加过滤条件
      if (params.category) queryParams.append('category', params.category)
      if (params.level) queryParams.append('level', params.level)
      if (params.enabled !== undefined) queryParams.append('enabled', String(params.enabled))
      if (params.alert_state) queryParams.append('alert_state', params.alert_state)
      if (params.name) queryParams.append('name', params.name)
      
      const response = await ApiService.get<{
        items: AlertRule[]
        total: number
        page: number
        size: number
      }>(`/alert/rule?${queryParams.toString()}`)
      
      return response || { items: [], total: 0, page: 1, size: 20 }
    } catch (error) {
      console.error('获取规则列表失败:', error)
      return { items: [], total: 0, page: 1, size: 20 }
    }
  }

  // 获取规则分组
  static async getRuleCategories(): Promise<string[]> {
    try {
      const response = await ApiService.get<string[]>('/alert/rule/categories')
      return response || []
    } catch (error) {
      console.error('获取规则分组失败:', error)
      return []
    }
  }

  static async getRule(id: number): Promise<AlertRule | null> {
    try {
      const response = await ApiService.get<AlertRule>(`/alert/rule/${id}`)
      return response || null
    } catch (error) {
      console.error('获取规则详情失败:', error)
      return null
    }
  }

  static async createRule(rule: Partial<AlertRule>): Promise<AlertRule | null> {
    try {
      const response = await ApiService.post<AlertRule>('/alert/rule', rule)
      return response
    } catch (error) {
      console.error('创建规则失败:', error)
      throw error
    }
  }

  static async updateRule(id: number, rule: Partial<AlertRule>): Promise<AlertRule> {
    const response = await ApiService.put<AlertRule>(`/alert/rule/${id}`, rule)
    return response
  }

  static async deleteRule(id: number): Promise<boolean> {
    try {
      const response = await ApiService.delete<{success: boolean}>(`/alert/rule/${id}`)
      return response?.success || false
    } catch (error) {
      console.error('删除规则失败:', error)
      return false
    }
  }

  // 告警模板相关
  static async getTemplates(type?: string): Promise<AlertNotifyTemplate[]> {
    try {
      const url = type ? `/alert/notify_template?type=${type}` : '/alert/notify_template'
      const response = await ApiService.get<AlertNotifyTemplate[]>(url)
      return response || []
    } catch (error) {
      console.error('获取模板列表失败:', error)
      return []
    }
  }

  static async getTemplate(id: number): Promise<AlertNotifyTemplate | null> {
    const response = await ApiService.get<AlertNotifyTemplate>(`/alert/notify_template/${id}`)
    return response || null
  }

  static async createTemplate(template: {
    name: string
    type: 'email' | 'http' | 'lechat'
    params: any
  }): Promise<AlertNotifyTemplate> {
    const response = await ApiService.post<AlertNotifyTemplate>('/alert/notify_template', template)
    return response
  }

  static async updateTemplate(id: number, template: {
    name: string
    params: any
  }): Promise<AlertNotifyTemplate> {
    const response = await ApiService.put<AlertNotifyTemplate>(`/alert/notify_template/${id}`, template)
    return response
  }

  static async deleteTemplate(id: number): Promise<{success: boolean}> {
    const response = await ApiService.delete<{success: boolean}>(`/alert/notify_template/${id}`)
    return response
  }

  // 告警历史相关 - 优化后的分页查询
  static async getHistory(params: {
    rule_id?: number
    page?: number
    size?: number
    status?: string
    start_time?: string
    end_time?: string
  } = {}): Promise<{
    items: AlertHistory[]
    total: number
    page: number
    size: number
  }> {
    try {
      const queryParams = new URLSearchParams()
      
      queryParams.append('page', String(params.page || 1))
      queryParams.append('size', String(params.size || 20))
      
      if (params.rule_id) queryParams.append('rule_id', String(params.rule_id))
      if (params.status) queryParams.append('status', params.status)
      if (params.start_time) queryParams.append('start_time', params.start_time)
      if (params.end_time) queryParams.append('end_time', params.end_time)
      
      const response = await ApiService.get<{
        items: AlertHistory[]
        total: number
        page: number
        size: number
      }>(`/alert/history?${queryParams.toString()}`)
      
      return response || { items: [], total: 0, page: 1, size: 20 }
    } catch (error) {
      console.error('获取告警历史失败:', error)
      return { items: [], total: 0, page: 1, size: 20 }
    }
  }

  static async getHistoryById(id: number): Promise<AlertHistory | null> {
    const response = await ApiService.get<AlertHistory>(`/alert/history/${id}`)
    return response || null
  }

  static async deleteHistory(id: number): Promise<{success: boolean}> {
    const response = await ApiService.delete<{success: boolean}>(`/alert/history/${id}`)
    return response
  }

  // 告警引擎相关
  static async getEngineStatus(): Promise<EngineStatus> {
    try {
      const response = await ApiService.get<EngineStatus>('/alert/engine/status')
      return response || { running: false }
    } catch (error) {
      console.error('获取引擎状态失败:', error)
      return { running: false }
    }
  }

  static async startEngine(): Promise<{status: string}> {
    const response = await ApiService.post<{status: string}>('/alert/engine/start')
    return response
  }

  static async stopEngine(): Promise<{status: string}> {
    const response = await ApiService.post<{status: string}>('/alert/engine/stop')
    return response
  }

  static async testEngine(): Promise<{status: string}> {
    const response = await ApiService.post<{status: string}>('/alert/engine/test')
    return response
  }
} 