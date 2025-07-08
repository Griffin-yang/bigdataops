// LDAP用户类型
export interface User {
  uid: string
  username: string
  email?: string
  gidNumber?: string
  homeDirectory?: string
  groups: string[]
}

// LDAP组类型
export interface Group {
  groupname: string
  gidNumber?: string
  members: User[]
}

// 告警规则类型
export interface AlertRule {
  id: number
  name: string
  category: string  // 组件分组
  promql: string
  condition: string  // 包含比较符和阈值的字符串，如"> 80"
  level: 'low' | 'medium' | 'high' | 'critical'
  description?: string
  labels?: Record<string, string>
  suppress?: string  // 抑制条件
  repeat?: number   // 再通知间隔（秒）
  enabled: boolean
  alert_state?: string  // 告警状态：ok、alerting、silenced
  last_alert_time?: string  // 最后告警时间
  notify_template_id?: number
  // 增强抑制功能字段
  duration?: number  // 告警持续时间(秒)
  max_send_count?: number  // 最大发送次数
  send_count?: number  // 当前已发送次数
  alert_start_time?: string  // 告警开始时间
  for_duration?: number  // 触发持续时间(秒)
  created_at?: string
  updated_at?: string
}

// 告警模板类型
export interface AlertNotifyTemplate {
  id: number
  name: string
  type: 'email' | 'http' | 'lechat'
  params: any  // 使用any类型以匹配后端的JSON格式
  description?: string
  created_at?: string
  updated_at?: string
}

export interface EmailConfig {
  smtp_server: string
  smtp_port: number
  username: string
  password: string
  use_ssl: boolean
  subject_template: string
  body_template: string
  to_addresses: string[]
}

export interface HttpConfig {
  url: string
  method: 'GET' | 'POST' | 'PUT' | 'PATCH'
  headers: Record<string, string>
  body_template: string
}

export interface LeChatConfig {
  mode: 'group' | 'personal'  // 发送模式：群组或个人
  url: string
  fromId: string
  groupId?: string  // 群组模式必填
  userIds?: string  // 个人模式必填，多个用逗号分隔
  ext: string
  body_template: string
  pushcontent?: string
  option?: string
  // 个人模式特有配置
  userMapping?: Record<string, string>  // 工号到用户ID的映射
}

// 告警历史类型
export interface AlertHistory {
  id: number
  rule_id: number
  rule_name: string
  category: string  // 组件分组
  level: string
  status: 'triggered' | 'recovered'
  message: string
  alert_value?: string  // 触发时的监控值
  condition?: string   // 触发条件
  labels?: Record<string, string>
  notified: boolean
  notified_at?: string
  resolved_at?: string
  created_at: string
}

// 组件分组选项
export interface ComponentCategory {
  value: string
  label: string
  description?: string
}

// 统计数据类型
export interface DashboardStats {
  totalUsers: number
  totalRules: number
  todayAlerts: number
  activeNodes: number
}

// 图表数据类型
export interface ChartData {
  labels: string[]
  datasets: Array<{
    label: string
    data: number[]
    backgroundColor?: string | string[]
    borderColor?: string
    fill?: boolean
  }>
}

// API响应类型
export interface ApiResponse<T = any> {
  code: number
  msg: string
  data: T
}

// 分页响应类型
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
}

// 表单类型
export interface LoginForm {
  username: string
  password: string
}

// LDAP请求参数类型
export interface LdapEnvParam {
  env: string
}

export interface CreateUserParam extends LdapEnvParam {
  username: string
  email?: string
  gidNumber?: string
  homeDirectory?: string
}

export interface CreateGroupParam extends LdapEnvParam {
  groupname: string
  gidNumber?: string
}

export interface AddUserToGroupParam extends LdapEnvParam {
  username: string
  groupname: string
}

export interface AlertRuleForm extends Omit<AlertRule, 'id' | 'created_at' | 'updated_at' | 'alert_state' | 'last_alert_time'> {}

export interface AlertTemplateForm extends Omit<AlertNotifyTemplate, 'id' | 'created_at' | 'updated_at'> {} 