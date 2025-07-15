<template>
  <div class="business-monitoring">
    <!-- 页面标题和工具栏 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1>
            <el-icon class="title-icon"><DataBoard /></el-icon>
            业务监控
          </h1>
          <p>大数据任务调度监控 - 实时掌握业务任务执行状态</p>
        </div>
        <div class="header-actions">
          <el-button 
            @click="refreshData" 
            :loading="loading" 
            type="primary"
            :icon="Refresh"
            size="default"
          >
            {{ loading ? '刷新中...' : '刷新数据' }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 集群选择和时间范围 -->
    <div class="control-panel">
      <el-card>
        <div class="controls">
          <div class="control-group">
            <label>选择集群:</label>
            <el-select 
              v-model="selectedCluster" 
              @change="handleClusterChange"
              placeholder="请选择集群"
              style="width: 200px"
            >
              <el-option
                v-for="cluster in clusters"
                :key="cluster.id"
                :label="cluster.name"
                :value="cluster.id"
              />
            </el-select>
          </div>
          
          <div class="control-group">
            <label>查询时间:</label>
            <el-date-picker
              v-model="dateRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始时间"
              end-placeholder="结束时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              @change="handleDateChange"
              style="width: 380px"
            />
          </div>
          
          <div class="control-group">
            <el-button 
              @click="queryData" 
              type="primary"
              :loading="loading"
              :disabled="!selectedCluster"
            >
              查询
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 业务概览统计 -->
    <div class="overview-section" v-if="overview.cluster_name">
      <el-card>
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <h3>业务概览统计</h3>
              <div class="cluster-info">
                <el-tag 
                  :type="getClusterTagType(selectedCluster)" 
                  size="small" 
                  effect="light"
                  style="margin-left: 8px;"
                >
                  {{ getClusterDisplayName(selectedCluster) }}
                </el-tag>
                <el-tag 
                  type="info" 
                  size="small" 
                  effect="light"
                  style="margin-left: 4px;"
                >
                  {{ getSchedulerInfo(selectedCluster) }}
                </el-tag>
              </div>
            </div>
            <span class="date-range">{{ overview.date_range }}</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-value">{{ overview.total_jobs }}</div>
              <div class="stat-label">总任务数</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-value">{{ overview.success_jobs }}</div>
              <div class="stat-label">成功任务</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-value">{{ overview.failed_jobs }}</div>
              <div class="stat-label">失败任务</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="stat-card">
              <div class="stat-value">{{ overview.success_rate }}%</div>
              <div class="stat-label">成功率</div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 数据展示区域 -->
    <div v-if="overview.cluster_name">
      <!-- 统计图表区域 -->
      <el-row :gutter="24" class="chart-section">
        <!-- 每日统计趋势 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <h3>每日任务统计趋势</h3>
                <span class="date-range">{{ overview.date_range }}</span>
              </div>
            </template>
            <div class="chart-container" style="height: 300px;">
              <div ref="dailyChartRef" style="width: 100%; height: 100%;"></div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 调度器分布 -->
        <el-col :span="6">
          <el-card>
            <template #header>
              <div class="card-header">
                <h3>调度器分布</h3>
              </div>
            </template>
            <div class="chart-container" style="height: 300px;">
              <div ref="schedulerChartRef" style="width: 100%; height: 100%;"></div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 项目分布 -->
        <el-col :span="6">
          <el-card>
            <template #header>
              <div class="card-header">
                <h3>项目分布</h3>
              </div>
            </template>
            <div class="chart-container" style="height: 300px;">
              <div ref="projectChartRef" style="width: 100%; height: 100%;"></div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 失败任务列表区域 -->
      <el-row :gutter="24" class="table-section">
        <el-col :span="24">
          <el-card>
            <template #header>
              <div class="card-header">
                <h3>失败任务列表</h3>
                <span class="task-count">共 {{ failedJobsData.total }} 个失败任务</span>
              </div>
            </template>
            
            <el-table :data="failedJobsData.items" v-loading="loading" height="500">
              <el-table-column type="index" label="序号" width="60" :index="(index: number) => (failedJobsData.page - 1) * failedJobsData.size + index + 1" />
              <el-table-column prop="job_name" label="任务名称" min-width="200" show-overflow-tooltip />
              <el-table-column prop="project_name" label="项目名称" width="150" show-overflow-tooltip />
              <el-table-column prop="submit_user" label="提交用户" width="120" show-overflow-tooltip />
              <el-table-column label="调度器" width="100">
                <template #default="{ row }">
                  <el-tag 
                    :type="getSchedulerTagType(row.scheduler_type)"
                    size="small"
                    effect="light"
                  >
                    {{ row.scheduler_type || row.scheduler }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="execution_time" label="执行时间" width="160" />
              <el-table-column label="时长" width="100">
                <template #default="{ row }">
                  {{ formatDuration(row.duration) }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag 
                    :type="getStatusTagType(row.status)"
                    size="small"
                  >
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="openJobDetail(row.view_url)"
                    link
                  >
                    查看日志
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <!-- 分页组件 -->
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="failedJobsData.page"
                v-model:page-size="failedJobsData.size"
                :page-sizes="[20, 50, 100, 200]"
                :total="failedJobsData.total"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleFailedJobsSizeChange"
                @current-change="handleFailedJobsPageChange"
              />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 执行时间排行榜区域 -->
      <el-row :gutter="24" class="table-section">
        <el-col :span="24">
          <el-card>
            <template #header>
              <div class="card-header">
                <h3>执行时间排行榜</h3>
                <span class="task-count">TOP 50 最耗时任务</span>
              </div>
            </template>
            
            <el-table :data="topDurationJobs" v-loading="loading" height="400">
              <el-table-column type="index" label="排名" width="60" :index="(index: number) => index + 1" />
              <el-table-column prop="job_name" label="任务名称" min-width="200" show-overflow-tooltip />
              <el-table-column prop="project_name" label="项目名称" width="150" show-overflow-tooltip />
              <el-table-column prop="submit_user" label="提交用户" width="120" show-overflow-tooltip />
              <el-table-column label="调度器" width="100">
                <template #default="{ row }">
                  <el-tag 
                    :type="getSchedulerTagType(row.scheduler_type)"
                    size="small"
                    effect="light"
                  >
                    {{ row.scheduler_type || row.scheduler }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="execution_time" label="执行时间" width="160" />
              <el-table-column label="执行时长" width="120">
                <template #default="{ row }">
                  <span class="duration-text">{{ formatDuration(row.duration) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120">
                <template #default="{ row }">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="openJobDetail(row.view_url)"
                    link
                  >
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, DataBoard } from '@element-plus/icons-vue'
import { businessService } from '@/services'
import type { Cluster, BusinessOverview, FailedJob, TopDurationJob } from '@/services/businessService'
import * as echarts from 'echarts'

// 数据状态
const loading = ref(false)
const clusters = ref<Cluster[]>([])
const selectedCluster = ref<string>('')
const dateRange = ref<[string, string]>(['', ''])

const overview = ref({
  cluster_name: '',
  date_range: '',
  total_jobs: 0,
  success_jobs: 0,
  failed_jobs: 0,
  success_rate: 0,
  schedulers_stats: {}
})

const failedJobsData = ref<{
  items: FailedJob[]
  total: number
  page: number
  size: number
  pages: number
}>({
  items: [],
  total: 0,
  page: 1,
  size: 20,
  pages: 0
})

const topDurationJobs = ref<TopDurationJob[]>([])

// 图表相关
const dailyChartRef = ref<HTMLElement>()
const schedulerChartRef = ref<HTMLElement>()
const projectChartRef = ref<HTMLElement>()

// 统计数据
const statisticsData = ref<any>({
  daily_statistics: [],
  scheduler_distribution: [],
  project_distribution: []
})

onMounted(async () => {
  await loadClusters()
  if (clusters.value.length > 0) {
    // 默认选择apache集群，如果不存在则选择cdh集群，最后选择第一个
    const apacheCluster = clusters.value.find(cluster => cluster.id === 'apache')
    const cdhCluster = clusters.value.find(cluster => cluster.id === 'cdh')
    selectedCluster.value = apacheCluster ? apacheCluster.id : (cdhCluster ? cdhCluster.id : clusters.value[0].id)
    
    // 设置默认时间范围为过去24小时
    const now = new Date()
    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000)
    
    // 使用本地时间格式化，避免时区问题
    const startDateStr = yesterday.getFullYear() + '-' + 
      String(yesterday.getMonth() + 1).padStart(2, '0') + '-' + 
      String(yesterday.getDate()).padStart(2, '0') + ' ' + 
      String(yesterday.getHours()).padStart(2, '0') + ':' + 
      String(yesterday.getMinutes()).padStart(2, '0') + ':' + 
      String(yesterday.getSeconds()).padStart(2, '0')
    
    const endDateStr = now.getFullYear() + '-' + 
      String(now.getMonth() + 1).padStart(2, '0') + '-' + 
      String(now.getDate()).padStart(2, '0') + ' ' + 
      String(now.getHours()).padStart(2, '0') + ':' + 
      String(now.getMinutes()).padStart(2, '0') + ':' + 
      String(now.getSeconds()).padStart(2, '0')
    
    dateRange.value = [startDateStr, endDateStr]
    
    // 给用户一个提示信息
    const selectedClusterInfo = clusters.value.find(c => c.id === selectedCluster.value)
    if (selectedClusterInfo) {
      const schedulerInfo = selectedClusterInfo.schedulers.includes('azkaban') 
        ? 'Azkaban + DolphinScheduler' 
        : 'DolphinScheduler'
      ElMessage.info(`已选择 ${selectedClusterInfo.name} (${schedulerInfo})，默认查询昨日到今日的数据`)
    }
    
    // 自动查询数据
    await queryData()
  } else {
    ElMessage.warning('未找到可用的集群，请检查后端配置')
  }
})

const loadClusters = async () => {
  try {
    clusters.value = await businessService.getClusters()
    console.log('已加载集群列表:', clusters.value)
  } catch (error: any) {
    console.error('加载集群列表失败:', error)
    if (error.response?.status === 500) {
      ElMessage.error('服务器内部错误，请检查后端服务状态')
    } else if (error.response?.status === 404) {
      ElMessage.error('业务监控接口不存在，请检查后端服务是否启动')
    } else if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      ElMessage.error('网络连接超时，请检查后端服务是否正常运行')
    } else {
      ElMessage.error(`加载集群列表失败: ${error.message || '未知错误'}`)
    }
  }
}

const queryData = async () => {
  if (!selectedCluster.value) {
    ElMessage.warning('请先选择集群')
    return
  }
  
  if (!dateRange.value[0] || !dateRange.value[1]) {
    ElMessage.warning('请选择查询时间范围')
    return
  }
  
  loading.value = true
  try {
    const [startDate, endDate] = dateRange.value
    
    // 显示集群类型信息
    const clusterInfo = clusters.value.find(c => c.id === selectedCluster.value)
    if (clusterInfo) {
      const schedulerInfo = clusterInfo.schedulers.includes('azkaban') 
        ? 'Azkaban + DolphinScheduler' 
        : 'DolphinScheduler'
      console.log(`正在查询 ${clusterInfo.name} (${schedulerInfo}) 的数据...`)
    }
    
    // 并行获取所有数据
    const [overviewData, topDurationJobsResult, statisticsResult] = await Promise.all([
      businessService.getBusinessOverview(selectedCluster.value, startDate, endDate),
      businessService.getTopDurationJobs(selectedCluster.value, startDate, endDate, 50),
      businessService.getStatistics(selectedCluster.value, startDate, endDate)
    ])
    
    overview.value = overviewData
    topDurationJobs.value = topDurationJobsResult
    statisticsData.value = statisticsResult
    
    // 单独查询失败任务（支持分页）
    await queryFailedJobs()
    
    // 等待DOM更新后初始化图表
    await nextTick()
    initCharts()
    
    // 显示查询成功信息
    ElMessage.success(`查询完成：共找到 ${overviewData.total_jobs} 个任务`)
      } catch (error: any) {
      console.error('查询数据失败:', error)
      // 更详细的错误信息
      if (error.response?.status === 500) {
        ElMessage.error('服务器内部错误，请检查后端服务和数据库连接')
      } else if (error.response?.status === 404) {
        ElMessage.error('接口不存在，请检查后端服务是否启动')
      } else if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
        ElMessage.error('请求超时，请检查网络连接或后端服务状态')
      } else {
        ElMessage.error(`查询数据失败: ${error.message || '未知错误'}`)
      }
    } finally {
    loading.value = false
  }
}

const handleClusterChange = async () => {
  // 清空当前数据
  overview.value = {
    cluster_name: '',
    date_range: '',
    total_jobs: 0,
    success_jobs: 0,
    failed_jobs: 0,
    success_rate: 0,
    schedulers_stats: {}
  }
  
  failedJobsData.value = {
    items: [],
    total: 0,
    page: 1,
    size: 20,
    pages: 0
  }
  
  topDurationJobs.value = []
  
  statisticsData.value = {
    daily_statistics: [],
    scheduler_distribution: [],
    project_distribution: []
  }
  
  // 如果选择了集群且时间范围有效，自动查询数据
  if (selectedCluster.value && dateRange.value[0] && dateRange.value[1]) {
    await queryData()
  } else if (selectedCluster.value) {
    // 如果只选择了集群但没有选择时间范围，给出提示
    ElMessage.info('请选择查询时间范围')
  }
}

const handleDateChange = () => {
  if (selectedCluster.value && dateRange.value[0] && dateRange.value[1]) {
    queryData()
  }
}

const refreshData = () => {
  queryData()
}

// 初始化图表
const initCharts = () => {
  initDailyChart()
  initSchedulerChart()
  initProjectChart()
}

// 初始化每日统计图表
const initDailyChart = () => {
  if (!dailyChartRef.value) return
  
  const chart = echarts.init(dailyChartRef.value)
  const { daily_statistics } = statisticsData.value
  
  console.log('每日统计数据:', daily_statistics)
  
  if (!daily_statistics || daily_statistics.length === 0) {
    console.warn('每日统计数据为空')
    return
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['总任务数', '成功任务', '失败任务', '成功率']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: daily_statistics.map((item: any) => item.date)
    },
    yAxis: [
      {
        type: 'value',
        name: '任务数量',
        position: 'left'
      },
      {
        type: 'value',
        name: '成功率(%)',
        position: 'right',
        max: 100
      }
    ],
    series: [
      {
        name: '总任务数',
        type: 'line',
        data: daily_statistics.map((item: any) => item.total_jobs)
      },
      {
        name: '成功任务',
        type: 'line',
        data: daily_statistics.map((item: any) => item.success_jobs)
      },
      {
        name: '失败任务',
        type: 'line',
        data: daily_statistics.map((item: any) => item.failed_jobs)
      },
      {
        name: '成功率',
        type: 'line',
        yAxisIndex: 1,
        data: daily_statistics.map((item: any) => item.success_rate)
      }
    ]
  }
  
  console.log('图表配置:', option)
  chart.setOption(option)
}

// 初始化调度器分布图表
const initSchedulerChart = () => {
  if (!schedulerChartRef.value) return
  
  const chart = echarts.init(schedulerChartRef.value)
  const { scheduler_distribution } = statisticsData.value
  
  console.log('调度器分布数据:', scheduler_distribution)
  
  if (!scheduler_distribution || scheduler_distribution.length === 0) {
    console.warn('调度器分布数据为空')
    return
  }
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [
      {
        name: '调度器分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: scheduler_distribution.map((item: any) => ({
          name: item.scheduler_name,
          value: item.job_count
        }))
      }
    ]
  }
  
  console.log('调度器图表配置:', option)
  chart.setOption(option)
}

// 初始化项目分布图表
const initProjectChart = () => {
  if (!projectChartRef.value) return
  
  const chart = echarts.init(projectChartRef.value)
  const { project_distribution } = statisticsData.value
  
  console.log('项目分布数据:', project_distribution)
  
  if (!project_distribution || project_distribution.length === 0) {
    console.warn('项目分布数据为空')
    return
  }
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [
      {
        name: '项目分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '14',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: project_distribution.map((item: any) => ({
          name: item.name,
          value: item.value
        }))
      }
    ]
  }
  
  console.log('项目图表配置:', option)
  chart.setOption(option)
}

const openJobDetail = (url: string) => {
  if (url) {
    window.open(url, '_blank')
  }
}

// 格式化执行时长
const formatDuration = (seconds: number) => {
  if (!seconds) return '0秒'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  } else if (minutes > 0) {
    return `${minutes}分钟${secs}秒`
  } else {
    return `${secs}秒`
  }
}

// 获取调度器标签类型
const getSchedulerTagType = (schedulerType: string) => {
  switch (schedulerType) {
    case 'Azkaban':
      return 'warning'
    case 'DolphinScheduler':
      return 'success'
    default:
      return 'info'
  }
}

// 获取状态标签类型
const getStatusTagType = (status: string) => {
  switch (status) {
    case 'FAILED':
    case 'FAILURE':
    case 'KILL':
    case 'KILLED':
      return 'danger'
    case 'STOP':
      return 'warning'
    case 'SUCCESS':
    case 'SUCCEEDED':
      return 'success'
    default:
      return 'info'
  }
}

// 获取集群标签类型
const getClusterTagType = (clusterId: string) => {
  switch (clusterId) {
    case 'cdh':
      return 'warning'
    case 'apache':
      return 'success'
    default:
      return 'info'
  }
}

// 获取集群显示名称
const getClusterDisplayName = (clusterId: string) => {
  const cluster = clusters.value.find(c => c.id === clusterId)
  return cluster ? cluster.name : clusterId
}

// 获取调度器信息
const getSchedulerInfo = (clusterId: string) => {
  const cluster = clusters.value.find(c => c.id === clusterId)
  if (!cluster) return '未知'
  
  if (cluster.schedulers.includes('azkaban') && cluster.schedulers.includes('dolphinscheduler')) {
    return 'Azkaban + DolphinScheduler'
  } else if (cluster.schedulers.includes('azkaban')) {
    return 'Azkaban'
  } else if (cluster.schedulers.includes('dolphinscheduler')) {
    return 'DolphinScheduler'
  } else {
    return '未知调度器'
  }
}

// 分页处理函数
const handleFailedJobsSizeChange = (size: number) => {
  failedJobsData.value.size = size
  failedJobsData.value.page = 1
  queryFailedJobs()
}

const handleFailedJobsPageChange = (page: number) => {
  failedJobsData.value.page = page
  queryFailedJobs()
}

// 查询失败任务列表（支持分页）
const queryFailedJobs = async () => {
  if (!selectedCluster.value || !dateRange.value[0] || !dateRange.value[1]) {
    return
  }
  
  try {
    const [startDate, endDate] = dateRange.value
    const result = await businessService.getFailedJobs(
      selectedCluster.value, 
      startDate, 
      endDate, 
      failedJobsData.value.page, 
      failedJobsData.value.size
    )
    failedJobsData.value = result
  } catch (error: any) {
    console.error('查询失败任务失败:', error)
    ElMessage.error(`查询失败任务失败: ${error.message || '未知错误'}`)
  }
}
</script>

<style scoped>
.business-monitoring {
  padding: 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.page-header {
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left h1 {
  color: #2d3748;
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-section {
  margin-bottom: 24px;
}

.table-section {
  margin-bottom: 24px;
}

.chart-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-panel {
  margin-bottom: 24px;
}

.controls {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.overview-section,
.failed-jobs-section {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .header-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.card-header .header-left h3 {
  margin: 0;
}

.cluster-info {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: white;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
}

.stat-label {
  font-size: 14px;
  color: #718096;
  margin-top: 4px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 16px;
  padding: 16px 0;
  border-top: 1px solid #e2e8f0;
}
</style> 