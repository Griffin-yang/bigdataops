// API相关常量
export const API_BASE_URL = '/api'

// 响应码常量
export const RESPONSE_CODE = {
  SUCCESS: 0,
  ERROR: 1
} as const

// 告警严重级别
export const ALERT_SEVERITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
} as const

export const ALERT_SEVERITY_LABELS = {
  [ALERT_SEVERITY.LOW]: '低',
  [ALERT_SEVERITY.MEDIUM]: '中',
  [ALERT_SEVERITY.HIGH]: '高',
  [ALERT_SEVERITY.CRITICAL]: '严重'
} as const

export const ALERT_SEVERITY_COLORS = {
  [ALERT_SEVERITY.LOW]: '#52c41a',
  [ALERT_SEVERITY.MEDIUM]: '#faad14',
  [ALERT_SEVERITY.HIGH]: '#fa8c16',
  [ALERT_SEVERITY.CRITICAL]: '#f5222d'
} as const

// 比较运算符
export const COMPARISON_OPERATORS_DICT = {
  GT: 'gt',
  LT: 'lt',
  EQ: 'eq',
  GTE: 'gte',
  LTE: 'lte'
} as const

export const COMPARISON_LABELS = {
  [COMPARISON_OPERATORS_DICT.GT]: '>',
  [COMPARISON_OPERATORS_DICT.LT]: '<',
  [COMPARISON_OPERATORS_DICT.EQ]: '=',
  [COMPARISON_OPERATORS_DICT.GTE]: '>=',
  [COMPARISON_OPERATORS_DICT.LTE]: '<='
} as const

// 通知类型
export const NOTIFY_TYPES = {
  EMAIL: 'email',
  HTTP: 'http',
  LECHAT: 'lechat'
} as const

export const NOTIFY_TYPE_LABELS = {
  [NOTIFY_TYPES.EMAIL]: '邮件',
  [NOTIFY_TYPES.HTTP]: 'HTTP',
  [NOTIFY_TYPES.LECHAT]: '乐聊'
} as const

// HTTP方法
export const HTTP_METHODS = ['GET', 'POST', 'PUT', 'PATCH'] as const

// 告警状态
export const ALERT_STATUS = {
  FIRING: 'firing',
  RESOLVED: 'resolved'
} as const

export const ALERT_STATUS_LABELS = {
  [ALERT_STATUS.FIRING]: '触发中',
  [ALERT_STATUS.RESOLVED]: '已解决'
} as const

export const ALERT_STATUS_COLORS = {
  [ALERT_STATUS.FIRING]: '#f5222d',
  [ALERT_STATUS.RESOLVED]: '#52c41a'
} as const

// 本地存储键名
export const STORAGE_KEYS = {
  TOKEN: 'token',
  USERNAME: 'username',
  USER_INFO: 'userInfo'
} as const

// 路由路径
export const ROUTES = {
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  USERS: '/users',
  ALERT_RULES: '/alert-rules',
  ALERT_TEMPLATES: '/alert-templates',
  ALERT_HISTORY: '/alert-history',
  MONITORING: '/monitoring'
} as const

// 分页配置
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  PAGE_SIZES: [10, 20, 50, 100]
} as const

// 组件分组选项
export const COMPONENT_CATEGORIES = [
  { value: 'hdfs', label: 'HDFS', description: 'Hadoop分布式文件系统' },
  { value: 'hive', label: 'Hive', description: 'Hive数据仓库' },
  { value: 'spark', label: 'Spark', description: 'Spark计算引擎' },
  { value: 'mysql', label: 'MySQL', description: 'MySQL数据库' },
  { value: 'redis', label: 'Redis', description: 'Redis缓存' },
  { value: 'kafka', label: 'Kafka', description: 'Kafka消息队列' },
  { value: 'elasticsearch', label: 'Elasticsearch', description: 'ES搜索引擎' },
  { value: 'kubernetes', label: 'Kubernetes', description: 'K8s容器编排' },
  { value: 'system', label: '系统监控', description: 'CPU、内存、磁盘等' },
  { value: 'network', label: '网络监控', description: '网络连接、带宽等' },
  { value: 'application', label: '应用监控', description: '业务应用监控' },
  { value: 'other', label: '其他', description: '其他类型告警' }
]

// 告警等级选项
export const ALERT_LEVELS = [
  { value: 'low', label: '低', color: '#909399', type: 'info' },
  { value: 'medium', label: '中', color: '#E6A23C', type: 'warning' },
  { value: 'high', label: '高', color: '#F56C6C', type: 'danger' },
  { value: 'critical', label: '严重', color: '#F56C6C', type: 'danger' }
]

// 告警状态选项
export const ALERT_STATES = [
  { value: 'ok', label: '正常', color: '#67C23A', type: 'success' },
  { value: 'alerting', label: '告警中', color: '#F56C6C', type: 'danger' },
  { value: 'silenced', label: '静默中', color: '#909399', type: 'info' }
]

// 告警历史状态
export const ALERT_HISTORY_STATUS = [
  { value: 'triggered', label: '已触发', color: '#F56C6C', type: 'danger' },
  { value: 'recovered', label: '已恢复', color: '#67C23A', type: 'success' }
]

// 比较操作符
export const COMPARISON_OPERATORS = [
  { value: 'gt', label: '>', description: '大于' },
  { value: 'gte', label: '>=', description: '大于等于' },
  { value: 'lt', label: '<', description: '小于' },
  { value: 'lte', label: '<=', description: '小于等于' },
  { value: 'eq', label: '=', description: '等于' },
  { value: 'ne', label: '!=', description: '不等于' }
]

// 时间单位选项
export const TIME_UNITS = [
  { value: 's', label: '秒' },
  { value: 'm', label: '分钟' },
  { value: 'h', label: '小时' },
  { value: 'd', label: '天' }
]

// 通用的分页配置
export const PAGINATION_CONFIG = {
  pageSizes: [10, 20, 50, 100],
  defaultPageSize: 20,
  layout: 'total, sizes, prev, pager, next, jumper'
}

// 获取分组标签
export const getCategoryLabel = (value: string): string => {
  const category = COMPONENT_CATEGORIES.find(c => c.value === value)
  return category ? category.label : value
}

// 获取等级标签
export const getLevelLabel = (value: string): string => {
  const level = ALERT_LEVELS.find(l => l.value === value)
  return level ? level.label : value
}

// 获取等级类型
export const getLevelType = (value: string): string => {
  const level = ALERT_LEVELS.find(l => l.value === value)
  return level ? level.type : 'info'
}

// 获取状态标签
export const getStateLabel = (value: string): string => {
  const state = ALERT_STATES.find(s => s.value === value)
  return state ? state.label : value
}

// 获取状态类型
export const getStateType = (value: string): string => {
  const state = ALERT_STATES.find(s => s.value === value)
  return state ? state.type : 'info'
}

// 获取分组类型
export const getCategoryType = (value: string): string => {
  // 为不同组件分配不同颜色类型
  const typeMap: Record<string, string> = {
    'hdfs': 'primary',
    'hive': 'success',
    'spark': 'warning',
    'mysql': 'danger',
    'redis': 'info',
    'kafka': 'primary',
    'elasticsearch': 'warning',
    'kubernetes': 'success',
    'system': 'info',
    'network': 'warning',
    'application': 'primary',
    'other': 'info'
  }
  return typeMap[value] || 'info'
}

// 导出选项常量供组件使用
export const CATEGORY_OPTIONS = COMPONENT_CATEGORIES
export const LEVEL_OPTIONS = ALERT_LEVELS 