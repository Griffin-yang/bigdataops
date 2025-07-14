<template>
    <div class="cluster-components">
          <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h2>
            <el-icon class="title-icon"><DataBoard /></el-icon>
            大数据组件监控
          </h2>
          <p>实时监控HDFS、YARN、Spark等大数据组件的运行状态和健康情况</p>
        </div>
        <div class="header-actions">
          <div class="status-summary">
            <span class="summary-item">
              总组件: <strong>{{ Object.keys(components).length }}</strong>
            </span>
            <span class="summary-item healthy">
              健康: <strong>{{ getHealthyComponentsCount() }}</strong>
            </span>
            <span class="summary-item error">
              异常: <strong>{{ getUnhealthyComponentsCount() }}</strong>
            </span>
          </div>
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
      
      <!-- 最后更新时间 -->
      <div class="update-info">
        <el-icon><Clock /></el-icon>
        <span>最后更新: {{ getLastUpdateTime() }}</span>
      </div>
    </div>
  
      <!-- 组件概览卡片 -->
      <div class="components-grid">
        <el-row :gutter="24">
          <el-col 
            v-for="(component, name) in components" 
            :key="name"
            :xs="24" :sm="12" :md="12" :lg="8" :xl="6"
          >
            <div 
              class="component-card" 
              :class="getComponentCardClass(component.status)"
              @click="showComponentDetail(name, component)"
            >
              <div class="card-header">
                <div class="component-icon">
                  <el-icon :size="32">
                    <component :is="getComponentIcon(name)" />
                  </el-icon>
                </div>
                <div class="component-title">
                  <h3>{{ getComponentDisplayName(name) }}</h3>
                  <div class="component-status">
                    <el-tag 
                      :type="getStatusTagType(component.status)" 
                      size="small"
                      effect="dark"
                    >
                      {{ getStatusText(component.status) }}
                    </el-tag>
                  </div>
                </div>
              </div>
              
              <div class="card-content">
                <div class="metric-item">
                  <span class="metric-label">服务实例</span>
                  <span class="metric-value">
                    {{ component.healthy_instances || 0 }} / {{ component.total_instances || 0 }}
                  </span>
                </div>
                
                <div class="metric-item">
                  <span class="metric-label">服务数量</span>
                  <span class="metric-value">{{ (component.services || []).length }}</span>
                </div>
                
                <div class="metric-item">
                  <span class="metric-label">最后更新</span>
                  <span class="metric-value time">{{ formatTime(component.update_time) }}</span>
                </div>
              </div>
              
              <!-- 健康度进度条 -->
              <div class="health-progress">
                <el-progress 
                  :percentage="getHealthPercentage(component)"
                  :stroke-width="6"
                  :status="getProgressStatus(component.status)"
                  :show-text="false"
                />
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
  
      <!-- 组件详情对话框 -->
      <el-dialog
        v-model="detailDialogVisible"
        :title="`${getComponentDisplayName(selectedComponent)} 详细信息`"
        width="80%"
        :before-close="handleDetailClose"
      >
        <div v-if="componentDetail" class="component-detail">
          <!-- 概览信息 -->
          <div class="detail-overview">
            <el-row :gutter="16">
              <el-col :span="6">
                <el-statistic title="总实例数" :value="componentDetail.total_instances || 0" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="健康实例" :value="componentDetail.healthy_instances || 0" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="异常实例" :value="(componentDetail.total_instances || 0) - (componentDetail.healthy_instances || 0)" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="健康率" :value="getHealthPercentage(componentDetail)" suffix="%" />
              </el-col>
            </el-row>
          </div>
  
          <!-- 服务列表 -->
          <div class="services-section">
            <h4>服务实例详情</h4>
            <el-table :data="componentDetail.services || []" style="width: 100%">
              <el-table-column prop="display_name" label="服务名称" min-width="150" />
              <el-table-column label="状态" width="100">
                <template #default="{ row }">
                  <el-tag 
                    :type="getServiceStatusType(row)"
                    size="small"
                  >
                    {{ getServiceStatusText(row) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="total_instances" label="实例数" width="80" />
              <el-table-column prop="healthy_instances" label="健康实例" width="100" />
              <el-table-column label="实例详情" min-width="300">
                <template #default="{ row }">
                  <div class="instances-list">
                    <el-tag
                      v-for="instance in (row.instances || []).slice(0, 3)"
                      :key="instance.instance"
                      :type="instance.status === 'up' ? 'success' : 'danger'"
                      size="small"
                      style="margin-right: 4px; margin-bottom: 2px;"
                    >
                      {{ instance.instance }}
                    </el-tag>
                    <span v-if="(row.instances || []).length > 3">
                      +{{ (row.instances || []).length - 3 }} 更多
                    </span>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
  
          <!-- 详细指标 -->
          <div v-if="componentDetail.detailed_metrics" class="metrics-section">
            <h4>详细监控指标</h4>
            <el-row :gutter="16">
              <el-col 
                v-for="(metric, metricName) in componentDetail.detailed_metrics" 
                :key="metricName"
                :span="8"
              >
                <div class="metric-card">
                  <div class="metric-title">{{ metric.description || metricName }}</div>
                  <div class="metric-query">{{ metric.query }}</div>
                  <div class="metric-result">
                    <pre>{{ formatMetricResult(metric.result) }}</pre>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-dialog>
  
      <!-- 加载状态 -->
      <div v-if="loading && Object.keys(components).length === 0" class="loading-state">
        <el-skeleton :rows="6" animated />
      </div>
  
      <!-- 空状态 -->
      <div v-if="!loading && Object.keys(components).length === 0" class="empty-state">
        <el-empty description="未发现组件数据">
          <el-button type="primary" @click="refreshData">重新加载</el-button>
        </el-empty>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, onUnmounted } from 'vue'
  import { ElMessage } from 'element-plus'
  import {
  Refresh,
  Monitor,
  Setting,
  DataBoard,
  Cpu,
  Connection,
  Files,
  Document,
  Clock
} from '@element-plus/icons-vue'
  import { clusterService } from '@/services'
  
  // 数据状态
  const components = ref<Record<string, any>>({})
  const loading = ref(false)
  const detailDialogVisible = ref(false)
  const selectedComponent = ref('')
  const componentDetail = ref<any>(null)
  
  // 定时器
  let refreshTimer: number | null = null
  
  // 生命周期
  onMounted(() => {
    refreshData()
    // 每30秒自动刷新
    refreshTimer = setInterval(refreshData, 30000)
  })
  
  onUnmounted(() => {
    if (refreshTimer) {
      clearInterval(refreshTimer)
    }
  })
  
  // 刷新数据
  const refreshData = async () => {
    loading.value = true
    try {
      const response = await clusterService.getClusterComponents()
      if (response.code === 0) {
        components.value = response.data.components || {}
      } else {
        ElMessage.error(`加载组件数据失败: ${response.msg}`)
      }
    } catch (error) {
      console.error('加载组件数据失败:', error)
      ElMessage.error('加载组件数据失败')
    } finally {
      loading.value = false
    }
  }
  
  // 显示组件详情
  const showComponentDetail = async (componentName: string, component: any) => {
    selectedComponent.value = componentName
    detailDialogVisible.value = true
    
    try {
      const response = await clusterService.getComponentDetail(componentName)
      if (response.code === 0) {
        componentDetail.value = response.data
      } else {
        ElMessage.error(`加载组件详情失败: ${response.msg}`)
        componentDetail.value = component
      }
    } catch (error) {
      console.error('加载组件详情失败:', error)
      componentDetail.value = component
    }
  }
  
  // 关闭详情对话框
  const handleDetailClose = () => {
    detailDialogVisible.value = false
    selectedComponent.value = ''
    componentDetail.value = null
  }
  
  // 统计函数
const getHealthyComponentsCount = () => {
  return Object.values(components.value).filter(
    (component: any) => component.status === 'healthy'
  ).length
}

const getUnhealthyComponentsCount = () => {
  return Object.values(components.value).filter(
    (component: any) => component.status !== 'healthy'
  ).length
}

const getLastUpdateTime = () => {
  const updates = Object.values(components.value)
    .map((component: any) => component.update_time)
    .filter(Boolean)
  
  if (updates.length === 0) return '未知'
  
  const latest = new Date(Math.max(...updates.map(time => new Date(time).getTime())))
  return latest.toLocaleTimeString()
}

// 工具函数
const getComponentDisplayName = (name: string) => {
  const displayNames: Record<string, string> = {
    'hdfs': 'HDFS 分布式文件系统',
    'yarn': 'YARN 资源管理器',
    'spark': 'Spark 计算引擎',
    'hive': 'Hive 数据仓库',
    'kafka': 'Kafka 消息队列',
    'zookeeper': 'ZooKeeper 协调服务',
    'flink': 'Flink 流处理引擎'
  }
  return displayNames[name] || name.toUpperCase()
}
  
  const getComponentIcon = (name: string) => {
    const icons: Record<string, any> = {
      'hdfs': Files,
      'yarn': Cpu,
      'spark': DataBoard,
      'hive': Document,
      'kafka': Connection,
      'zookeeper': Monitor,
      'flink': Setting
    }
    return icons[name] || Monitor
  }
  
  const getComponentCardClass = (status: string) => {
    const classes: Record<string, string> = {
      'healthy': 'card-healthy',
      'warning': 'card-warning',
      'unhealthy': 'card-unhealthy',
      'unknown': 'card-unknown'
    }
    return classes[status] || 'card-unknown'
  }
  
  const getStatusTagType = (status: string) => {
    const types: Record<string, string> = {
      'healthy': 'success',
      'warning': 'warning',
      'unhealthy': 'danger',
      'unknown': 'info'
    }
    return types[status] || 'info'
  }
  
  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      'healthy': '健康',
      'warning': '警告',
      'unhealthy': '异常',
      'unknown': '未知'
    }
    return texts[status] || '未知'
  }
  
  const getHealthPercentage = (component: any) => {
    const total = component.total_instances || 0
    const healthy = component.healthy_instances || 0
    return total > 0 ? Math.round((healthy / total) * 100) : 0
  }
  
  const getProgressStatus = (status: string) => {
    const statusMap: Record<string, string> = {
      'healthy': 'success',
      'warning': 'warning',
      'unhealthy': 'exception',
      'unknown': 'info'
    }
    return statusMap[status] || undefined
  }
  
  const getServiceStatusType = (service: any) => {
    const total = service.total_instances || 0
    const healthy = service.healthy_instances || 0
    
    if (total === 0) return 'info'
    if (healthy === total) return 'success'
    if (healthy > 0) return 'warning'
    return 'danger'
  }
  
  const getServiceStatusText = (service: any) => {
    const total = service.total_instances || 0
    const healthy = service.healthy_instances || 0
    
    if (total === 0) return '无实例'
    if (healthy === total) return '健康'
    if (healthy > 0) return '部分异常'
    return '全部异常'
  }
  
  const formatTime = (timeStr: string) => {
    if (!timeStr) return '未知'
    try {
      return new Date(timeStr).toLocaleTimeString()
    } catch {
      return '未知'
    }
  }
  
  const formatMetricResult = (result: any) => {
    if (!result || result.status !== 'success') {
      return '无数据'
    }
    
    const data = result.data?.result || []
    if (data.length === 0) {
      return '无数据'
    }
    
    return JSON.stringify(data.slice(0, 3), null, 2)
  }
  </script>
  
  <style scoped>
  .cluster-components {
    padding: 20px;
    background: #f5f5f5;
    min-height: calc(100vh - 60px);
  }
  
  /* 页面头部 */
.page-header {
  margin-bottom: 24px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #409eff;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.header-left h2 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 28px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  color: #409eff;
}

.header-left p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.status-summary {
  display: flex;
  gap: 24px;
  margin-right: 8px;
}

.summary-item {
  font-size: 14px;
  color: #666;
}

.summary-item strong {
  font-size: 18px;
  margin-left: 4px;
}

.summary-item.healthy strong {
  color: #67c23a;
}

.summary-item.error strong {
  color: #f56c6c;
}

.update-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #999;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}
  
  /* 组件网格 */
  .components-grid {
    margin-bottom: 24px;
  }
  
  /* 组件卡片 */
  .component-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    cursor: pointer;
    border-left: 4px solid #e5e5e5;
    margin-bottom: 16px;
  }
  
  .component-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.15);
  }
  
  .component-card.card-healthy {
    border-left-color: #67c23a;
  }
  
  .component-card.card-warning {
    border-left-color: #e6a23c;
  }
  
  .component-card.card-unhealthy {
    border-left-color: #f56c6c;
  }
  
  .component-card.card-unknown {
    border-left-color: #909399;
  }
  
  .card-header {
    display: flex;
    align-items: center;
    margin-bottom: 16px;
  }
  
  .component-icon {
    width: 50px;
    height: 50px;
    border-radius: 10px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    margin-right: 16px;
  }
  
  .component-title h3 {
    margin: 0 0 6px 0;
    font-size: 18px;
    color: #333;
  }
  
  .component-status {
    margin-top: 4px;
  }
  
  .card-content {
    margin-bottom: 16px;
  }
  
  .metric-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    padding: 6px 0;
  }
  
  .metric-label {
    color: #666;
    font-size: 14px;
  }
  
  .metric-value {
    color: #333;
    font-weight: 500;
    font-size: 14px;
  }
  
  .metric-value.time {
    color: #999;
    font-size: 12px;
  }
  
  .health-progress {
    margin-top: 16px;
  }
  
  /* 详情对话框 */
  .component-detail {
    padding: 0;
  }
  
  .detail-overview {
    margin-bottom: 24px;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
  }
  
  .services-section,
  .metrics-section {
    margin-bottom: 24px;
  }
  
  .services-section h4,
  .metrics-section h4 {
    margin: 0 0 16px 0;
    color: #333;
    font-size: 16px;
    border-bottom: 2px solid #e5e5e5;
    padding-bottom: 8px;
  }
  
  .instances-list {
    max-width: 300px;
  }
  
  .metric-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
  }
  
  .metric-title {
    font-weight: 500;
    color: #333;
    margin-bottom: 8px;
  }
  
  .metric-query {
    font-size: 12px;
    color: #666;
    font-family: monospace;
    background: #fff;
    padding: 4px 8px;
    border-radius: 4px;
    margin-bottom: 8px;
  }
  
  .metric-result {
    max-height: 200px;
    overflow-y: auto;
  }
  
  .metric-result pre {
    font-size: 12px;
    color: #333;
    margin: 0;
    white-space: pre-wrap;
    word-break: break-all;
  }
  
  /* 状态样式 */
  .loading-state,
  .empty-state {
    padding: 40px;
    text-align: center;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  /* 响应式样式 */
  @media (max-width: 768px) {
    .cluster-components {
      padding: 10px;
    }
    
    .page-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;
    }
    
    .component-card {
      margin-bottom: 12px;
    }
    
    .card-header {
      flex-direction: column;
      text-align: center;
    }
    
    .component-icon {
      margin-right: 0;
      margin-bottom: 12px;
    }
  }
  </style>