<template>
  <div class="monitoring-container">
    <!-- 集群概览 -->
    <div class="page-header">
      <h2>集群概览</h2>
      <div style="float: right">
        <el-button type="primary" @click="toClusterOverview" style="margin-right: 12px;">
          <el-icon><Monitor /></el-icon>
          集群监控
        </el-button>
        <el-button type="text" size="small" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>
    
    <div class="metrics-section">
      <div class="metric-grid">
        <div class="metric-item" v-for="metric in clusterMetrics" :key="metric.name">
          <div class="metric-title">
            <el-icon><component :is="metric.icon" /></el-icon>
            <span>{{ metric.name }}</span>
          </div>
          <div class="metric-value">{{ metric.value }}</div>
          <div class="metric-description">实时监控数据</div>
        </div>
      </div>
    </div>

    <!-- 服务器列表 -->
    <el-row :gutter="20" class="servers-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>服务器节点</span>
          </template>
          
          <el-table :data="servers" v-loading="loading">
            <el-table-column prop="hostname" label="主机名" width="200" />
            <el-table-column prop="ip" label="IP地址" width="150" />
            <el-table-column prop="role" label="角色" width="120">
              <template #default="scope">
                <el-tag :type="getRoleType(scope.row.role)" size="small">
                  {{ scope.row.role }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="CPU使用率" width="120">
              <template #default="scope">
                <el-progress 
                  :percentage="scope.row.cpu_usage" 
                  :color="getProgressColor(scope.row.cpu_usage)"
                  :stroke-width="8"
                />
              </template>
            </el-table-column>
            <el-table-column label="内存使用率" width="120">
              <template #default="scope">
                <el-progress 
                  :percentage="scope.row.memory_usage" 
                  :color="getProgressColor(scope.row.memory_usage)"
                  :stroke-width="8"
                />
              </template>
            </el-table-column>
            <el-table-column label="磁盘使用率" width="120">
              <template #default="scope">
                <el-progress 
                  :percentage="scope.row.disk_usage" 
                  :color="getProgressColor(scope.row.disk_usage)"
                  :stroke-width="8"
                />
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'online' ? 'success' : 'danger'" size="small">
                  {{ scope.row.status === 'online' ? '在线' : '离线' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="uptime" label="运行时间" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 服务组件状态 -->
    <el-row :gutter="20" class="services-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>大数据服务组件</span>
          </template>
          
          <div class="services-grid">
            <div 
              v-for="service in services" 
              :key="service.name"
              class="service-item"
              :class="{ 'service-error': service.status !== 'running' }"
            >
              <div class="service-icon">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="service-info">
                <div class="service-name">{{ service.name }}</div>
                <div class="service-status">
                  <el-tag 
                    :type="service.status === 'running' ? 'success' : 'danger'" 
                    size="small"
                  >
                    {{ service.status === 'running' ? '运行中' : '停止' }}
                  </el-tag>
                </div>
              </div>
              <div class="service-actions">
                <el-button 
                  v-if="service.status !== 'running'"
                  size="small" 
                  type="success"
                  @click="startService(service)"
                >
                  启动
                </el-button>
                <el-button 
                  v-else
                  size="small" 
                  type="danger"
                  @click="stopService(service)"
                >
                  停止
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>资源使用趋势</span>
          </template>
          <v-chart 
            class="chart" 
            :option="resourceTrendOption" 
            autoresize
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Monitor } from '@element-plus/icons-vue'
import { clusterService } from '@/services'

const router = useRouter()

// 数据
const loading = ref(false)
const clusterMetrics = ref([
  {
    name: '总节点数',
    value: '8',
    icon: 'Server',
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  {
    name: 'CPU平均使用率',
    value: '65%',
    icon: 'Cpu',
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  {
    name: '内存平均使用率',
    value: '72%',
    icon: 'MemoryCard',
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
  },
  {
    name: '磁盘平均使用率',
    value: '45%',
    icon: 'HardDisk',
    color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
  }
])

const servers = ref([
  {
    hostname: 'hadoop-master-01',
    ip: '192.168.1.10',
    role: 'NameNode',
    cpu_usage: 65,
    memory_usage: 72,
    disk_usage: 45,
    status: 'online',
    uptime: '15天 3小时'
  },
  {
    hostname: 'hadoop-master-02',
    ip: '192.168.1.11',
    role: 'NameNode',
    cpu_usage: 58,
    memory_usage: 68,
    disk_usage: 42,
    status: 'online',
    uptime: '15天 3小时'
  },
  {
    hostname: 'hadoop-worker-01',
    ip: '192.168.1.20',
    role: 'DataNode',
    cpu_usage: 75,
    memory_usage: 80,
    disk_usage: 55,
    status: 'online',
    uptime: '14天 8小时'
  },
  {
    hostname: 'hadoop-worker-02',
    ip: '192.168.1.21',
    role: 'DataNode',
    cpu_usage: 82,
    memory_usage: 85,
    disk_usage: 62,
    status: 'online',
    uptime: '14天 8小时'
  },
  {
    hostname: 'hadoop-worker-03',
    ip: '192.168.1.22',
    role: 'DataNode',
    cpu_usage: 45,
    memory_usage: 52,
    disk_usage: 38,
    status: 'offline',
    uptime: '0天 0小时'
  }
])

const services = ref([
  { name: 'HDFS', status: 'running' },
  { name: 'YARN', status: 'running' },
  { name: 'Spark', status: 'running' },
  { name: 'HBase', status: 'running' },
  { name: 'Kafka', status: 'running' },
  { name: 'Elasticsearch', status: 'stopped' },
  { name: 'Prometheus', status: 'running' },
  { name: 'Grafana', status: 'running' }
])

// 资源趋势图表配置
const resourceTrendOption = ref({
  title: {
    text: '近24小时资源使用率'
  },
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['CPU', '内存', '磁盘']
  },
  xAxis: {
    type: 'category',
    data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00']
  },
  yAxis: {
    type: 'value',
    max: 100,
    axisLabel: {
      formatter: '{value}%'
    }
  },
  series: [
    {
      name: 'CPU',
      type: 'line',
      data: [45, 52, 61, 68, 75, 72, 65],
      itemStyle: { color: '#409EFF' }
    },
    {
      name: '内存',
      type: 'line',
      data: [55, 58, 65, 70, 78, 75, 72],
      itemStyle: { color: '#67C23A' }
    },
    {
      name: '磁盘',
      type: 'line',
      data: [35, 38, 42, 45, 48, 46, 45],
      itemStyle: { color: '#E6A23C' }
    }
  ]
})

// 方法
const getRoleType = (role: string) => {
  const types: Record<string, string> = {
    'NameNode': 'danger',
    'DataNode': 'primary',
    'ResourceManager': 'warning',
    'NodeManager': 'info'
  }
  return types[role] || 'info'
}

const getProgressColor = (percentage: number) => {
  if (percentage < 60) return '#67C23A'
  if (percentage < 80) return '#E6A23C'
  return '#F56C6C'
}

const refreshData = () => {
  ElMessage.success('数据已刷新')
  // 这里可以重新加载数据
}

const toClusterOverview = () => {
  router.push('/cluster/overview')
}

const startService = (service: any) => {
  service.status = 'running'
  ElMessage.success(`${service.name} 服务启动成功`)
}

const stopService = (service: any) => {
  service.status = 'stopped'
  ElMessage.warning(`${service.name} 服务已停止`)
}

onMounted(() => {
  // 初始化数据
})
</script>

<style scoped>
.monitoring-container {
  padding: 24px;
  background: #faf9f7 !important;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.page-header:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 48px rgba(102, 126, 234, 0.15);
}

.title-section h2 {
  color: #2d3748;
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.subtitle {
  color: #718096;
  margin: 0;
  font-size: 14px;
  font-weight: 500;
}

.metrics-section {
  margin-bottom: 32px;
}

.section-card {
  border-radius: 20px;
  border: none;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.section-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.15);
}

.section-card :deep(.el-card__header) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
  font-weight: 600;
  color: #2d3748;
  padding: 20px 24px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.metric-item {
  padding: 20px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.metric-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

.metric-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.15);
  background: rgba(255, 255, 255, 0.8);
}

.metric-title {
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 8px;
}

.metric-description {
  font-size: 12px;
  color: #718096;
}

.servers-row,
.services-row {
  margin-bottom: 24px;
}

.servers-row :deep(.el-card),
.services-row :deep(.el-card) {
  border: 1px solid #e8eaed;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  background: #ffffff;
}

.servers-row :deep(.el-card__header),
.services-row :deep(.el-card__header) {
  background: #f8f9fa;
  border-bottom: 1px solid #e8eaed;
  padding: 16px 20px;
}

.servers-row :deep(.el-card__header span),
.services-row :deep(.el-card__header span) {
  color: #202124;
  font-weight: 500;
  font-size: 16px;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.service-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 1px solid #e8eaed;
  border-radius: 8px;
  transition: all 0.2s ease;
  background: #ffffff;
}

.service-item:hover {
  border-color: #1a73e8;
  box-shadow: 0 2px 8px rgba(26, 115, 232, 0.1);
}

.service-error {
  border-color: #ea4335;
  background: #fef7f0;
}

.service-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #1a73e8;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  color: white;
}

.service-info {
  flex: 1;
}

.service-name {
  font-weight: 500;
  color: #202124;
  margin-bottom: 4px;
}

.service-status {
  font-size: 12px;
}

.service-actions {
  margin-left: 10px;
}

.service-actions .el-button {
  height: 32px;
  padding: 0 12px;
  border-radius: 6px;
  font-weight: 400;
}

.chart {
  height: 300px;
  width: 100%;
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