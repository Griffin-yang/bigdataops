<template>
  <div class="dashboard">
    <!-- 顶部操作栏 -->
    <div class="dashboard-header">
      <h2 class="dashboard-title">数据概览</h2>
      <el-button type="primary" @click="refreshAll" class="refresh-btn">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>
    
    <!-- 数据统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon users">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.userCount }}</div>
              <div class="stat-label">LDAP用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon rules">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.ruleCount }}</div>
              <div class="stat-label">告警规则</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon alerts">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.alertCount }}</div>
              <div class="stat-label">今日告警</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon servers">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ stats.serverCount }}</div>
              <div class="stat-label">服务器节点</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>告警趋势</span>
          </template>
          <v-chart 
            class="chart" 
            :option="alertTrendOption" 
            autoresize
          />
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>集群资源使用率</span>
          </template>
          <v-chart 
            class="chart" 
            :option="resourceOption" 
            autoresize
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作和最新告警 -->
    <el-row :gutter="20" class="content-row">
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>
          <div class="quick-actions">
            <el-button 
              type="primary" 
              icon="Plus" 
              @click="$router.push('/alert-rules')"
              class="action-btn"
            >
              新增告警规则
            </el-button>
            <el-button 
              type="success" 
              icon="Message" 
              @click="$router.push('/alert-templates')"
              class="action-btn"
            >
              配置告警模板
            </el-button>
            <el-button 
              type="info" 
              icon="UserFilled" 
              @click="$router.push('/users')"
              class="action-btn"
            >
              添加LDAP用户
            </el-button>
            <el-button 
              type="warning" 
              icon="View" 
              @click="$router.push('/monitoring')"
              class="action-btn"
            >
              查看集群监控
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>最新告警记录</span>
            <el-button 
              type="text" 
              size="small" 
              style="float: right"
              @click="refreshAlerts"
            >
              刷新
            </el-button>
          </template>
          <el-table :data="recentAlerts" style="width: 100%">
            <el-table-column prop="rule_name" label="规则名称" width="200" />
            <el-table-column prop="level" label="等级" width="100">
              <template #default="scope">
                <el-tag 
                  :type="getLevelType(scope.row.level)"
                  size="small"
                >
                  {{ scope.row.level }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="告警内容" show-overflow-tooltip />
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="scope">
                {{ formatTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="notified" label="状态" width="100">
              <template #default="scope">
                <el-tag 
                  :type="scope.row.notified ? 'success' : 'danger'" 
                  size="small"
                >
                  {{ scope.row.notified ? '已通知' : '未通知' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { User, Warning, Bell, Monitor, Refresh } from '@element-plus/icons-vue'
import { alertAPI } from '@/utils/api'
import { UserService } from '@/services'

// 统计数据
const stats = ref({
  userCount: 0,
  ruleCount: 0,
  alertCount: 0,
  serverCount: 0
})

// 最新告警
const recentAlerts = ref<any[]>([])

// 告警趋势图表配置
const alertTrendOption = ref({
  title: {
    text: '近7天告警趋势'
  },
  tooltip: {
    trigger: 'axis'
  },
  xAxis: {
    type: 'category',
    data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  },
  yAxis: {
    type: 'value'
  },
  series: [{
    data: [12, 8, 15, 22, 9, 6, 11],
    type: 'line',
    smooth: true,
    itemStyle: {
      color: '#409EFF'
    }
  }]
})

// 资源使用率图表配置
const resourceOption = ref({
  title: {
    text: '集群资源使用率'
  },
  tooltip: {
    trigger: 'item'
  },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: [
      { value: 35, name: 'CPU使用', itemStyle: { color: '#409EFF' } },
      { value: 65, name: 'CPU空闲', itemStyle: { color: '#E4E7ED' } }
    ],
    label: {
      show: true,
      formatter: '{b}: {c}%'
    }
  }]
})

// 获取等级类型
const getLevelType = (level: string) => {
  const types: Record<string, string> = {
    'critical': 'danger',
    'warning': 'warning',
    'info': 'info'
  }
  return types[level] || 'info'
}

// 格式化时间
const formatTime = (time: string) => {
  return new Date(time).toLocaleString()
}

// 加载LDAP用户数据
const loadLdapUsers = async () => {
  try {
    console.log('开始获取LDAP用户数量...')
    const users = await UserService.getUsers('prod')
    console.log('获取到的LDAP用户:', users)
    stats.value.userCount = users.length
    console.log('设置用户数量为:', users.length)
  } catch (error) {
    console.error('获取LDAP用户数量失败:', error)
    stats.value.userCount = 0
  }
}

// 加载告警规则数据
const loadAlertRules = async () => {
  try {
    const rulesRes = await alertAPI.getRules()
    console.log('告警规则响应:', rulesRes)
    // 根据实际API响应格式处理
    if (Array.isArray(rulesRes)) {
      stats.value.ruleCount = rulesRes.length
    } else if (rulesRes && typeof rulesRes === 'object') {
      // 如果是包装对象，尝试获取数据
      const rules = (rulesRes as any).data || (rulesRes as any).items || rulesRes
      stats.value.ruleCount = Array.isArray(rules) ? rules.length : 0
    } else {
      stats.value.ruleCount = 0
    }
  } catch (error) {
    console.error('获取告警规则失败:', error)
    stats.value.ruleCount = 0
  }
}

// 加载告警历史数据
const loadAlertHistory = async () => {
  try {
    const historyRes = await alertAPI.getHistory()
    console.log('告警历史响应:', historyRes)
    // 根据实际API响应格式处理
    if (Array.isArray(historyRes)) {
      recentAlerts.value = historyRes.slice(0, 10)
      stats.value.alertCount = historyRes.length
    } else if (historyRes && typeof historyRes === 'object') {
      // 如果是包装对象，尝试获取数据
      const history = (historyRes as any).data || (historyRes as any).items || historyRes
      if (Array.isArray(history)) {
        recentAlerts.value = history.slice(0, 10)
        stats.value.alertCount = history.length
      } else {
        recentAlerts.value = []
        stats.value.alertCount = 0
      }
    } else {
      recentAlerts.value = []
      stats.value.alertCount = 0
    }
  } catch (error) {
    console.error('获取告警历史失败:', error)
    recentAlerts.value = []
    stats.value.alertCount = 0
  }
}

// 加载数据
const loadData = async () => {
  console.log('开始加载Dashboard数据...')
  
  // 并行加载数据，但不阻塞页面渲染
  Promise.all([
    loadLdapUsers(),
    loadAlertRules(),
    loadAlertHistory()
  ]).then(() => {
    console.log('Dashboard数据加载完成:', stats.value)
  }).catch(error => {
    console.warn('Dashboard数据加载部分失败:', error)
  })

  // 模拟服务器节点数据
  stats.value.serverCount = 8
}

// 刷新告警
const refreshAlerts = () => {
  loadAlertHistory()
}

// 刷新所有数据
const refreshAll = () => {
  loadData()
}

onMounted(() => {
  // 确保页面先渲染，然后再加载数据
  nextTick(() => {
    loadData()
  })
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
  width: 100%;
  min-height: calc(100vh - 120px);
  background: #faf9f7 !important;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.dashboard-title {
  margin: 0;
  color: #2d3748;
  font-size: 24px;
  font-weight: 600;
}

.refresh-btn {
  height: 40px;
  padding: 0 20px;
  border-radius: 8px;
  font-weight: 500;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: #ffffff;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.stat-card :deep(.el-card__body) {
  padding: 24px;
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 10px 0;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 24px;
  color: white;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.stat-icon.users {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.rules {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.alerts {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.servers {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #2d3748;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #718096;
  margin-top: 5px;
  font-weight: 500;
}

.charts-row {
  margin-bottom: 24px;
}

.charts-row :deep(.el-card) {
  border: none;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.charts-row :deep(.el-card__header) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  font-weight: 600;
  color: #2d3748;
}

.chart {
  height: 300px;
  width: 100%;
}

.content-row {
  margin-bottom: 24px;
}

.content-row :deep(.el-card) {
  border: none;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.content-row :deep(.el-card__header) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  font-weight: 600;
  color: #2d3748;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.action-btn {
  width: 100%;
  height: 45px;
  justify-content: flex-start;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  color: #667eea;
  font-weight: 600;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.action-btn:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.content-row :deep(.el-table) {
  border: none;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.content-row :deep(.el-table th) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  color: #2d3748;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.content-row :deep(.el-table td) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.6);
}

.content-row :deep(.el-table__row:hover td) {
  background: rgba(102, 126, 234, 0.1) !important;
}

.content-row :deep(.el-tag) {
  border-radius: 8px;
  font-weight: 500;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
  }
  
  .stats-row {
    margin: 0 -10px 20px -10px;
  }
  
  .charts-row {
    margin: 0 -10px 20px -10px;
  }
  
  .content-row {
    margin: 0 -10px 20px -10px;
  }
}

@media (min-width: 1200px) {
  .dashboard {
    max-width: none;
    width: 100%;
  }
}
</style> 