<template>
  <div class="alert-rules">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h2 class="page-title">告警规则管理</h2>
          <span class="rule-count">共 {{ filteredRules.length }} 个规则</span>
        </div>
        <el-button type="primary" @click="showCreateDialog" class="create-btn">
          <el-icon><Plus /></el-icon>
          新增规则
        </el-button>
      </div>
    </div>

    <div class="content-container">
      <!-- 组件分组Tab -->
      <div class="category-tabs">
        <el-tabs v-model="activeCategory" @tab-change="handleCategoryChange" class="component-tabs">
          <el-tab-pane label="全部" name="all">
            <template #label>
              <span class="tab-label">
                <el-icon><Grid /></el-icon>
                全部 ({{ getTotalCountByCategory('all') }})
              </span>
            </template>
          </el-tab-pane>
          <el-tab-pane 
            v-for="category in categoryOptions" 
            :key="category.value" 
            :label="category.label" 
            :name="category.value"
          >
            <template #label>
              <span class="tab-label">
                <el-icon><component :is="getCategoryIcon(category.value)" /></el-icon>
                {{ category.label }} ({{ getTotalCountByCategory(category.value) }})
              </span>
            </template>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 搜索和状态栏 -->
      <div class="filter-section">
        <div class="search-bar">
          <el-input
            v-model="searchText"
            placeholder="搜索规则名称..."
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon class="search-icon"><Search /></el-icon>
            </template>
          </el-input>
          <el-button @click="loadRules" class="search-btn">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </div>

        <!-- 告警引擎状态 -->
        <div class="engine-status-card">
          <div class="status-header">
            <el-icon class="status-icon"><Setting /></el-icon>
            <span class="status-title">告警引擎状态</span>
          </div>
          <div class="status-content">
            <el-tag 
              :type="engineStatus === '运行中' ? 'success' : 'danger'" 
              size="large" 
              class="status-tag"
            >
              {{ engineStatus }}
            </el-tag>
            <div class="engine-actions">
              <el-button
                v-if="engineStatus !== '运行中'"
                type="success"
                size="small"
                @click="startEngine"
                class="engine-btn"
              >
                启动引擎
              </el-button>
              <el-button
                v-else
                type="danger"
                size="small"
                @click="stopEngine"
                class="engine-btn"
              >
                停止引擎
              </el-button>
              <el-button
                type="primary"
                size="small"
                @click="testEngine"
                class="engine-btn"
              >
                测试执行
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 规则列表 -->
      <div class="table-container">
        <el-table 
          :data="filteredRules" 
          v-loading="loading" 
          class="rules-table"
          stripe
          size="large"
          :header-cell-style="{ backgroundColor: '#f8fafc', color: '#374151', fontWeight: '600' }"
        >
          <el-table-column prop="name" label="规则名称" min-width="180" show-overflow-tooltip />
          <el-table-column prop="category" label="所属分组" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="getCategoryType(row.category)" size="small">
                {{ getCategoryLabel(row.category) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="promql" label="PromQL表达式" min-width="200" show-overflow-tooltip />
          <el-table-column prop="condition" label="告警条件" width="120" align="center" show-overflow-tooltip />
          <el-table-column prop="level" label="告警等级" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getSeverityType(row.level)" size="small">
                {{ getSeverityText(row.level) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="enabled" label="状态" width="80" align="center">
            <template #default="{ row }">
              <el-switch
                v-model="row.enabled"
                @change="toggleRule(row)"
                :loading="switchingRules.has(row.id)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="suppress" label="抑制条件" width="100" align="center" show-overflow-tooltip />
          <el-table-column prop="repeat" label="再通知间隔" width="110" align="center">
            <template #default="{ row }">
              {{ row.repeat ? `${row.repeat}秒` : '无' }}
            </template>
          </el-table-column>
          <el-table-column prop="notify_template_id" label="通知模板" width="120" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.notify_template_id" type="success" size="small">
                {{ getTemplateName(row.notify_template_id) }}
              </el-tag>
              <span v-else class="no-template">未设置</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="info" link @click="viewRule(row)" class="action-btn">
                  详情
                </el-button>
                <el-button type="primary" link @click="editRule(row)" class="action-btn">
                  编辑
                </el-button>
                <el-button type="success" link @click="copyRule(row)" class="action-btn">
                  复制
                </el-button>
                <el-button 
                  v-if="row.alert_state === 'alerting'"
                  type="warning" 
                  link 
                  @click="acknowledgeRuleAlert(row)" 
                  class="action-btn"
                >
                  确认
                </el-button>
                <el-button type="danger" link @click="deleteRule(row)" class="action-btn">
                  删除
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="740px"
      class="rule-dialog"
      :close-on-click-modal="false"
      @close="resetForm"
    >
      <el-form
        :model="ruleForm"
        :rules="formRules"
        ref="formRef"
        label-width="140px"
        class="rule-form"
      >
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="ruleForm.name" placeholder="请输入规则名称" clearable />
        </el-form-item>
        <el-form-item label="所属分组" prop="category">
          <el-select v-model="ruleForm.category" placeholder="请选择组件分组" class="full-width">
            <el-option 
              v-for="category in categoryOptions" 
              :key="category.value" 
              :label="category.label" 
              :value="category.value"
            >
              <span class="category-option">
                <el-tag :type="getCategoryType(category.value)" size="small">{{ category.label }}</el-tag>
                <span class="category-desc">{{ category.description }}</span>
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="PromQL表达式" prop="promql">
          <el-input
            v-model="ruleForm.promql"
            type="textarea"
            :rows="3"
            placeholder="例如: up == 0 或 cpu_usage_percent"
            show-word-limit
            maxlength="500"
          />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="比较方式" prop="comparison">
              <el-select v-model="ruleForm.comparison" placeholder="选择比较方式" class="full-width">
                <el-option label=">" value="gt" />
                <el-option label=">=" value="gte" />
                <el-option label="<" value="lt" />
                <el-option label="<=" value="lte" />
                <el-option label="=" value="eq" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="阈值" prop="threshold">
              <el-input v-model.number="ruleForm.threshold" type="number" placeholder="请输入阈值" class="full-width" min="0" max="999999" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item prop="for_duration">
              <template #label>
                <span class="label-with-tooltip">
                  持续时间(秒)
                  <el-tooltip
                    content="条件必须持续满足多长时间才触发告警"
                    placement="top"
                    effect="dark"
                  >
                    <el-icon class="tooltip-icon"><InfoFilled /></el-icon>
                  </el-tooltip>
                </span>
              </template>
              <el-input v-model.number="ruleForm.for_duration" type="number" placeholder="触发持续时间" class="full-width" min="0" max="86400" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="告警等级" prop="level">
              <el-select v-model="ruleForm.level" placeholder="请选择告警等级" class="full-width">
                <el-option v-for="option in severityOptions" :key="option.value" :label="option.label" :value="option.value">
                  <span class="severity-option">
                    <el-tag :type="option.type" size="small">{{ option.label }}</el-tag>
                  </span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="通知模板" prop="notify_template_id">
              <el-select v-model="ruleForm.notify_template_id" placeholder="请选择通知模板" class="full-width">
                <el-option v-for="template in templates" :key="template.id" :label="template.name" :value="template.id">
                  <span class="template-option">
                    <el-tag :type="template.type === 'email' ? 'success' : 'primary'" size="small">
                      {{ template.type === 'email' ? '邮件' : 'HTTP' }}
                    </el-tag>
                    {{ template.name }}
                  </span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="ruleForm.description" type="textarea" :rows="2" placeholder="规则描述（可选）" show-word-limit maxlength="200" />
        </el-form-item>
        <el-form-item>
          <template #label>
            <span class="label-with-tooltip">
              标签
              <el-tooltip
                content="标签用于告警分组和过滤，支持JSON格式"
                placement="top"
                effect="dark"
              >
                <el-icon class="tooltip-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </span>
          </template>
          <el-input v-model="labelsText" placeholder='JSON格式，如: {"env": "prod", "service": "api"}' />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item prop="suppress">
              <template #label>
                <span class="label-with-tooltip">
                  抑制条件
                  <el-tooltip
                    content="防止重复告警的时间间隔，例如：5m表示同一服务5分钟内只发一次告警"
                    placement="top"
                    effect="dark"
                  >
                    <el-icon class="tooltip-icon"><InfoFilled /></el-icon>
                  </el-tooltip>
                </span>
              </template>
              <el-input v-model="ruleForm.suppress" placeholder="如: 5m" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="max_send_count">
              <template #label>
                <span class="label-with-tooltip">
                  最大次数
                  <el-tooltip
                    content="在持续时间内最多发送的告警次数"
                    placement="top"
                    effect="dark"
                  >
                    <el-icon class="tooltip-icon"><InfoFilled /></el-icon>
                  </el-tooltip>
                </span>
              </template>
              <el-input v-model.number="ruleForm.max_send_count" type="number" placeholder="默认不限制" min="1" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="再通知间隔(秒)" prop="repeat">
              <el-input v-model.number="ruleForm.repeat" type="number" placeholder="可选，单位秒" min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="duration">
              <template #label>
                <span class="label-with-tooltip">
                  发送时长(秒)
                  <el-tooltip
                    content="告警发送超过此时间后自动停止，第二天重置"
                    placement="top"
                    effect="dark"
                  >
                    <el-icon class="tooltip-icon"><InfoFilled /></el-icon>
                  </el-tooltip>
                </span>
              </template>
              <el-input v-model.number="ruleForm.duration" type="number" placeholder="默认3600秒(1小时)" min="60" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="启用状态">
          <el-switch v-model="ruleForm.enabled" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveRule" :loading="submitting">
            <el-icon v-if="!submitting"><Check /></el-icon>
            {{ submitting ? '保存中...' : '保存规则' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      title="规则详情"
      v-model="detailDialogVisible"
      width="650px"
      class="rule-detail-dialog"
    >
      <div class="rule-detail" v-if="selectedRule">
        <div class="detail-section">
          <h4 class="section-title">基本信息</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">规则名称:</span>
              <span class="detail-value">{{ selectedRule.name }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">告警等级:</span>
              <el-tag :type="getSeverityType(selectedRule.level)" size="small">
                {{ getSeverityText(selectedRule.level) }}
              </el-tag>
            </div>
            <div class="detail-item">
              <span class="detail-label">状态:</span>
              <el-tag :type="selectedRule.enabled ? 'success' : 'danger'" size="small">
                {{ selectedRule.enabled ? '启用' : '禁用' }}
              </el-tag>
            </div>
            <div class="detail-item">
              <span class="detail-label">通知模板:</span>
              <span class="detail-value">{{ selectedRule.notify_template_id ? getTemplateName(selectedRule.notify_template_id) : '未设置' }}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-section">
          <h4 class="section-title">监控配置</h4>
          <div class="detail-item full-width">
            <span class="detail-label">PromQL表达式:</span>
            <div class="code-block">{{ selectedRule.promql }}</div>
          </div>
          <div class="detail-item full-width">
            <span class="detail-label">告警条件:</span>
            <span class="detail-value">{{ selectedRule.condition }}</span>
          </div>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">触发持续时间:</span>
              <span class="detail-value">{{ selectedRule.for_duration ? `${selectedRule.for_duration}秒` : '60秒' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">抑制条件:</span>
              <span class="detail-value">{{ selectedRule.suppress || '无' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">再通知间隔:</span>
              <span class="detail-value">{{ selectedRule.repeat ? `${selectedRule.repeat}秒` : '无' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">所属分组:</span>
              <el-tag :type="getCategoryType(selectedRule.category)" size="small">
                {{ getCategoryLabel(selectedRule.category) }}
              </el-tag>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4 class="section-title">抑制策略</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">发送持续时间:</span>
              <span class="detail-value">{{ selectedRule.duration ? `${selectedRule.duration}秒` : '3600秒' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">最大发送次数:</span>
              <span class="detail-value">{{ selectedRule.max_send_count || '无限制' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">当前发送次数:</span>
              <span class="detail-value">{{ selectedRule.send_count || 0 }}次</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">告警状态:</span>
              <el-tag :type="getAlertStateType(selectedRule.alert_state)" size="small">
                {{ getAlertStateText(selectedRule.alert_state) }}
              </el-tag>
            </div>
          </div>
          <div class="detail-grid" v-if="selectedRule.alert_start_time">
            <div class="detail-item">
              <span class="detail-label">告警开始时间:</span>
              <span class="detail-value">{{ formatDateTime(selectedRule.alert_start_time) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">告警持续时长:</span>
              <span class="detail-value">{{ getAlertDuration(selectedRule.alert_start_time) }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section" v-if="selectedRule.description">
          <h4 class="section-title">描述信息</h4>
          <div class="detail-item full-width">
            <span class="detail-value">{{ selectedRule.description }}</span>
          </div>
        </div>

        <div class="detail-section" v-if="selectedRule.labels && Object.keys(selectedRule.labels).length > 0">
          <h4 class="section-title">标签信息</h4>
          <div class="labels-container">
            <el-tag 
              v-for="(value, key) in selectedRule.labels" 
              :key="key" 
              type="info" 
              size="small"
              class="label-tag"
            >
              {{ key }}: {{ value }}
            </el-tag>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailDialogVisible = false">关闭</el-button>
          <el-button type="primary" @click="editRuleFromDetail">编辑规则</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Search, Setting, InfoFilled, Check, Grid,
  Files, DataLine, Lightning, Connection,
  Monitor, Box, DocumentCopy, Compass, TrendCharts
} from '@element-plus/icons-vue'
import { AlertService } from '@/services/alertService'
import { CATEGORY_OPTIONS } from '@/constants'
import type { AlertRule, AlertNotifyTemplate } from '@/types'

// 数据
const rules = ref<AlertRule[]>([])
const templates = ref<AlertNotifyTemplate[]>([])
const loading = ref(false)
const submitting = ref(false)
const searchText = ref('')
const engineStatus = ref('未知')
const switchingRules = ref<Set<number>>(new Set())
const activeCategory = ref('all')

// 对话框
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const isEdit = ref(false)
const currentRuleId = ref<number | null>(null)
const selectedRule = ref<AlertRule | null>(null)

// 表单
const formRef = ref()
const ruleForm = ref<Partial<AlertRule> & { comparison?: string; threshold?: number; duration?: number; max_send_count?: number; for_duration?: number }>({
  name: '',
  category: '',
  promql: '',
  condition: '',
  level: 'medium',
  description: '',
  labels: {},
  notify_template_id: undefined,
  enabled: true,
  suppress: '',
  repeat: 0,
  comparison: 'gt',
  threshold: 0,
  duration: 3600,
  max_send_count: undefined,
  for_duration: 60
})

// 标签文本（用于编辑）
const labelsText = ref('{}')

// 告警等级选项
const severityOptions = [
  { label: '低', value: 'low', type: 'info' },
  { label: '中', value: 'medium', type: 'warning' },
  { label: '高', value: 'high', type: 'danger' },
  { label: '严重', value: 'critical', type: 'danger' }
]

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择组件分组', trigger: 'change' }],
  promql: [{ required: true, message: '请输入PromQL表达式', trigger: 'blur' }],
  threshold: [{ required: true, message: '请输入阈值', trigger: 'blur' }],
  comparison: [{ required: true, message: '请选择比较方式', trigger: 'change' }],
  level: [{ required: true, message: '请选择告警等级', trigger: 'change' }],
  notify_template_id: [{ required: true, message: '请选择通知模板', trigger: 'change' }]
}

// 告警状态相关方法
const getAlertStateType = (state?: string) => {
  switch (state) {
    case 'ok': return 'success'
    case 'alerting': return 'danger'
    case 'silenced': return 'warning'
    default: return 'info'
  }
}

const getAlertStateText = (state?: string) => {
  switch (state) {
    case 'ok': return '正常'
    case 'alerting': return '告警中'
    case 'silenced': return '已抑制'
    default: return '未知'
  }
}

// 时间格式化方法
const formatDateTime = (dateString?: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 计算告警持续时间
const getAlertDuration = (startTime?: string) => {
  if (!startTime) return '-'
  const start = new Date(startTime)
  const now = new Date()
  const diffMs = now.getTime() - start.getTime()
  
  const days = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
  
  if (days > 0) {
    return `${days}天${hours}小时${minutes}分钟`
  } else if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  } else {
    return `${minutes}分钟`
  }
}

// 计算属性
const dialogTitle = computed(() => isEdit.value ? '编辑告警规则' : '新增告警规则')
const categoryOptions = computed(() => CATEGORY_OPTIONS)
const filteredRules = computed(() => {
  let filtered = rules.value

  // 根据分组过滤
  if (activeCategory.value !== 'all') {
    filtered = filtered.filter((rule: AlertRule) => rule.category === activeCategory.value)
  }

  // 根据搜索文本过滤
  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter((rule: AlertRule) => 
      rule.name.toLowerCase().includes(keyword) ||
      rule.promql.toLowerCase().includes(keyword) ||
      (rule.category && rule.category.toLowerCase().includes(keyword))
    )
  }

  return filtered
})

// 方法
const getSeverityType = (severity: string) => {
  const types: Record<string, string> = {
    'low': 'info',
    'medium': 'warning', 
    'high': 'danger',
    'critical': 'danger'
  }
  return types[severity] || 'info'
}

const getSeverityText = (severity: string) => {
  const texts: Record<string, string> = {
    'low': '低',
    'medium': '中',
    'high': '高', 
    'critical': '严重'
  }
  return texts[severity] || severity
}

const getComparisonText = (comparison: string) => {
  const texts: Record<string, string> = {
    'gt': '>',
    'gte': '>=',
    'lt': '<',
    'lte': '<=',
    'eq': '='
  }
  return texts[comparison] || comparison
}

const getTemplateName = (templateId: number) => {
  const template = templates.value.find(t => t.id === templateId)
  return template ? template.name : '未设置'
}

// 解析condition字段
const parseCondition = (condition: string) => {
  if (!condition) return { comparison: 'gt', threshold: 0 }
  
  const match = condition.match(/^([><=]+)\s*(.+)$/)
  if (!match) return { comparison: 'gt', threshold: 0 }
  
  const [, operator, value] = match
  const comparisonMap: Record<string, string> = {
    '>': 'gt',
    '>=': 'gte',
    '<': 'lt',
    '<=': 'lte',
    '=': 'eq'
  }
  
  return {
    comparison: comparisonMap[operator] || 'gt',
    threshold: parseFloat(value) || 0
  }
}

// 加载数据
const loadRules = async () => {
  loading.value = true
  try {
    const data = await AlertService.getRules()
    
    // 处理新的分页响应格式
    if (data && typeof data === 'object' && 'items' in data) {
      rules.value = data.items || []
    } else if (Array.isArray(data)) {
      rules.value = data
    } else {
      rules.value = []
    }
    
    console.log('告警规则数据:', data)
  } catch (error) {
    console.error('加载规则失败:', error)
    rules.value = [] // 确保有默认值
  } finally {
    loading.value = false
  }
}

const loadTemplates = async () => {
  try {
    const data = await AlertService.getTemplates()
    templates.value = data
    console.log('模板数据:', data)
  } catch (error) {
    console.error('加载模板失败:', error)
  }
}

const loadEngineStatus = async () => {
  try {
    const status = await AlertService.getEngineStatus()
    engineStatus.value = status.running ? '运行中' : '已停止'
    console.log('引擎状态:', status)
  } catch (error) {
    console.error('获取引擎状态失败:', error)
    engineStatus.value = '未知'
  }
}

// 引擎操作
const startEngine = async () => {
  try {
    await AlertService.startEngine()
    ElMessage.success('告警引擎启动成功')
    loadEngineStatus()
  } catch (error) {
    ElMessage.error('启动失败')
  }
}

const stopEngine = async () => {
  try {
    await AlertService.stopEngine()
    ElMessage.success('告警引擎停止成功')
    loadEngineStatus()
  } catch (error) {
    ElMessage.error('停止失败')
  }
}

const testEngine = async () => {
  try {
    await AlertService.testEngine()
    ElMessage.success('测试执行完成')
  } catch (error) {
    ElMessage.error('测试执行失败')
  }
}

// 对话框操作
const showCreateDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const viewRule = (rule: AlertRule) => {
  selectedRule.value = rule
  detailDialogVisible.value = true
}

const editRule = (rule: AlertRule) => {
  isEdit.value = true
  currentRuleId.value = rule.id
  
  // 解析condition字段
  const { comparison, threshold } = parseCondition(rule.condition)
  
  ruleForm.value = { 
    ...rule,
    comparison,
    threshold
  }
  
  labelsText.value = JSON.stringify(rule.labels || {}, null, 2)
  dialogVisible.value = true
}

const copyRule = (rule: AlertRule) => {
  isEdit.value = false
  currentRuleId.value = null
  
  // 解析condition字段
  const { comparison, threshold } = parseCondition(rule.condition)
  
  // 复制规则数据，名称添加副本后缀
  ruleForm.value = { 
    ...rule,
    id: undefined, // 清除ID，作为新规则
    name: `${rule.name} - 副本`,
    comparison,
    threshold,
    enabled: false // 复制的规则默认禁用，防止意外触发
  }
  
  labelsText.value = JSON.stringify(rule.labels || {}, null, 2)
  dialogVisible.value = true
  
  ElMessage.success('规则复制成功，请修改后保存')
}

const editRuleFromDetail = () => {
  if (selectedRule.value) {
    detailDialogVisible.value = false
    editRule(selectedRule.value)
  }
}

const resetForm = () => {
  ruleForm.value = {
    name: '',
    category: '',
    promql: '',
    condition: '',
    level: 'medium',
    description: '',
    labels: {},
    notify_template_id: undefined,
    enabled: true,
    suppress: '',
    repeat: 0,
    comparison: 'gt',
    threshold: 0,
    duration: 3600,
    max_send_count: undefined,
    for_duration: 60
  }
  labelsText.value = '{}'
  formRef.value?.resetFields()
}

const comparisonMap = {
  gt: '>',
  gte: '>=',
  lt: '<',
  lte: '<=',
  eq: '='
}

const saveRule = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    // 组装 condition 字段
    const comparison = ruleForm.value.comparison || 'gt'
    const condition = `${comparisonMap[comparison as keyof typeof comparisonMap]} ${ruleForm.value.threshold || 0}`

    // 只组装后端需要的字段
    const payload = {
      name: ruleForm.value.name,
      category: ruleForm.value.category,
      promql: ruleForm.value.promql,
      condition,
      level: ruleForm.value.level,
      suppress: ruleForm.value.suppress,
      repeat: ruleForm.value.repeat,
      duration: ruleForm.value.duration || 3600, // 告警发送持续时间，默认1小时
      max_send_count: ruleForm.value.max_send_count, // 最大发送次数
      for_duration: ruleForm.value.for_duration || 60, // 触发持续时间，默认60秒
      enabled: ruleForm.value.enabled,
      notify_template_id: ruleForm.value.notify_template_id
    }

    submitting.value = true

    if (isEdit.value && currentRuleId.value) {
      await AlertService.updateRule(currentRuleId.value, payload)
      ElMessage.success('规则更新成功')
    } else {
      await AlertService.createRule(payload)
      ElMessage.success('规则创建成功')
    }

    dialogVisible.value = false
    loadRules()
  } catch (error) {
    console.error('保存规则失败:', error)
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

const toggleRule = async (rule: AlertRule) => {
  try {
    switchingRules.value.add(rule.id!)
    await AlertService.updateRule(rule.id!, { enabled: rule.enabled })
    ElMessage.success('状态更新成功')
  } catch (error) {
    console.error('状态更新失败:', error)
    ElMessage.error('状态更新失败')
    rule.enabled = !rule.enabled // 回滚状态
  } finally {
    switchingRules.value.delete(rule.id!)
  }
}

const acknowledgeRuleAlert = async (rule: AlertRule) => {
  try {
    const acknowledgedBy = 'current_user' // 这里应该从用户上下文获取
    const response = await fetch(`/api/alert/rule/${rule.id}/acknowledge?acknowledged_by=${acknowledgedBy}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    const result = await response.json()
    
    if (result.code === 0) {
      ElMessage.success('规则告警已确认，停止发送通知')
      await loadRules()
    } else {
      ElMessage.error(result.msg || '确认失败')
    }
  } catch (error) {
    console.error('确认规则告警失败:', error)
    ElMessage.error('确认失败')
  }
}

const deleteRule = async (rule: AlertRule) => {
  try {
    await ElMessageBox.confirm('确定要删除这个告警规则吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await AlertService.deleteRule(rule.id!)
    ElMessage.success('规则删除成功')
    loadRules()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除规则失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const getCategoryLabel = (category: string) => {
  const categoryItem = categoryOptions.value.find(item => item.value === category)
  return categoryItem ? categoryItem.label : category
}

const getCategoryType = (category: string) => {
  // 为不同组件分配不同颜色类型
  const typeMap: Record<string, string> = {
    'hdfs': 'primary',
    'hive': 'success',
    'spark': 'warning',
    'mysql': 'danger',
    'redis': 'info',
    'kafka': 'primary',
    'elasticsearch': 'warning',
    'kubernetes': 'success',
    'system': 'info',
    'network': 'warning',
    'application': 'primary',
    'other': 'info'
  }
  return typeMap[category] || 'info'
}

const handleCategoryChange = (categoryValue: string) => {
  activeCategory.value = categoryValue
  console.log('切换到分组:', categoryValue)
}

const getTotalCountByCategory = (category: string) => {
  if (category === 'all') {
    return rules.value.length
  }
  return rules.value.filter(rule => rule.category === category).length
}

const getCategoryIcon = (category: string) => {
  const iconMap: Record<string, any> = {
    'hdfs': Files,
    'hive': DataLine,
    'spark': Lightning,
    'mysql': Connection,
    'redis': Monitor,
    'kafka': Box,
    'elasticsearch': DocumentCopy,
    'kubernetes': Compass,
    'system': TrendCharts,
    'network': Connection,
    'application': Monitor,
    'other': Grid
  }
  return iconMap[category] || Grid
}

onMounted(() => {
  // 确保页面先渲染，然后再加载数据
  nextTick(() => {
    // 并行加载数据，但不阻塞页面渲染
    Promise.all([
      loadRules(),
      loadTemplates(),
      loadEngineStatus()
    ]).then(() => {
      console.log('AlertRules数据加载完成')
    }).catch(error => {
      console.warn('AlertRules数据加载部分失败:', error)
    })
  })
})
</script>

<style scoped>
.alert-rules {
  min-height: 100vh;
  background: #faf9f7 !important;
  padding: 24px;
}

/* 页面头部 */
.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.header-info {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #2d3748;
}

.rule-count {
  font-size: 14px;
  color: #718096;
  background: rgba(255, 255, 255, 0.8);
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.create-btn {
  height: 40px;
  padding: 0 20px;
  border-radius: 12px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: #ffffff;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.create-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

/* 内容容器 */
.content-container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 过滤区域 */
.filter-section {
  margin-bottom: 24px;
}

.search-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
}

.search-input {
  width: 320px;
}

.search-icon {
  color: #718096;
}

.search-btn {
  height: 40px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border: 1px solid rgba(102, 126, 234, 0.3);
  color: #667eea;
  font-weight: 600;
  transition: all 0.3s ease;
}

.search-btn:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  transform: translateY(-2px);
}

/* 引擎状态卡片 */
.engine-status-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 20px;
  color: white;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.status-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.status-icon {
  font-size: 18px;
}

.status-title {
  font-weight: 600;
  font-size: 16px;
}

.status-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-tag {
  font-weight: 600;
}

.engine-actions {
  display: flex;
  gap: 8px;
}

.engine-btn {
  border-radius: 8px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  transition: all 0.3s ease;
}

.engine-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

/* 表格容器 */
.table-container {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
}

.rules-table {
  border-radius: 16px;
  overflow: hidden;
}

.rules-table :deep(.el-table__row) {
  transition: all 0.3s ease;
}

.rules-table :deep(.el-table__row:hover) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%) !important;
}

.rules-table :deep(.el-table th) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  color: #2d3748;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.rules-table :deep(.el-table td) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.6);
}

.no-template {
  color: #a0aec0;
  font-size: 12px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.action-btn {
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 6px;
}

/* 对话框样式 */
.rule-dialog :deep(.el-dialog),
.rule-detail-dialog :deep(.el-dialog) {
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid #e8eaed;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.rule-dialog :deep(.el-dialog__header),
.rule-detail-dialog :deep(.el-dialog__header) {
  background: #f8f9fa;
  color: #202124;
  padding: 20px 24px;
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  border-bottom: 1px solid #e8eaed;
  border-radius: 8px 8px 0 0;
}

.rule-dialog :deep(.el-dialog__title),
.rule-detail-dialog :deep(.el-dialog__title) {
  color: #202124;
  font-weight: 500;
}

.rule-form {
  background: #ffffff;
  border-radius: 0;
  padding: 24px;
}

.rule-form .el-input, .rule-form .el-select, .rule-form .el-input-number {
  border-radius: 6px;
  border-color: #dadce0;
}

.rule-form .el-input:focus, .rule-form .el-select:focus {
  border-color: #1a73e8;
}

.rule-form :deep(.el-form-item__label) {
  white-space: nowrap;
  overflow: visible;
}

/* 详情对话框样式 */
.rule-detail {
  padding: 0 8px;
}

.detail-section {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f3f4;
}

.detail-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
  color: #202124;
  padding-bottom: 8px;
  border-bottom: 2px solid #e8eaed;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
  flex-direction: column;
  gap: 8px;
}

.detail-label {
  font-weight: 500;
  color: #5f6368;
  min-width: 100px;
  flex-shrink: 0;
}

.detail-value {
  color: #202124;
  word-break: break-word;
}

.code-block {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #202124;
  border: 1px solid #e8eaed;
}

.labels-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.label-tag {
  margin: 0;
  border-radius: 4px;
  font-weight: 400;
}

.dialog-footer {
  padding: 20px 24px;
  background: #f8f9fa;
  border-top: 1px solid #e8eaed;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  border-radius: 0 0 8px 8px;
}

.dialog-footer .el-button {
  min-width: 80px;
  height: 36px;
  font-size: 14px;
  border-radius: 6px;
  font-weight: 400;
}

.dialog-footer .el-button--primary {
  background: #1a73e8;
  border-color: #1a73e8;
  color: #ffffff;
}

.dialog-footer .el-button--primary:hover {
  background: #1557b0;
  border-color: #1557b0;
}

.dialog-footer .el-button:not(.el-button--primary) {
  background: #ffffff;
  color: #5f6368;
  border: 1px solid #dadce0;
}

.dialog-footer .el-button:not(.el-button--primary):hover {
  background: #f8f9fa;
  border-color: #1a73e8;
  color: #1a73e8;
}

.full-width {
  width: 100%;
}

/* 确保输入框正常显示 */
.el-input-number {
  width: 100%;
}

.el-select {
  width: 100%;
}

/* 表单提示 */
.form-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  color: #5f6368;
  font-size: 12px;
}

/* 严重等级选项 */
.severity-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 模板选项 */
.template-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 分组选项 */
.category-option {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.category-desc {
  color: #909399;
  font-size: 12px;
  margin-left: auto;
}

/* 带tooltip的标签样式 */
.label-with-tooltip {
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
}

.tooltip-icon {
  color: #909399;
  font-size: 14px;
  cursor: help;
  flex-shrink: 0;
}
</style> 