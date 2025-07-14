import api from '@/utils/api'
import type { ApiResponse } from '@/types'

export interface ClusterOverview {
  total_nodes: number
  healthy_nodes: number
  unhealthy_nodes: number
  avg_cpu_usage: number
  avg_memory_usage: number
  avg_disk_usage: number
  services_status: Record<string, { healthy: number; total: number }>
  update_time: string
}

export interface ClusterNode {
  hostname: string
  instance: string
  job: string
  status: string
  roles: string[]
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_bytes_recv: number
  network_bytes_sent: number
  load_1m: number
  uptime: number
  uptime_formatted: string
  last_seen: string
}

export interface ClusterNodesResponse {
  items: ClusterNode[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ComponentService {
  name: string
  display_name: string
  query: string
  instances: ComponentInstance[]
  total_instances: number
  healthy_instances: number
  error?: string
}

export interface ComponentInstance {
  instance: string
  job: string
  status: string
  value: number
  metric: Record<string, any>
}

export interface Component {
  status: string
  total_instances: number
  healthy_instances: number
  services: ComponentService[]
  update_time: string
  detailed_metrics?: Record<string, {
    description: string
    query: string
    result: any
  }>
  error?: string
}

export interface ComponentsResponse {
  components: Record<string, Component>
}

export interface NodesQueryParams {
  status?: string
  service?: string
  job?: string
  role?: string
  page?: number
  size?: number
}

export interface ClusterOverviewParams {
  service?: string
  job?: string
  role?: string
}

export interface RealtimeMetricsParams {
  nodes?: string[]
  metrics?: string[]
}

export interface HealthCheckResponse {
  status: string
  message: string
  details: {
    total_nodes: number
    healthy_nodes: number
    unhealthy_nodes: number
    avg_cpu_usage: number
    avg_memory_usage: number
  }
}

class ClusterService {
  /**
   * 获取集群总览信息
   */
  async getClusterOverview(params?: ClusterOverviewParams): Promise<ApiResponse<ClusterOverview>> {
    try {
      // 过滤空值参数并构建查询字符串
      const filteredParams = Object.entries(params || {})
        .filter(([_, v]) => v != null && v !== '')
        .map(([k, v]) => [k, String(v)])
      
      const queryString = filteredParams.length > 0 
        ? '?' + new URLSearchParams(filteredParams).toString()
        : ''
      
      console.log('集群概览请求URL:', `/api/cluster/overview${queryString}`)
      
      const response = await fetch(`/api/cluster/overview${queryString}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      console.log('集群概览响应:', result)
      return result
    } catch (error) {
      console.error('获取集群概览失败:', error)
      throw error
    }
  }

  /**
   * 获取集群节点列表
   */
  async getClusterNodes(params?: NodesQueryParams): Promise<ApiResponse<ClusterNodesResponse>> {
    try {
      // 过滤空值参数并构建查询字符串
      const filteredParams = Object.entries(params || {})
        .filter(([_, v]) => v != null && v !== '')
        .map(([k, v]) => [k, String(v)])
      
      const queryString = filteredParams.length > 0 
        ? '?' + new URLSearchParams(filteredParams).toString()
        : ''
      
      console.log('集群节点请求URL:', `/api/cluster/nodes${queryString}`)
      
      const response = await fetch(`/api/cluster/nodes${queryString}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const result = await response.json()
      console.log('集群节点响应:', result)
      return result
    } catch (error) {
      console.error('获取集群节点失败:', error)
      throw error
    }
  }

  /**
   * 获取所有大数据组件概览
   */
  async getClusterComponents(): Promise<ApiResponse<ComponentsResponse>> {
    try {
      const response = await fetch('/api/cluster/components')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      console.log('集群组件响应:', result)
      return result
    } catch (error) {
      console.error('获取集群组件失败:', error)
      throw error
    }
  }

  /**
   * 获取特定组件的详细信息
   */
  async getComponentDetail(componentName: string): Promise<ApiResponse<Component>> {
    try {
      const response = await fetch(`/api/cluster/components/${componentName}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      console.log('组件详情响应:', result)
      return result
    } catch (error) {
      console.error('获取组件详情失败:', error)
      throw error
    }
  }

  /**
   * 获取实时监控指标
   */
  async getRealtimeMetrics(params?: RealtimeMetricsParams): Promise<ApiResponse<any>> {
    try {
      const filteredParams = Object.entries(params || {})
        .filter(([_, v]) => v != null && v !== '')
        .map(([k, v]) => [k, String(v)])
      
      const queryString = filteredParams.length > 0 
        ? '?' + new URLSearchParams(filteredParams).toString()
        : ''
      
      const response = await fetch(`/api/cluster/metrics/realtime${queryString}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      return result
    } catch (error) {
      console.error('获取实时指标失败:', error)
      throw error
    }
  }

  /**
   * 集群健康检查
   */
  async getClusterHealth(): Promise<ApiResponse<HealthCheckResponse>> {
    try {
      const response = await fetch('/api/cluster/health')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const result = await response.json()
      console.log('集群健康检查响应:', result)
      return result
    } catch (error) {
      console.error('获取集群健康状态失败:', error)
      throw error
    }
  }

  /**
   * 批量获取集群数据
   */
  async getAllClusterData(): Promise<{
    overview: ApiResponse<ClusterOverview>
    components: ApiResponse<ComponentsResponse>
    health: ApiResponse<HealthCheckResponse>
  }> {
    const [overview, components, health] = await Promise.all([
      this.getClusterOverview(),
      this.getClusterComponents(),
      this.getClusterHealth()
    ])

    return { overview, components, health }
  }

  /**
   * 获取节点角色统计
   */
  async getNodeRoleStats(): Promise<Record<string, number>> {
    try {
      const response = await this.getClusterNodes()
      if (response.code === 0) {
        const roleStats: Record<string, number> = {}
        response.data.items.forEach(node => {
          node.roles.forEach(role => {
            roleStats[role] = (roleStats[role] || 0) + 1
          })
        })
        return roleStats
      }
      return {}
    } catch (error) {
      console.error('获取节点角色统计失败:', error)
      return {}
    }
  }

  /**
   * 获取组件健康统计
   */
  async getComponentHealthStats(): Promise<{
    total: number
    healthy: number
    warning: number
    unhealthy: number
    unknown: number
  }> {
    try {
      const response = await this.getClusterComponents()
      if (response.code === 0) {
        const components = response.data.components
        const stats = {
          total: 0,
          healthy: 0,
          warning: 0,
          unhealthy: 0,
          unknown: 0
        }

        Object.values(components).forEach(component => {
          stats.total++
          switch (component.status) {
            case 'healthy':
              stats.healthy++
              break
            case 'warning':
              stats.warning++
              break
            case 'unhealthy':
              stats.unhealthy++
              break
            default:
              stats.unknown++
          }
        })

        return stats
      }
      return { total: 0, healthy: 0, warning: 0, unhealthy: 0, unknown: 0 }
    } catch (error) {
      console.error('获取组件健康统计失败:', error)
      return { total: 0, healthy: 0, warning: 0, unhealthy: 0, unknown: 0 }
    }
  }
}

// 导出单例
export const clusterService = new ClusterService()
export default clusterService