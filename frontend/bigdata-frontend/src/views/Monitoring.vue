<template>
  <div class="monitoring-dashboard">
    <!-- 仪表盘标题 -->
    <div class="dashboard-header">
      <div class="header-content">
        <div class="header-left">
          <h1>
            <el-icon class="title-icon"><TrendCharts /></el-icon>
            监控仪表盘
          </h1>
          <p>集群监控系统总览 - 实时掌握大数据平台运行状态</p>
        </div>
        <div class="header-actions">
          <div class="status-info">
            <el-tag :type="getSystemHealthType()" size="large" effect="dark">
              <el-icon><component :is="getSystemHealthIcon()" /></el-icon>
              {{ getSystemHealthText() }}
            </el-tag>
          </div>
          <el-button 
            @click="refreshAllData" 
            :loading="loading" 
            type="primary"
            :icon="Refresh"
            size="default"
          >
            {{ loading ? '刷新中...' : '全局刷新' }}
          </el-button>
        </div>
      </div>
      
      <!-- 最后更新时间 -->
      <div class="update-info">
        <el-icon><Clock /></el-icon>
        <span>最后更新: {{ formatTime(lastUpdateTime) }}</span>
      </div>
    </div>

    <!-- 关键指标摘要 -->
    <div class="metrics-summary">
      <div class="summary-header">
        <h3>
          <el-icon class="section-icon"><DataBoard /></el-icon>
          关键指标摘要
        </h3>
        <el-tag size="small" type="info">Prometheus数据源</el-tag>
      </div>
      
      <div class="metrics-grid">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6" :lg="6">
            <div class="summary-card cluster-health">
              <div class="card-header">
                <div class="card-icon">
                  <el-icon><Monitor /></el-icon>
                </div>
                <div class="card-title">集群健康</div>
              </div>
              <div class="card-content">
                <div class="main-metric">
                  <span class="metric-value">{{ clusterHealth.healthy_nodes || 0 }}</span>
                  <span class="metric-unit">/ {{ clusterHealth.total_nodes || 0 }}</span>
                </div>
                <div class="metric-label">在线节点</div>
                <div class="card-progress">
                  <el-progress 
                    :percentage="getClusterHealthPercentage()" 
                    :status="getClusterHealthStatus()"
                    :stroke-width="6"
                    :show-text="false"
                  />
                </div>
              </div>
            </div>
          </el-col>
          
          <el-col :xs="24" :sm="12" :md="6" :lg="6">
            <div class="summary-card resource-usage">
              <div class="card-header">
                <div class="card-icon">
                  <el-icon><Cpu /></el-icon>
                </div>
                <div class="card-title">平均CPU</div>
              </div>
              <div class="card-content">
                <div class="main-metric">
                  <span class="metric-value">{{ (clusterHealth.avg_cpu_usage || 0).toFixed(1) }}</span>
                  <span class="metric-unit">%</span>
                </div>
                <div class="metric-label">CPU使用率</div>
                <div class="card-progress">
                  <el-progress 
                    :percentage="clusterHealth.avg_cpu_usage || 0" 
                    :status="getResourceStatus(clusterHealth.avg_cpu_usage, [70, 90])"
                    :stroke-width="6"
                    :show-text="false"
                  />
                </div>
              </div>
            </div>
          </el-col>
          
          <el-col :xs="24" :sm="12" :md="6" :lg="6">
            <div class="summary-card memory-usage">
              <div class="card-header">
                <div class="card-icon">
                  <el-icon><TakeawayBox /></el-icon>
                </div>
                <div class="card-title">平均内存</div>
              </div>
              <div class="card-content">
                <div class="main-metric">
                  <span class="metric-value">{{ (clusterHealth.avg_memory_usage || 0).toFixed(1) }}</span>
                  <span class="metric-unit">%</span>
                </div>
                <div class="metric-label">内存使用率</div>
                <div class="card-progress">
                  <el-progress 
                    :percentage="clusterHealth.avg_memory_usage || 0" 
                    :status="getResourceStatus(clusterHealth.avg_memory_usage, [80, 95])"
                    :stroke-width="6"
                    :show-text="false"
                  />
                </div>
              </div>
            </div>
          </el-col>
          
          <el-col :xs="24" :sm="12" :md="6" :lg="6">
            <div class="summary-card component-health">
              <div class="card-header">
                <div class="card-icon">
                  <el-icon><Setting /></el-icon>
                </div>
                <div class="card-title">组件健康</div>
              </div>
              <div class="card-content">
                <div class="main-metric">
                  <span class="metric-value">{{ getHealthyComponentsCount() }}</span>
                  <span class="metric-unit">/ {{ getTotalComponentsCount() }}</span>
                </div>
                <div class="metric-label">健康组件</div>
                <div class="card-progress">
                  <el-progress 
                    :percentage="getComponentHealthPercentage()" 
                    :status="getComponentHealthStatus()"
                    :stroke-width="6"
                    :show-text="false"
                  />
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 快速导航 -->
    <div class="quick-navigation">
      <div class="nav-header">
        <h3>
          <el-icon class="section-icon"><Grid /></el-icon>
          监控导航
        </h3>
        <span class="nav-description">快速访问各监控模块</span>
      </div>
      
      <div class="nav-grid">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" :lg="8">
            <div class="nav-card" @click="navigateTo('/cluster/overview')">
              <div class="nav-icon cluster-overview">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="nav-content">
                <h4>集群总览</h4>
                <p>查看节点状态、资源使用率、系统负载等集群级别监控数据</p>
                <div class="nav-stats">
                  <span>{{ clusterHealth.total_nodes || 0 }} 个节点</span>
                  <span class="separator">•</span>
                  <span :class="getClusterStatusClass()">{{ getClusterStatusText() }}</span>
                </div>
              </div>
              <div class="nav-arrow">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </el-col>
          
          <el-col :xs="24" :sm="12" :md="8" :lg="8">
            <div class="nav-card" @click="navigateTo('/cluster/components')">
              <div class="nav-icon component-monitoring">
                <el-icon><DataBoard /></el-icon>
              </div>
              <div class="nav-content">
                <h4>组件监控</h4>
                <p>监控HDFS、YARN、Spark等大数据组件的运行状态和健康情况</p>
                <div class="nav-stats">
                  <span>{{ getTotalComponentsCount() }} 个组件</span>
                  <span class="separator">•</span>
                  <span :class="getComponentsStatusClass()">{{ getComponentsStatusText() }}</span>
                </div>
              </div>
              <div class="nav-arrow">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </el-col>
          
          <el-col :xs="24" :sm="12" :md="8" :lg="8">
            <div class="nav-card" @click="navigateTo('/alert-rules')">
              <div class="nav-icon alert-management">
                <el-icon><Bell /></el-icon>
              </div>
              <div class="nav-content">
                <h4>告警管理</h4>
                <p>查看告警规则、历史告警、配置通知模板等告警相关功能</p>
                <div class="nav-stats">
                  <span>告警系统</span>
                  <span class="separator">•</span>
                  <span class="status-active">运行中</span>
                </div>
              </div>
              <div class="nav-arrow">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 系统状态概览 -->
    <div class="system-status">
      <div class="status-header">
        <h3>
          <el-icon class="section-icon"><List /></el-icon>
          系统状态概览
        </h3>
      </div>
      
      <div class="status-grid">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="status-card">
              <h4>集群节点状态分布</h4>
              <div class="status-chart">
                <div class="status-item">
                  <div class="status-indicator online"></div>
                  <span class="status-label">在线节点</span>
                  <span class="status-value">{{ clusterHealth.healthy_nodes || 0 }}</span>
                </div>
                <div class="status-item">
                  <div class="status-indicator offline"></div>
                  <span class="status-label">离线节点</span>
                  <span class="status-value">{{ clusterHealth.unhealthy_nodes || 0 }}</span>
                </div>
                <div class="status-item">
                  <div class="status-indicator warning"></div>
                  <span class="status-label">警告节点</span>
                  <span class="status-value">{{ getWarningNodesCount() }}</span>
                </div>
              </div>
            </div>
          </el-col>
          
          <el-col :span="12">
            <div class="status-card">
              <h4>大数据组件状态</h4>
              <div class="components-status">
                <div 
                  v-for="(component, name) in componentsStatus" 
                  :key="name"
                  class="component-status-item"
                  :class="getComponentStatusClass(component.status)"
                >
                  <div class="component-icon">
                    <el-icon><component :is="getComponentIcon(name)" /></el-icon>
                  </div>
                  <div class="component-info">
                    <span class="component-name">{{ getComponentDisplayName(name) }}</span>
                    <el-tag 
                      :type="getStatusTagType(component.status)" 
                      size="small"
                      effect="plain"
                    >
                      {{ getStatusText(component.status) }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && !hasData" class="loading-state">
      <el-skeleton :rows="8" animated />
      <p class="loading-text">正在加载监控数据...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  Monitor,
  TrendCharts,
  DataBoard,
  Cpu,
  TakeawayBox,
  Setting,
  Grid,
  ArrowRight,
  Bell,
  List,
  Clock,
  CircleCheck,
  CircleClose,
  Warning,
  Files,
  Connection,
  Document
} from '@element-plus/icons-vue'
import { clusterService } from '@/services'

const router = useRouter()

// 数据状态
const loading = ref(false)
const clusterHealth = ref<any>({})
const componentsStatus = ref<Record<string, any>>({})
const lastUpdateTime = ref<string>('')

// 定时器
let refreshTimer: number | null = null

// 计算属性
const hasData = computed(() => {
  return Object.keys(clusterHealth.value).length > 0 || Object.keys(componentsStatus.value).length > 0
})

// 生命周期
onMounted(() => {
  refreshAllData()
  // 每60秒自动刷新
  refreshTimer = setInterval(refreshAllData, 60000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})

// 刷新所有数据
const refreshAllData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadClusterHealth(),
      loadComponentsStatus()
    ])
    lastUpdateTime.value = new Date().toISOString()
    ElMessage.success('监控数据已刷新')
  } catch (error) {
    console.error('刷新数据失败:', error)
    ElMessage.error('刷新数据失败')
  } finally {
    loading.value = false
  }
}

// 加载集群健康状态
const loadClusterHealth = async () => {
  try {
    const response = await clusterService.getClusterHealth()
    if (response.code === 0) {
      clusterHealth.value = response.data.details || {}
    }
  } catch (error) {
    console.error('加载集群健康状态失败:', error)
  }
}

// 加载组件状态
const loadComponentsStatus = async () => {
  try {
    const response = await clusterService.getClusterComponents()
    if (response.code === 0) {
      componentsStatus.value = response.data.components || {}
    }
  } catch (error) {
    console.error('加载组件状态失败:', error)
  }
}

// 系统健康相关函数
const getSystemHealthType = () => {
  const clusterHealthy = getClusterHealthPercentage() >= 80
  const componentsHealthy = getComponentHealthPercentage() >= 80
  
  if (clusterHealthy && componentsHealthy) return 'success'
  if (clusterHealthy || componentsHealthy) return 'warning'
  return 'danger'
}

const getSystemHealthIcon = () => {
  const type = getSystemHealthType()
  if (type === 'success') return CircleCheck
  if (type === 'warning') return Warning
  return CircleClose
}

const getSystemHealthText = () => {
  const type = getSystemHealthType()
  if (type === 'success') return '系统健康'
  if (type === 'warning') return '部分异常'
  return '系统异常'
}

// 集群健康相关函数
const getClusterHealthPercentage = () => {
  const total = clusterHealth.value.total_nodes || 0
  const healthy = clusterHealth.value.healthy_nodes || 0
  return total > 0 ? Math.round((healthy / total) * 100) : 0
}

const getClusterHealthStatus = () => {
  const percentage = getClusterHealthPercentage()
  if (percentage >= 90) return 'success'
  if (percentage >= 70) return 'warning'
  return 'exception'
}

const getClusterStatusClass = () => {
  const percentage = getClusterHealthPercentage()
  if (percentage >= 90) return 'status-healthy'
  if (percentage >= 70) return 'status-warning'
  return 'status-error'
}

const getClusterStatusText = () => {
  const percentage = getClusterHealthPercentage()
  if (percentage >= 90) return '健康'
  if (percentage >= 70) return '警告'
  return '异常'
}

// 组件健康相关函数
const getHealthyComponentsCount = () => {
  return Object.values(componentsStatus.value).filter(
    (component: any) => component.status === 'healthy'
  ).length
}

const getTotalComponentsCount = () => {
  return Object.keys(componentsStatus.value).length
}

const getComponentHealthPercentage = () => {
  const total = getTotalComponentsCount()
  const healthy = getHealthyComponentsCount()
  return total > 0 ? Math.round((healthy / total) * 100) : 0
}

const getComponentHealthStatus = () => {
  const percentage = getComponentHealthPercentage()
  if (percentage >= 90) return 'success'
  if (percentage >= 70) return 'warning'
  return 'exception'
}

const getComponentsStatusClass = () => {
  const percentage = getComponentHealthPercentage()
  if (percentage >= 90) return 'status-healthy'
  if (percentage >= 70) return 'status-warning'
  return 'status-error'
}

const getComponentsStatusText = () => {
  const percentage = getComponentHealthPercentage()
  if (percentage >= 90) return '健康'
  if (percentage >= 70) return '部分异常'
  return '异常'
}

// 资源状态函数
const getResourceStatus = (usage: number, thresholds: [number, number]) => {
  if (usage >= thresholds[1]) return 'exception'
  if (usage >= thresholds[0]) return 'warning'
  return 'success'
}

// 警告节点数（CPU或内存使用率过高的节点）
const getWarningNodesCount = () => {
  const cpuWarning = (clusterHealth.value.avg_cpu_usage || 0) >= 80
  const memoryWarning = (clusterHealth.value.avg_memory_usage || 0) >= 80
  return cpuWarning || memoryWarning ? 1 : 0
}

// 组件相关函数
const getComponentDisplayName = (name: string) => {
  const displayNames: Record<string, string> = {
    'hdfs': 'HDFS',
    'yarn': 'YARN',
    'spark': 'Spark',
    'hive': 'Hive',
    'kafka': 'Kafka',
    'zookeeper': 'ZooKeeper',
    'flink': 'Flink'
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

const getComponentStatusClass = (status: string) => {
  return `component-${status}`
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

// 导航函数
const navigateTo = (path: string) => {
  router.push(path)
}

// 工具函数
const formatTime = (timeStr: string) => {
  if (!timeStr) return '未知'
  try {
    return new Date(timeStr).toLocaleString()
  } catch {
    return '未知'
  }
}
</script>

<style scoped>
.monitoring-dashboard {
  padding: 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.dashboard-header {
  margin-bottom: 32px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #667eea;
  transition: all 0.3s ease;
}

.dashboard-header:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
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

.header-left p {
  color: #718096;
  font-size: 16px;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-info .el-tag {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #667eea;
}

.update-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #718096;
  font-size: 14px;
}

.metrics-summary {
  margin-bottom: 32px;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.summary-header h3 {
  color: #2d3748;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon {
  font-size: 24px;
  color: #667eea;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.summary-card {
  border-radius: 20px;
  border: none;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  overflow: hidden;
}

.summary-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.15);
}

.summary-card .el-card__header {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  font-weight: 600;
  color: #2d3748;
  padding: 20px 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #e0e7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
}

.card-content {
  padding: 0 24px 24px;
}

.main-metric {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 36px;
  font-weight: 700;
  color: #667eea;
}

.metric-unit {
  font-size: 16px;
  color: #718096;
}

.metric-label {
  font-size: 14px;
  color: #718096;
  margin-top: 4px;
}

.card-progress {
  margin-top: 12px;
}

.quick-navigation {
  margin-bottom: 32px;
}

.nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.nav-header h3 {
  color: #2d3748;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-description {
  color: #718096;
  font-size: 14px;
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.nav-card {
  border-radius: 20px;
  border: none;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  overflow: hidden;
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 20px;
}

.nav-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.15);
}

.nav-card .el-card__header {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  font-weight: 600;
  color: #2d3748;
  padding: 0;
}

.nav-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: #e0e7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
  font-size: 28px;
}

.nav-icon.cluster-overview {
  background: #dbeafe;
  color: #3b82f6;
}

.nav-icon.component-monitoring {
  background: #dcfce7;
  color: #16a34a;
}

.nav-icon.alert-management {
  background: #fef3c7;
  color: #f59e0b;
}

.nav-content h4 {
  color: #2d3748;
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.nav-content p {
  color: #718096;
  font-size: 14px;
  margin: 0 0 16px 0;
}

.nav-stats {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #718096;
  font-size: 14px;
}

.nav-stats .separator {
  color: #e0e0e0;
}

.nav-arrow {
  margin-left: auto;
  color: #667eea;
  font-size: 24px;
}

.system-status {
  margin-bottom: 32px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.status-header h3 {
  color: #2d3748;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.status-card {
  border-radius: 20px;
  border: none;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  overflow: hidden;
}

.status-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.15);
}

.status-card .el-card__header {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  font-weight: 600;
  color: #2d3748;
  padding: 20px 24px;
}

.status-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-indicator {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.status-label {
  font-size: 14px;
  color: #718096;
}

.status-value {
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
}

.components-status {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.component-status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  background: #f8f9fa;
  transition: all 0.2s ease;
}

.component-status-item:hover {
  border-color: #1a73e8;
  box-shadow: 0 2px 8px rgba(26, 115, 232, 0.1);
}

.component-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #e0e7ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #667eea;
  font-size: 20px;
}

.component-info {
  flex: 1;
}

.component-name {
  font-size: 14px;
  font-weight: 500;
  color: #2d3748;
  margin-bottom: 4px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #718096;
  font-size: 16px;
}

.loading-text {
  margin-top: 16px;
}

:deep(.el-card) {
  border-radius: 16px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
}

:deep(.el-card__header) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%);
  border-bottom: 1px solid rgba(102, 126, 234, 0.15);
  font-weight: 600;
  color: #2d3748;
  padding: 16px 20px;
}

:deep(.el-table) {
  border-radius: 16px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
}

:deep(.el-table th) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%);
  color: #2d3748;
  font-weight: 600;
  border-bottom: 1px solid rgba(102, 126, 234, 0.15);
}

:deep(.el-table td) {
  border-bottom: 1px solid rgba(102, 126, 234, 0.08);
  background: rgba(255, 255, 255, 0.7);
}

:deep(.el-table__row:hover) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%) !important;
  transform: scale(1.01);
}

:deep(.el-tag) {
  border-radius: 4px;
  font-weight: 400;
}

:deep(.el-progress) {
  width: 100%;
}

:deep(.el-button) {
  border-radius: 6px;
  font-weight: 400;
}
</style> 