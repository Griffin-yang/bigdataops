<template>
  <div class="alert-history-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="title-section">
        <h2>
          <el-icon><Clock /></el-icon>
          告警历史
        </h2>
        <p class="subtitle">查看和管理系统告警历史记录</p>
      </div>
      <div class="actions">
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards" v-if="stats">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number total">{{ stats.total_alerts }}</div>
              <div class="stat-label">总告警数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number firing">{{ stats.firing_alerts }}</div>
              <div class="stat-label">告警中</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number resolved">{{ stats.resolved_alerts }}</div>
              <div class="stat-label">已解决</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number rate">{{ alertResolveRate }}%</div>
              <div class="stat-label">解决率</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 筛选面板 -->
    <el-card class="filter-panel">
      <el-form :model="filters" label-width="80px" :inline="true">
        <el-form-item label="组件分组">
          <el-select v-model="filters.category" placeholder="选择组件" clearable style="width: 140px">
            <el-option 
              v-for="item in CATEGORY_OPTIONS" 
              :key="item.value" 
              :label="item.label" 
              :value="item.value" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="告警等级">
          <el-select v-model="filters.level" placeholder="选择等级" clearable style="width: 120px">
            <el-option 
              v-for="item in LEVEL_OPTIONS" 
              :key="item.value" 
              :label="item.label" 
              :value="item.value" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="告警状态">
          <el-select v-model="filters.status" placeholder="选择状态" clearable style="width: 120px">
            <el-option 
              v-for="item in STATUS_OPTIONS" 
              :key="item.value" 
              :label="item.label" 
              :value="item.value" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="规则名称">
          <el-input v-model="filters.rule_name" placeholder="搜索规则名称" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ssZ"
            @change="handleDateChange"
            style="width: 350px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetFilters">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 告警历史表格 -->
    <el-card class="table-card">
      <el-table 
        :data="historyList" 
        v-loading="loading" 
        style="width: 100%"
        row-key="id"
        :default-sort="{ prop: 'fired_at', order: 'descending' }"
      >
        <el-table-column prop="rule_name" label="规则名称" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="category" label="组件分组" width="120" align="center">
          <template #default="scope">
            <el-tag :type="getCategoryType(scope.row.category)" size="small">
              {{ getCategoryLabel(scope.row.category) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="level" label="告警等级" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getLevelType(scope.row.level)" size="small">
              {{ getLevelLabel(scope.row.level) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="alert_value" label="告警值" width="100" align="center">
          <template #default="scope">
            <span class="alert-value">{{ scope.row.alert_value }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="condition" label="触发条件" width="120" align="center" show-overflow-tooltip />

        <el-table-column prop="fired_at" label="触发时间" width="180" align="center">
          <template #default="scope">
            <div class="time-info">
              <div>{{ formatDateTime(scope.row.fired_at) }}</div>
              <div class="time-ago">{{ getTimeAgo(scope.row.fired_at) }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="resolved_at" label="解决时间" width="180" align="center">
          <template #default="scope">
            <div v-if="scope.row.resolved_at" class="time-info">
              <div>{{ formatDateTime(scope.row.resolved_at) }}</div>
              <div class="time-ago">{{ getTimeAgo(scope.row.resolved_at) }}</div>
            </div>
            <span v-else class="not-resolved">未解决</span>
          </template>
        </el-table-column>

        <el-table-column label="持续时间" width="120" align="center">
          <template #default="scope">
            <span class="duration">{{ getDuration(scope.row.fired_at, scope.row.resolved_at) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="240" align="center" fixed="right">
          <template #default="scope">
            <div class="operation-buttons">
              <el-button type="primary" size="small" @click="viewDetails(scope.row)">
                <el-icon><View /></el-icon>
                详情
              </el-button>
              <el-button 
                v-if="scope.row.status === 'triggered' && !scope.row.acknowledged" 
                type="warning" 
                size="small" 
                @click="acknowledgeAlert(scope.row)"
              >
                <el-icon><Warning /></el-icon>
                确认
              </el-button>
              <el-button 
                v-if="scope.row.status === 'triggered'" 
                type="success" 
                size="small" 
                @click="resolveAlert(scope.row)"
              >
                <el-icon><Check /></el-icon>
                解决
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailDialog.visible" title="告警详情" width="800px">
      <div v-if="detailDialog.data" class="alert-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="规则名称">{{ detailDialog.data.rule_name }}</el-descriptions-item>
          <el-descriptions-item label="组件分组">
            <el-tag :type="getCategoryType(detailDialog.data.category)" size="small">
              {{ getCategoryLabel(detailDialog.data.category) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="告警等级">
            <el-tag :type="getLevelType(detailDialog.data.level)" size="small">
              {{ getLevelLabel(detailDialog.data.level) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="告警状态">
            <el-tag :type="getStatusType(detailDialog.data.status)" size="small">
              {{ getStatusLabel(detailDialog.data.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="告警值">{{ detailDialog.data.alert_value }}</el-descriptions-item>
          <el-descriptions-item label="触发条件">{{ detailDialog.data.condition }}</el-descriptions-item>
          <el-descriptions-item label="触发时间">{{ formatDateTime(detailDialog.data.fired_at) }}</el-descriptions-item>
          <el-descriptions-item label="解决时间">
            {{ detailDialog.data.resolved_at ? formatDateTime(detailDialog.data.resolved_at) : '未解决' }}
          </el-descriptions-item>
          <el-descriptions-item label="持续时间" span="2">
            {{ getDuration(detailDialog.data.fired_at, detailDialog.data.resolved_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="标签信息" span="2">
            <div class="labels-display">
              <template v-if="detailDialog.data.labels">
                <el-tag v-for="label in parseLabels(detailDialog.data.labels)" :key="label" size="small" class="label-tag">
                  {{ label }}
                </el-tag>
              </template>
              <span v-else class="no-labels">无标签</span>
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialog.visible = false">关闭</el-button>
        <el-button 
          v-if="detailDialog.data && detailDialog.data.status === 'triggered'" 
          type="success" 
          @click="resolveAlert(detailDialog.data)"
        >
          标记为已解决
        </el-button>
      </template>
    </el-dialog>

    <!-- 解决告警对话框 -->
    <el-dialog v-model="resolveDialog.visible" title="解决告警" width="500px">
      <el-form :model="resolveDialog.form" label-width="80px">
        <el-form-item label="解决原因">
          <el-input 
            v-model="resolveDialog.form.reason" 
            type="textarea" 
            :rows="4" 
            placeholder="请输入解决原因（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveDialog.visible = false">取消</el-button>
        <el-button type="success" @click="confirmResolve" :loading="resolveDialog.loading">
          确认解决
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Clock,
  Refresh,
  Search,
  RefreshLeft,
  View,
  Check,
  Warning
} from '@element-plus/icons-vue'
import { alertHistoryService } from '@/services'
import {
  CATEGORY_OPTIONS,
  LEVEL_OPTIONS,
  getCategoryLabel,
  getCategoryType,
  getLevelLabel,
  getLevelType
} from '@/constants'

// 告警状态选项
const STATUS_OPTIONS = [
  { value: 'triggered', label: '告警中' },
  { value: 'recovered', label: '已解决' }
]

// 状态处理函数
const getStatusLabel = (status: string) => {
  const option = STATUS_OPTIONS.find(item => item.value === status)
  return option ? option.label : status
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'triggered': return 'danger'
    case 'recovered': return 'success'
    default: return 'info'
  }
}

// 响应式数据
const loading = ref(false)
const historyList = ref<any[]>([])
const stats = ref<any>(null)

// 筛选条件
const filters = reactive({
  category: '',
  level: '',
  status: '',
  rule_name: '',
  start_time: '',
  end_time: ''
})

const dateRange = ref([])

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 详情对话框
const detailDialog = reactive({
  visible: false,
  data: null as any
})

// 解决告警对话框
const resolveDialog = reactive({
  visible: false,
  loading: false,
  currentAlert: null as any,
  form: {
    reason: ''
  }
})

// 计算属性
const alertResolveRate = computed(() => {
  if (!stats.value || stats.value.total_alerts === 0) return 0
  return Math.round((stats.value.resolved_alerts / stats.value.total_alerts) * 100)
})

// 方法
const loadHistoryData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...filters
    }
    
    // 移除空值
    Object.keys(params).forEach(key => {
      if ((params as any)[key] === '' || (params as any)[key] === null || (params as any)[key] === undefined) {
        delete (params as any)[key]
      }
    })

    const response = await alertHistoryService.getHistoryList(params)
    if (response.code === 0) {
      historyList.value = response.data.items
      pagination.total = response.data.total
    } else {
      ElMessage.error(response.msg || '获取告警历史失败')
    }
  } catch (error) {
    console.error('获取告警历史失败:', error)
    ElMessage.error('获取告警历史失败')
  } finally {
    loading.value = false
  }
}

const loadStatsData = async () => {
  try {
    const params: any = { days: 7 }
    if (filters.category) {
      params.category = filters.category
    }
    
    const response = await alertHistoryService.getHistoryStats(params)
    if (response.code === 0) {
      stats.value = response.data
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const refreshData = async () => {
  await Promise.all([loadHistoryData(), loadStatsData()])
}

const handleDateChange = (value: any) => {
  if (value && value.length === 2) {
    filters.start_time = value[0]
    filters.end_time = value[1]
  } else {
    filters.start_time = ''
    filters.end_time = ''
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadHistoryData()
}

const resetFilters = () => {
  Object.assign(filters, {
    category: '',
    level: '',
    status: '',
    rule_name: '',
    start_time: '',
    end_time: ''
  })
  dateRange.value = []
  pagination.page = 1
  loadHistoryData()
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  loadHistoryData()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadHistoryData()
}

const viewDetails = (row: any) => {
  detailDialog.data = row
  detailDialog.visible = true
}

const acknowledgeAlert = async (row: any) => {
  try {
    const acknowledgedBy = 'current_user' // 这里应该从用户上下文获取
    const response = await alertHistoryService.acknowledgeAlert(row.id, acknowledgedBy)
    
    if (response.code === 0) {
      ElMessage.success('告警已确认，停止发送通知')
      await refreshData()
    } else {
      ElMessage.error(response.msg || '确认失败')
    }
  } catch (error) {
    console.error('确认告警失败:', error)
    ElMessage.error('确认失败')
  }
}

const resolveAlert = (row: any) => {
  resolveDialog.currentAlert = row
  resolveDialog.form.reason = ''
  resolveDialog.visible = true
}

const confirmResolve = async () => {
  if (!resolveDialog.currentAlert) return
  
  resolveDialog.loading = true
  try {
    const response = await alertHistoryService.resolveAlert(
      resolveDialog.currentAlert.id,
      resolveDialog.form.reason
    )
    
    if (response.code === 0) {
      ElMessage.success('告警已标记为解决')
      resolveDialog.visible = false
      detailDialog.visible = false
      await refreshData()
    } else {
      ElMessage.error(response.msg || '操作失败')
    }
  } catch (error) {
    console.error('解决告警失败:', error)
    ElMessage.error('操作失败')
  } finally {
    resolveDialog.loading = false
  }
}

// 工具函数
const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getTimeAgo = (dateStr: string) => {
  if (!dateStr) return ''
  const now = new Date()
  const date = new Date(dateStr)
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))
  
  if (diffMins < 60) return `${diffMins}分钟前`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}小时前`
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}天前`
}

const getDuration = (startTime: string, endTime: string | null) => {
  if (!startTime) return '-'
  
  const start = new Date(startTime)
  const end = endTime ? new Date(endTime) : new Date()
  const diffMs = end.getTime() - start.getTime()
  
  if (diffMs < 1000 * 60) return `${Math.floor(diffMs / 1000)}秒`
  if (diffMs < 1000 * 60 * 60) return `${Math.floor(diffMs / (1000 * 60))}分钟`
  if (diffMs < 1000 * 60 * 60 * 24) return `${Math.floor(diffMs / (1000 * 60 * 60))}小时`
  return `${Math.floor(diffMs / (1000 * 60 * 60 * 24))}天`
}

const parseLabels = (labels: any) => {
  if (!labels) return []
  
  // 如果是字符串，按逗号分割
  if (typeof labels === 'string') {
    return labels.split(',').map(label => label.trim()).filter(label => label)
  }
  
  // 如果是JSON对象，转换为键值对字符串
  if (typeof labels === 'object') {
    return Object.entries(labels).map(([key, value]) => `${key}=${value}`)
  }
  
  return []
}

// 初始化
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.alert-history-container {
  padding: 24px;
  background: #faf9f7 !important;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.stats-cards {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 20px;
  border: none;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  overflow: hidden;
  position: relative;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

.stat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.2);
}

.stat-content {
  text-align: center;
  padding: 20px;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-number.total { color: #667eea; }
.stat-number.firing { color: #f56c6c; }
.stat-number.resolved { color: #67c23a; }
.stat-number.rate { color: #e6a23c; }

.stat-label {
  color: #718096;
  font-size: 14px;
  font-weight: 500;
}

.filter-panel {
  margin-bottom: 24px;
  border-radius: 20px;
  border: none;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.filter-panel:hover {
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.15);
}

.filter-panel :deep(.el-card__body) {
  padding: 20px 24px;
}

.table-card {
  border-radius: 20px;
  border: none;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.table-card:hover {
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.15);
}

.time-info {
  text-align: center;
}

.time-ago {
  font-size: 12px;
  color: #a0aec0;
  margin-top: 2px;
}

.not-resolved {
  color: #f56c6c;
  font-style: italic;
}

.duration {
  font-weight: 600;
  color: #667eea;
}

.alert-value {
  font-weight: 600;
  color: #e6a23c;
}

.operation-buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
}

.operation-buttons .el-button {
  font-size: 12px;
  padding: 4px 8px;
  min-width: auto;
  height: 28px;
  border-radius: 6px;
  white-space: nowrap;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.3);
}

.alert-detail {
  padding: 16px 0;
}

.labels-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.label-tag {
  margin: 0;
  border-radius: 8px;
  font-weight: 500;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.no-labels {
  color: #a0aec0;
  font-style: italic;
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

:deep(.el-button) {
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
}

:deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

:deep(.el-tag) {
  border-radius: 8px;
  font-weight: 500;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-dialog) {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  color: #2d3748;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 16px 16px 0 0;
}
</style> 