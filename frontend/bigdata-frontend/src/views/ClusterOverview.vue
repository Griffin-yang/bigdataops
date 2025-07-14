<template>
    <div class="cluster-overview">
      <!-- 集群资源概览 -->
      <div class="cluster-overview-panel">
        <div class="panel-header">
          <h3>
            <el-icon class="panel-icon"><TrendCharts /></el-icon>
            集群资源概览
          </h3>
          <el-tag size="small" type="info">实时监控数据</el-tag>
        </div>
        
        <div class="metrics-grid">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="6" :lg="6">
              <div class="metric-card cluster-nodes">
                <div class="metric-header">
                  <div class="metric-icon">
                    <el-icon><Monitor /></el-icon>
                  </div>
                  <div class="metric-info">
                    <div class="metric-title">集群节点</div>
                    <div class="metric-value">{{ overview.total_nodes || 0 }}</div>
                  </div>
                </div>
                <div class="metric-details">
                  <div class="detail-item healthy">
                    <span class="detail-label">在线</span>
                    <span class="detail-value">{{ overview.healthy_nodes || 0 }}</span>
                  </div>
                  <div class="detail-item error">
                    <span class="detail-label">离线</span>
                    <span class="detail-value">{{ overview.unhealthy_nodes || 0 }}</span>
                  </div>
                </div>
                <div class="metric-progress">
                  <el-progress 
                    :percentage="getNodeHealthPercentage()" 
                    :stroke-width="4"
                    :status="getNodeHealthStatus()"
                    :show-text="false"
                  />
                </div>
              </div>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6" :lg="6">
              <div class="metric-card cpu-usage">
                <div class="metric-header">
                  <div class="metric-icon">
                    <el-icon><Cpu /></el-icon>
                  </div>
                  <div class="metric-info">
                    <div class="metric-title">CPU 使用率</div>
                    <div class="metric-value">{{ (overview.avg_cpu_usage || 0).toFixed(1) }}%</div>
                  </div>
                </div>
                <div class="metric-status">
                  <el-tag 
                    :type="getCpuTagType(overview.avg_cpu_usage)" 
                    size="small"
                    effect="dark"
                  >
                    {{ getCpuStatusText(overview.avg_cpu_usage) }}
                  </el-tag>
                </div>
                <div class="metric-progress">
                  <el-progress 
                    :percentage="overview.avg_cpu_usage || 0" 
                    :stroke-width="4"
                    :status="getCpuProgressStatus(overview.avg_cpu_usage)"
                    :show-text="false"
                  />
                </div>
              </div>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6" :lg="6">
              <div class="metric-card memory-usage">
                <div class="metric-header">
                  <div class="metric-icon">
                    <el-icon><TakeawayBox /></el-icon>
                  </div>
                  <div class="metric-info">
                    <div class="metric-title">内存使用率</div>
                    <div class="metric-value">{{ (overview.avg_memory_usage || 0).toFixed(1) }}%</div>
                  </div>
                </div>
                <div class="metric-status">
                  <el-tag 
                    :type="getMemoryTagType(overview.avg_memory_usage)" 
                    size="small"
                    effect="dark"
                  >
                    {{ getMemoryStatusText(overview.avg_memory_usage) }}
                  </el-tag>
                </div>
                <div class="metric-progress">
                  <el-progress 
                    :percentage="overview.avg_memory_usage || 0" 
                    :stroke-width="4"
                    :status="getMemoryProgressStatus(overview.avg_memory_usage)"
                    :show-text="false"
                  />
                </div>
              </div>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6" :lg="6">
              <div class="metric-card disk-usage">
                <div class="metric-header">
                  <div class="metric-icon">
                    <el-icon><FolderOpened /></el-icon>
                  </div>
                  <div class="metric-info">
                    <div class="metric-title">磁盘使用率</div>
                    <div class="metric-value">{{ (overview.avg_disk_usage || 0).toFixed(1) }}%</div>
                  </div>
                </div>
                <div class="metric-status">
                  <el-tag 
                    :type="getDiskTagType(overview.avg_disk_usage)" 
                    size="small"
                    effect="dark"
                  >
                    {{ getDiskStatusText(overview.avg_disk_usage) }}
                  </el-tag>
                </div>
                <div class="metric-progress">
                  <el-progress 
                    :percentage="overview.avg_disk_usage || 0" 
                    :stroke-width="4"
                    :status="getDiskProgressStatus(overview.avg_disk_usage)"
                    :show-text="false"
                  />
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
  
          <!-- 筛选和操作区域 -->
    <div class="filter-section">
      <div class="filter-header">
        <div class="filter-left">
          <h3>
            <el-icon class="section-icon"><Monitor /></el-icon>
            集群节点列表
          </h3>
          <div class="filter-controls">
            <el-select 
              v-model="filters.service" 
              placeholder="服务筛选" 
              clearable 
              @change="handleFilterChange" 
              style="width: 160px; margin-right: 10px;"
            >
              <el-option label="大数据" value="大数据" />
              <el-option label="数据科学" value="bigdata-ds-new" />
              <el-option label="Hadoop" value="bigdata-hadoop-new" />
              <el-option label="Hive" value="bigdata-hive-new" />
              <el-option label="ZooKeeper" value="bigdata-zookeeper-new" />
            </el-select>
            
            <el-select 
              v-model="filters.job" 
              placeholder="任务筛选" 
              clearable 
              filterable
              allow-create
              @change="handleFilterChange" 
              style="width: 200px; margin-right: 10px;"
            >
              <el-option label="Consul节点" value="consul-node" />
              <el-option label="大数据DS调度" value="bigdata-ds-new" />
              <el-option label="大数据Hadoop" value="bigdata-hadoop-new" />
              <el-option label="大数据Hive" value="bigdata-hive-new" />
              <el-option label="大数据ZooKeeper" value="bigdata-zookeeper-new" />
              <el-option label="大数据导出器" value="bigdata-exporter-new" />
            </el-select>
            
            <el-select 
              v-model="filters.role" 
              placeholder="角色筛选" 
              clearable 
              @change="handleFilterChange" 
              style="width: 160px; margin-right: 10px;"
            >
              <el-option label="存储节点" value="bigdata-storage" />
              <el-option label="计算节点" value="bigdata-compute" />
              <el-option label="主节点" value="bigdata-master" />
            </el-select>
            
            <el-select 
              v-model="statusFilter" 
              placeholder="状态筛选" 
              clearable 
              @change="handleFilterChange" 
              style="width: 140px;"
            >
              <el-option label="全部节点" value="" />
              <el-option label="健康节点" value="healthy" />
              <el-option label="异常节点" value="unhealthy" />
            </el-select>
          </div>
        </div>
        <div class="filter-actions">
          <div class="node-summary">
            <span class="summary-item">
              总节点: <strong>{{ nodes.total || 0 }}</strong>
            </span>
            <span class="summary-item healthy">
              健康: <strong>{{ overview.healthy_nodes || 0 }}</strong>
            </span>
            <span class="summary-item error">
              异常: <strong>{{ overview.unhealthy_nodes || 0 }}</strong>
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
        <span>最后更新: {{ formatTime(overview.update_time) }}</span>
      </div>
    </div>
  
      <!-- 节点列表 -->
      <div class="nodes-table">
        <el-table 
          :data="nodes.items" 
          v-loading="loading"
          style="width: 100%"
          :row-class-name="getRowClassName"
          @row-click="handleRowClick"
        >
          <el-table-column prop="hostname" label="主机名" min-width="120">
            <template #default="{ row }">
              <div class="hostname-cell">
                <el-icon :class="getStatusIconClass(row.status)">
                  <CircleCheck v-if="row.status === 'up'" />
                  <CircleClose v-else />
                </el-icon>
                <span>{{ row.hostname }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="instance" label="IP地址" min-width="140">
            <template #default="{ row }">
              {{ getIpAddress(row.instance) }}
            </template>
          </el-table-column>
          
          <el-table-column label="服务角色" min-width="200">
            <template #default="{ row }">
              <div class="roles-cell">
                <el-tag
                  v-for="role in row.roles?.slice(0, showAllRoles[row.instance] ? undefined : 2)"
                  :key="role"
                  size="small"
                  :type="getRoleTagType(role)"
                  style="margin-right: 4px; margin-bottom: 2px;"
                >
                  {{ role }}
                </el-tag>
                <el-button
                  v-if="row.roles && row.roles.length > 2"
                  link
                  type="primary"
                  size="small"
                  @click.stop="toggleRoles(row.instance)"
                >
                  {{ showAllRoles[row.instance] ? '收起' : `+${row.roles.length - 2}` }}
                </el-button>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="cpu_usage" label="CPU使用率" width="180" sortable>
            <template #default="{ row }">
              <div class="metric-display-cell">
                <div class="metric-header-row">
                  <div class="metric-icon-wrapper">
                    <el-icon :class="getCpuIconClass(row.cpu_usage)">
                      <Cpu />
                    </el-icon>
                  </div>
                  <div class="metric-info-wrapper">
                    <div class="metric-value-row">
                      <span class="metric-percentage">{{ (row.cpu_usage || 0).toFixed(1) }}%</span>
                      <el-tag 
                        :type="getCpuTagType(row.cpu_usage)" 
                        size="small" 
                        effect="light"
                        class="metric-status-tag"
                      >
                        {{ getCpuStatusText(row.cpu_usage) }}
                      </el-tag>
                    </div>
                    <div class="metric-detail-row">
                      <span class="metric-cores">{{ row.cpu_cores || 0 }}核心</span>
                      <span class="metric-load">负载: {{ (row.load_1m || 0).toFixed(1) }}</span>
                    </div>
                  </div>
                </div>
                <div class="metric-progress-wrapper">
                  <el-progress 
                    :percentage="row.cpu_usage || 0" 
                    :stroke-width="4"
                    :status="getProgressStatus(row.cpu_usage, [70, 90])"
                    :show-text="false"
                  />
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="memory_usage" label="内存使用率" width="180" sortable>
            <template #default="{ row }">
              <div class="metric-display-cell">
                <div class="metric-header-row">
                  <div class="metric-icon-wrapper">
                    <el-icon :class="getMemoryIconClass(row.memory_usage)">
                      <TakeawayBox />
                    </el-icon>
                  </div>
                  <div class="metric-info-wrapper">
                    <div class="metric-value-row">
                      <span class="metric-percentage">{{ (row.memory_usage || 0).toFixed(1) }}%</span>
                      <el-tag 
                        :type="getMemoryTagType(row.memory_usage)" 
                        size="small" 
                        effect="light"
                        class="metric-status-tag"
                      >
                        {{ getMemoryStatusText(row.memory_usage) }}
                      </el-tag>
                    </div>
                    <div class="metric-detail-row">
                      <span class="metric-total">{{ formatMemorySize(row.memory_total) }}</span>
                      <span class="metric-used">已用: {{ formatMemorySize(getUsedMemory(row)) }}</span>
                    </div>
                  </div>
                </div>
                <div class="metric-progress-wrapper">
                  <el-progress 
                    :percentage="row.memory_usage || 0" 
                    :stroke-width="4"
                    :status="getProgressStatus(row.memory_usage, [80, 95])"
                    :show-text="false"
                  />
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="disk_usage" label="磁盘使用率" width="180" sortable>
            <template #default="{ row }">
              <div class="metric-display-cell">
                <div class="metric-header-row">
                  <div class="metric-icon-wrapper">
                    <el-icon :class="getDiskIconClass(row.disk_usage)">
                      <FolderOpened />
                    </el-icon>
                  </div>
                  <div class="metric-info-wrapper">
                    <div class="metric-value-row">
                      <span class="metric-percentage">{{ (row.disk_usage || 0).toFixed(1) }}%</span>
                      <el-tag 
                        :type="getDiskTagType(row.disk_usage)" 
                        size="small" 
                        effect="light"
                        class="metric-status-tag"
                      >
                        {{ getDiskStatusText(row.disk_usage) }}
                      </el-tag>
                    </div>
                    <div class="metric-detail-row">
                      <span class="metric-io">读: {{ formatIORate(row.disk_read_rate) }}</span>
                      <span class="metric-io">写: {{ formatIORate(row.disk_write_rate) }}</span>
                    </div>
                  </div>
                </div>
                <div class="metric-progress-wrapper">
                  <el-progress 
                    :percentage="row.disk_usage || 0" 
                    :stroke-width="4"
                    :status="getProgressStatus(row.disk_usage, [85, 95])"
                    :show-text="false"
                  />
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="load_1m" label="系统负载" width="100" sortable>
            <template #default="{ row }">
              <span :class="getLoadClass(row.load_1m)">
                {{ (row.load_1m || 0).toFixed(2) }}
              </span>
            </template>
          </el-table-column>
          
          <el-table-column prop="uptime_formatted" label="运行时间" width="120">
            <template #default="{ row }">
              {{ row.uptime_formatted || '未知' }}
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50, 100]"
            :small="false"
            :disabled="loading"
            :background="true"
            layout="total, sizes, prev, pager, next, jumper"
            :total="pagination.total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, reactive, onMounted, onUnmounted } from 'vue'
  import { ElMessage } from 'element-plus'
  import {
  Monitor,
  Cpu,
  TakeawayBox,
  FolderOpened,
  Refresh,
  CircleCheck,
  CircleClose,
  Clock,
  TrendCharts
} from '@element-plus/icons-vue'
  import { clusterService } from '@/services'
  
  // 数据状态
  const overview = ref<any>({})
  const nodes = ref<any>({ items: [], total: 0 })
  const loading = ref(false)
  const statusFilter = ref('')
  const showAllRoles = ref<Record<string, boolean>>({})
  
  // 筛选条件
  const filters = reactive({
    service: '大数据',  // 默认选择大数据
    job: '',
    role: ''
  })
  
  // 分页状态
  const pagination = reactive({
    page: 1,
    size: 20,
    total: 0
  })
  
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
    await Promise.all([
      loadOverview(),
      loadNodes()
    ])
  }
  
  // 加载概览数据
  const loadOverview = async () => {
    try {
      const params = {
        service: filters.service || undefined,
        job: filters.job || undefined,
        role: filters.role || undefined
      }
      const response = await clusterService.getClusterOverview(params)
      if (response.code === 0) {
        overview.value = response.data
      } else {
        ElMessage.error(`加载概览失败: ${response.msg}`)
      }
    } catch (error) {
      console.error('加载概览失败:', error)
      ElMessage.error('加载概览失败')
    }
  }
  
  // 加载节点数据
  const loadNodes = async () => {
    loading.value = true
    try {
      const params = {
        status: statusFilter.value || undefined,
        service: filters.service || undefined,
        job: filters.job || undefined,
        role: filters.role || undefined,
        page: pagination.page,
        size: pagination.size
      }
      const response = await clusterService.getClusterNodes(params)
      
      if (response.code === 0) {
        nodes.value = response.data
        pagination.total = response.data.total
      } else {
        ElMessage.error(`加载节点失败: ${response.msg}`)
      }
    } catch (error) {
      console.error('加载节点失败:', error)
      ElMessage.error('加载节点失败')
    } finally {
      loading.value = false
    }
  }
  
  // 处理筛选条件变化
  const handleFilterChange = () => {
    pagination.page = 1
    refreshData()
  }
  
  // 处理分页
  const handleSizeChange = (size: number) => {
    pagination.size = size
    pagination.page = 1
    loadNodes()
  }
  
  const handleCurrentChange = (page: number) => {
    pagination.page = page
    loadNodes()
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
  
  const getIpAddress = (instance: string) => {
    return instance ? instance.split(':')[0] : '未知'
  }
  
  const getRowClassName = ({ row }: { row: any }) => {
    return row.status === 'up' ? 'healthy-row' : 'unhealthy-row'
  }
  
  const getStatusIconClass = (status: string) => {
    return status === 'up' ? 'status-icon healthy' : 'status-icon unhealthy'
  }
  
  const getRoleTagType = (role: string) => {
    // 为不同的服务组件分配不同的颜色
    const roleTypes: Record<string, string> = {
      // HDFS 相关 - 蓝色系
      'HDFS NameNode': 'primary',
      'HDFS DataNode': 'info', 
      'HDFS JournalNode': 'primary',
      'Hdfs Dn': 'info',
      
      // YARN 相关 - 橙色系
      'YARN ResourceManager': 'warning',
      'YARN NodeManager': 'warning',
      'Yarn Nm': 'warning',
      'Yarnhistory': 'warning',
      
      // Spark 相关 - 红色系
      'Spark Master': 'danger',
      'Spark Worker': 'danger',
      'Spark History Server': 'danger',
      
      // Hive 相关 - 绿色系
      'HiveServer2': 'success',
      'Hive MetaStore': 'success',
      
      // DolphinScheduler 相关 - 紫色系（通过自定义样式实现）
      'DolphinScheduler Master': '',
      'DolphinScheduler API': '',
      'Ds Worker': '',
      
      // ZooKeeper 相关 - 青色系（通过自定义样式实现）
      'ZooKeeper': '',
      
      // Ranger 相关 - 深红色系
      'Ranger Admin': 'danger',
      'Ranger UserSync': 'danger',
      
      // 其他组件
      'Kerberos': 'warning',
      'LDAP Server': 'info',
      
      // 默认未知
      'Unknown': 'unknown'
    }
    
    // 返回匹配的类型或自定义类型
    if (roleTypes.hasOwnProperty(role)) {
      return roleTypes[role]
    }
    
    // 为特殊组件返回自定义类型
    if (role.includes('DolphinScheduler') || role.includes('Ds ')) {
      return 'dolphin'
    }
         if (role.includes('ZooKeeper') || role.includes('Zk')) {
       return 'zookeeper'
     }
     if (role === 'Unknown') {
       return 'unknown'
     }
    
    return 'info'
  }
  
  const getProgressStatus = (value: number, thresholds: [number, number]) => {
    if (value >= thresholds[1]) return 'exception'
    if (value >= thresholds[0]) return 'warning'
    return 'success'
  }
  
  const getLoadClass = (load: number) => {
    if (load >= 2) return 'load-high'
    if (load >= 1) return 'load-medium'
    return 'load-normal'
  }
  

  
  // 节点健康相关函数
const getNodeHealthPercentage = () => {
  const total = overview.value.total_nodes || 0
  const healthy = overview.value.healthy_nodes || 0
  return total > 0 ? Math.round((healthy / total) * 100) : 0
}

const getNodeHealthStatus = () => {
  const percentage = getNodeHealthPercentage()
  if (percentage >= 90) return 'success'
  if (percentage >= 70) return 'warning'
  return 'exception'
}

// CPU相关函数
const getCpuStatusClass = (usage: number) => {
  if (usage >= 90) return 'status-critical'
  if (usage >= 70) return 'status-warning'
  return 'status-normal'
}

const getCpuStatusText = (usage: number) => {
  if (usage >= 90) return '严重'
  if (usage >= 70) return '警告'
  return '正常'
}

const getCpuTagType = (usage: number) => {
  if (usage >= 90) return 'danger'
  if (usage >= 70) return 'warning'
  return 'success'
}

const getCpuProgressStatus = (usage: number) => {
  if (usage >= 90) return 'exception'
  if (usage >= 70) return 'warning'
  return 'success'
}

const getCpuIconClass = (usage: number) => {
  if (usage >= 90) return 'metric-icon critical'
  if (usage >= 70) return 'metric-icon warning'
  return 'metric-icon normal'
}

// 内存相关函数
const getMemoryStatusClass = (usage: number) => {
  if (usage >= 95) return 'status-critical'
  if (usage >= 80) return 'status-warning'
  return 'status-normal'
}

const getMemoryStatusText = (usage: number) => {
  if (usage >= 95) return '严重'
  if (usage >= 80) return '警告'
  return '正常'
}

const getMemoryTagType = (usage: number) => {
  if (usage >= 95) return 'danger'
  if (usage >= 80) return 'warning'
  return 'success'
}

const getMemoryProgressStatus = (usage: number) => {
  if (usage >= 95) return 'exception'
  if (usage >= 80) return 'warning'
  return 'success'
}

const getMemoryIconClass = (usage: number) => {
  if (usage >= 95) return 'metric-icon critical'
  if (usage >= 80) return 'metric-icon warning'
  return 'metric-icon normal'
}

const formatMemorySize = (bytes: number) => {
  if (!bytes) return '0 B'
  const gb = bytes / (1024 * 1024 * 1024)
  if (gb >= 1) {
    return `${gb.toFixed(1)} GB`
  }
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(0)} MB`
}

const getUsedMemory = (row: any) => {
  const total = row.memory_total || 0
  const usage = row.memory_usage || 0
  return total * (usage / 100)
}
  
  // 磁盘相关函数
const getDiskStatusClass = (usage: number) => {
  if (usage >= 95) return 'status-critical'
  if (usage >= 85) return 'status-warning'
  return 'status-normal'
}

const getDiskStatusText = (usage: number) => {
  if (usage >= 95) return '严重'
  if (usage >= 85) return '警告'
  return '正常'
}

const getDiskTagType = (usage: number) => {
  if (usage >= 95) return 'danger'
  if (usage >= 85) return 'warning'
  return 'success'
}

const getDiskProgressStatus = (usage: number) => {
  if (usage >= 95) return 'exception'
  if (usage >= 85) return 'warning'
  return 'success'
}

const getDiskIconClass = (usage: number) => {
  if (usage >= 95) return 'metric-icon critical'
  if (usage >= 85) return 'metric-icon warning'
  return 'metric-icon normal'
}

const formatIORate = (rate: number) => {
  if (!rate) return '0'
  if (rate >= 1024 * 1024 * 1024) {
    return `${(rate / (1024 * 1024 * 1024)).toFixed(1)}GB/s`
  }
  if (rate >= 1024 * 1024) {
    return `${(rate / (1024 * 1024)).toFixed(1)}MB/s`
  }
  if (rate >= 1024) {
    return `${(rate / 1024).toFixed(1)}KB/s`
  }
  return `${rate.toFixed(0)}B/s`
}
  
  const toggleRoles = (instance: string) => {
    showAllRoles.value[instance] = !showAllRoles.value[instance]
  }
  
  const handleRowClick = (row: any) => {
    console.log('点击节点:', row)
    // 可以在这里添加节点详情弹窗或跳转逻辑
  }
  </script>
  
  <style scoped>
  .cluster-overview {
    padding: 20px;
    background: #f5f5f5;
    min-height: calc(100vh - 60px);
  }
  
  /* 集群概览面板样式 */
.cluster-overview-panel {
  margin-bottom: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #409eff;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.panel-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-icon {
  color: #409eff;
}

.metrics-grid {
  padding: 20px;
}

.metric-card {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  transition: all 0.3s ease;
  border: 1px solid #ebeef5;
  height: 140px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.metric-card.cluster-nodes {
  border-left: 4px solid #909399;
}

.metric-card.cpu-usage {
  border-left: 4px solid #f56c6c;
}

.metric-card.memory-usage {
  border-left: 4px solid #409eff;
}

.metric-card.disk-usage {
  border-left: 4px solid #67c23a;
}

.metric-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.metric-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 18px;
  color: white;
}

.cluster-nodes .metric-icon {
  background: linear-gradient(135deg, #909399 0%, #606266 100%);
}

.cpu-usage .metric-icon {
  background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
}

.memory-usage .metric-icon {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}

.disk-usage .metric-icon {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.metric-info {
  flex: 1;
}

.metric-title {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
  font-weight: 500;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  line-height: 1;
}

.metric-details {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.detail-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 2px;
}

.detail-value {
  font-size: 16px;
  font-weight: bold;
}

.detail-item.healthy .detail-value {
  color: #67c23a;
}

.detail-item.error .detail-value {
  color: #f56c6c;
}

.metric-status {
  margin-bottom: 8px;
  text-align: center;
}

.metric-progress {
  margin-top: auto;
}
  
  /* 状态样式 */
  .status-normal { color: #67c23a; }
  .status-warning { color: #e6a23c; }
  .status-critical { color: #f56c6c; }
  
  /* 筛选区域样式 */
.filter-section {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #67c23a;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.filter-left h3 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-icon {
  color: #67c23a;
}

.filter-controls {
  margin-top: 8px;
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.node-summary {
  display: flex;
  gap: 24px;
  margin-right: 8px;
}

.summary-item {
  font-size: 14px;
  color: #666;
}

.summary-item strong {
  font-size: 16px;
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
  
  /* 表格样式 */
  .nodes-table {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .hostname-cell {
    display: flex;
    align-items: center;
  }
  
  .status-icon {
    margin-right: 8px;
    font-size: 16px;
  }
  
  .status-icon.healthy {
    color: #67c23a;
  }
  
  .status-icon.unhealthy {
    color: #f56c6c;
  }
  
  .roles-cell {
    max-width: 200px;
  }
  
  .progress-cell {
    display: flex;
    align-items: center;
    flex-direction: column;
    padding: 8px 4px;
  }
  
  .progress-text {
    font-size: 12px;
    color: #666;
    margin-top: 6px;
    font-weight: 600;
  }
  
  /* 自定义服务角色标签样式 */
  :deep(.el-tag.el-tag--dolphin) {
    background-color: #f3e8ff;
    border-color: #8b5cf6;
    color: #7c3aed;
  }
  
  :deep(.el-tag.el-tag--zookeeper) {
    background-color: #ecfeff;
    border-color: #06b6d4;
    color: #0891b2;
  }
  
  :deep(.el-tag.el-tag--unknown) {
    background-color: #f5f5f5;
    border-color: #d1d5db;
    color: #6b7280;
  }
  
  /* 增强进度条样式 */
  :deep(.el-progress-bar__outer) {
    background-color: #f0f2f5;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  :deep(.el-progress-bar__inner) {
    border-radius: 8px;
    transition: all 0.3s ease;
    background: linear-gradient(90deg, #67c23a, #85ce61);
  }
  
  :deep(.el-progress--warning .el-progress-bar__inner) {
    background: linear-gradient(90deg, #e6a23c, #f0c782);
  }
  
  :deep(.el-progress--exception .el-progress-bar__inner) {
    background: linear-gradient(90deg, #f56c6c, #f78989);
    box-shadow: 0 0 8px rgba(245, 108, 108, 0.3);
  }
  
  /* 角色标签容器优化 */
  .roles-cell {
    max-width: 200px;
    line-height: 1.4;
  }
  
  .roles-cell .el-tag {
    margin: 2px 3px 2px 0;
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 500;
  }
  
  /* 增强的指标显示单元格样式 */
  .metric-display-cell {
    padding: 8px 6px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    min-width: 160px;
  }
  
  .metric-header-row {
    display: flex;
    align-items: flex-start;
    gap: 8px;
  }
  
  .metric-icon-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    flex-shrink: 0;
  }
  
  .metric-icon {
    font-size: 16px;
    transition: all 0.3s ease;
  }
  
  .metric-icon.normal {
    color: #67c23a;
    background-color: #f0f9ff;
  }
  
  .metric-icon.warning {
    color: #e6a23c;
    background-color: #fef7e0;
  }
  
  .metric-icon.critical {
    color: #f56c6c;
    background-color: #fef0f0;
    animation: pulse 2s infinite;
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }
  
  .metric-info-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  
  .metric-value-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
  }
  
  .metric-percentage {
    font-size: 14px;
    font-weight: 600;
    color: #333;
  }
  
  .metric-status-tag {
    font-size: 10px;
    height: 18px;
    padding: 0 4px;
    border-radius: 2px;
  }
  
  .metric-detail-row {
    display: flex;
    flex-direction: column;
    gap: 1px;
    margin-top: 2px;
  }
  
  .metric-cores,
  .metric-load,
  .metric-total,
  .metric-used,
  .metric-io {
    font-size: 10px;
    color: #666;
    line-height: 1.2;
  }
  
  .metric-progress-wrapper {
    margin-top: 4px;
  }
  
  .metric-progress-wrapper :deep(.el-progress-bar__outer) {
    height: 3px;
    background-color: #f0f2f5;
    border-radius: 2px;
  }
  
  .metric-progress-wrapper :deep(.el-progress-bar__inner) {
    border-radius: 2px;
  }
  
  .load-normal { color: #67c23a; }
  .load-medium { color: #e6a23c; }
  .load-high { color: #f56c6c; }
  
  /* 行样式 */
  :deep(.healthy-row) {
    background-color: #f0f9ff;
  }
  
  :deep(.unhealthy-row) {
    background-color: #fef0f0;
  }
  
  /* 分页样式 */
  .pagination-wrapper {
    padding: 20px;
    text-align: center;
    background: white;
    border-top: 1px solid #ebeef5;
  }
  
  /* 响应式样式 */
  @media (max-width: 768px) {
    .cluster-overview {
      padding: 10px;
    }
    
    .overview-card {
      margin-bottom: 12px;
    }
    
    .card-icon {
      width: 40px;
      height: 40px;
      font-size: 18px;
    }
    
    .card-value {
      font-size: 20px;
    }
  }
  </style>