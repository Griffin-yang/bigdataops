// 兼容性导出，建议使用新的 services/
import { ApiService, AlertService, UserService } from '@/services'

// 保持向后兼容的默认导出
const api = {
  get: ApiService.get,
  post: ApiService.post,
  put: ApiService.put,
  delete: ApiService.delete,
  patch: ApiService.patch
}

export default api

// 保持向后兼容的API接口定义
export const alertAPI = {
  // 告警规则
  getRules: () => AlertService.getRules(),
  createRule: (data: any) => AlertService.createRule(data),
  updateRule: (id: number, data: any) => AlertService.updateRule(id, data),
  deleteRule: (id: number) => AlertService.deleteRule(id),
  
  // 告警模板
  getTemplates: () => AlertService.getTemplates(),
  createTemplate: (data: any) => AlertService.createTemplate(data),
  updateTemplate: (id: number, data: any) => AlertService.updateTemplate(id, data),
  deleteTemplate: (id: number) => AlertService.deleteTemplate(id),
  
  // 告警历史
  getHistory: () => AlertService.getHistory(),
  
  // 告警引擎
  getEngineStatus: () => AlertService.getEngineStatus(),
  startEngine: () => AlertService.startEngine(),
  stopEngine: () => AlertService.stopEngine(),
  testEngine: (ruleId: number) => AlertService.testEngine(ruleId)
}

export const ldapAPI = {
  getUsers: () => UserService.getUsers(),
  createUser: (data: any) => ApiService.post('/ldap/user', data),
  updateUser: (username: string, data: any) => ApiService.put(`/ldap/user/${username}`, data),
  deleteUser: (username: string) => ApiService.delete(`/ldap/user/${username}`)
} 