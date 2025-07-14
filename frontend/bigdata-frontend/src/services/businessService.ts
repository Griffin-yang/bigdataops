import api from '@/utils/api'

export interface Cluster {
  id: string
  name: string
  type: string
  schedulers: string[]
}

export interface BusinessOverview {
  cluster_name: string
  date_range: string
  total_jobs: number
  success_jobs: number
  failed_jobs: number
  success_rate: number
  schedulers_stats: Record<string, any>
}

export interface FailedJob {
  job_id: string
  job_name: string
  project_name: string
  execution_time: string
  duration: number
  status: string
  error_message: string
  scheduler: string
  scheduler_type?: string
  submit_user?: string
  view_url: string
}

export interface TopDurationJob {
  job_id: string
  job_name: string
  project_name: string
  execution_time: string
  duration: number
  status: string
  scheduler: string
  scheduler_type?: string
  view_url?: string
}

export interface DailyStatistic {
  date: string
  total_jobs: number
  success_jobs: number
  failed_jobs: number
  success_rate: number
}

export interface SchedulerDistribution {
  scheduler: string
  job_count: number
  percentage: number
}

export interface ProjectDistribution {
  name: string
  value: number
  success: number
  failed: number
  scheduler: string
}

export interface Statistics {
  daily_statistics: DailyStatistic[]
  scheduler_distribution: SchedulerDistribution[]
  project_distribution: ProjectDistribution[]
}

export const businessService = {
  // 获取集群列表
  async getClusters() {
    return api.get<Cluster[]>('/business/clusters')
  },

  // 获取业务概览
  async getBusinessOverview(clusterName: string, startDate?: string, endDate?: string) {
    const params: Record<string, string> = { cluster_name: clusterName }
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    
    return api.get<BusinessOverview>('/business/overview', { params })
  },

  // 获取失败任务列表
  async getFailedJobs(
    clusterName: string, 
    startDate?: string, 
    endDate?: string,
    page = 1, 
    size = 20
  ) {
    const params: Record<string, any> = { 
      cluster_name: clusterName,
      page,
      size
    }
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    
    return api.get<{
      items: FailedJob[]
      total: number
      page: number
      size: number
      pages: number
    }>('/business/failed-jobs', { params })
  },

  // 获取执行时间排行榜
  async getTopDurationJobs(
    clusterName: string, 
    startDate?: string, 
    endDate?: string,
    limit = 50
  ) {
    const params: Record<string, any> = { 
      cluster_name: clusterName,
      limit
    }
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    
    return api.get<TopDurationJob[]>('/business/top-duration-jobs', { params })
  },

  // 获取统计数据
  async getStatistics(clusterName: string, startDate?: string, endDate?: string) {
    const params: Record<string, string> = { cluster_name: clusterName }
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    
    return api.get<Statistics>('/business/statistics', { params })
  },

  // 获取项目分布数据
  async getProjectDistribution(clusterName: string, startDate?: string, endDate?: string) {
    const params: Record<string, string> = { cluster_name: clusterName }
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    
    return api.get<ProjectDistribution[]>('/business/project-distribution', { params })
  }
} 