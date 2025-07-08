import { ALERT_SEVERITY_LABELS, ALERT_STATUS_LABELS, COMPARISON_LABELS } from '@/constants'

/**
 * 格式化日期时间
 */
export function formatDateTime(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

/**
 * 格式化日期
 */
export function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * 格式化数字，添加千分位分隔符
 */
export function formatNumber(num: number): string {
  return num.toLocaleString('zh-CN')
}

/**
 * 格式化百分比
 */
export function formatPercent(value: number, total: number): string {
  if (total === 0) return '0%'
  return Math.round((value / total) * 100) + '%'
}

/**
 * 格式化告警级别
 */
export function formatSeverity(severity: string): string {
  return ALERT_SEVERITY_LABELS[severity as keyof typeof ALERT_SEVERITY_LABELS] || severity
}

/**
 * 格式化告警状态
 */
export function formatAlertStatus(status: string): string {
  return ALERT_STATUS_LABELS[status as keyof typeof ALERT_STATUS_LABELS] || status
}

/**
 * 格式化比较运算符
 */
export function formatComparison(comparison: string): string {
  return COMPARISON_LABELS[comparison as keyof typeof COMPARISON_LABELS] || comparison
}

/**
 * 格式化持续时间（秒转为可读格式）
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分钟`
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}小时`
  return `${Math.floor(seconds / 86400)}天`
}

/**
 * 截断文本
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
} 