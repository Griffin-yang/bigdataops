<template>
  <div class="alert-templates">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h2 class="page-title">告警模板管理</h2>
          <span class="template-count">共 {{ templates.length }} 个模板</span>
        </div>
        <el-button type="primary" @click="showCreateDialog" class="create-btn">
          <el-icon><Plus /></el-icon>
          新增模板
        </el-button>
      </div>
    </div>

    <div class="content-container">
      <!-- 模板列表 -->
      <div class="table-container">
        <el-table 
          :data="templates" 
          v-loading="loading"
          class="templates-table"
          stripe
          size="large"
          :header-cell-style="{ backgroundColor: '#f8fafc', color: '#374151', fontWeight: '600' }"
        >
          <el-table-column prop="name" label="模板名称" min-width="180" show-overflow-tooltip />
          <el-table-column prop="type" label="类型" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getTypeTag(row.type)" size="small">
                {{ getTypeLabel(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="配置预览" min-width="300" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="config-preview">{{ getConfigPreview(row) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160" align="center">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button type="primary" link @click="editTemplate(row)" class="action-btn">
                  编辑
                </el-button>
                <el-button type="success" link @click="copyTemplate(row)" class="action-btn">
                  复制
                </el-button>
                <el-button type="danger" link @click="deleteTemplate(row)" class="action-btn">
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
      class="template-dialog"
      :close-on-click-modal="false"
      @close="resetForm"
    >
      <el-form
        :model="templateForm"
        :rules="templateRules"
        ref="formRef"
        label-width="120px"
        class="template-form"
      >
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="templateForm.name" placeholder="请输入模板名称" clearable />
        </el-form-item>

        <el-form-item label="模板类型" prop="type">
          <div class="type-group">
            <el-button type="primary" @click="selectType('email')" :class="{ active: templateForm.type === 'email' }" class="type-btn">
              <el-icon><Message /></el-icon>
              邮件通知
            </el-button>
            <el-button type="primary" @click="selectType('http')" :class="{ active: templateForm.type === 'http' }" class="type-btn">
              <el-icon><Link /></el-icon>
              HTTP通知
            </el-button>
            <el-button type="primary" @click="selectType('lechat')" :class="{ active: templateForm.type === 'lechat' }" class="type-btn">
              <el-icon><ChatLineSquare /></el-icon>
              乐聊告警
            </el-button>
          </div>
        </el-form-item>

        <!-- 邮件配置 -->
        <template v-if="templateForm.type === 'email'">
          <div class="config-section">
            <h4 class="section-title">
              <el-icon><Message /></el-icon>
              邮件服务配置
            </h4>
            
            <el-row :gutter="20">
              <el-col :span="14">
                <el-form-item label="SMTP服务器" prop="smtp_host">
                  <el-input 
                    v-model="emailConfig.smtp_host" 
                    placeholder="如: smtp.163.com" 
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="10">
                <el-form-item label="SMTP端口" prop="smtp_port" class="smtp-port">
                  <el-input-number 
                    v-model="emailConfig.smtp_port" 
                    :min="1" 
                    :max="65535" 
                    class="full-width"
                    placeholder="465"
                    controls-position="right"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="发件人邮箱" prop="from">
              <el-input 
                v-model="emailConfig.from" 
                placeholder="发件人邮箱地址" 
                clearable
              />
            </el-form-item>
            
            <el-form-item label="收件人邮箱" prop="to_emails">
              <el-input 
                v-model="toEmails" 
                placeholder="多个邮箱用逗号分隔，如: user1@example.com, user2@example.com"
                clearable
              />
              <div class="form-tip">
                <el-icon><InfoFilled /></el-icon>
                <span>支持多个收件人，用逗号分隔</span>
              </div>
            </el-form-item>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="邮箱用户名">
                  <el-input 
                    v-model="emailConfig.user" 
                    placeholder="通常为邮箱地址" 
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="邮箱密码">
                  <el-input 
                    v-model="emailConfig.password" 
                    type="password" 
                    placeholder="邮箱密码或授权码" 
                    show-password
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="SSL加密">
              <el-switch 
                v-model="emailConfig.ssl"
                active-text="启用SSL/TLS"
                inactive-text="不使用加密"
              />
            </el-form-item>
          </div>
          
          <div class="config-section">
            <h4 class="section-title">
              <el-icon><Edit /></el-icon>
              邮件内容配置
            </h4>
            
            <el-form-item label="邮件主题" prop="subject_template">
              <el-input 
                v-model="emailConfig.subject_template" 
                placeholder="支持变量: {rule_name}, {level}, {current_value} 等"
                clearable
              />
            </el-form-item>
            
            <el-form-item label="邮件内容" prop="content_template">
              <el-input 
                v-model="emailConfig.content_template" 
                type="textarea" 
                :rows="6"
                placeholder="支持HTML格式和变量，如: &lt;h2&gt;告警详情&lt;/h2&gt;&lt;p&gt;规则: {rule_name}&lt;/p&gt;"
                show-word-limit
                maxlength="2000"
              />
            </el-form-item>
            
            <div class="variable-help">
              <div class="help-title">
                <el-icon><InfoFilled /></el-icon>
                <span>支持的变量</span>
              </div>
              <div class="variable-tags">
                <el-tag size="small" v-for="variable in emailVariables" :key="variable">
                  {{ variable }}
                </el-tag>
              </div>
            </div>
          </div>
        </template>

        <!-- HTTP配置 -->
        <template v-if="templateForm.type === 'http'">
          <div class="config-section">
            <h4 class="section-title">
              <el-icon><Link /></el-icon>
              HTTP请求配置
            </h4>
            
            <el-form-item label="请求URL" prop="url">
              <el-input 
                v-model="httpConfig.url" 
                placeholder="完整的URL地址，如: https://api.example.com/webhook"
                clearable
              />
            </el-form-item>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="请求方法" prop="method">
                  <el-select v-model="httpConfig.method" class="full-width">
                    <el-option label="POST" value="POST" />
                    <el-option label="PUT" value="PUT" />
                    <el-option label="PATCH" value="PATCH" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="超时时间(秒)" prop="timeout">
                  <el-input-number 
                    v-model="httpConfig.timeout" 
                    :min="1" 
                    :max="300" 
                    class="full-width"
                    placeholder="10"
                    controls-position="right"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="请求头" prop="headers">
              <el-input 
                v-model="httpHeaders" 
                type="textarea" 
                :rows="4"
                placeholder='JSON格式，如:
{
  "Content-Type": "application/json",
  "Authorization": "Bearer your-token-here"
}'
                show-word-limit
                maxlength="1000"
              />
              <div class="form-tip">
                <el-icon><InfoFilled /></el-icon>
                <span>请确保JSON格式正确</span>
              </div>
            </el-form-item>
            
            <el-form-item label="请求体模板" prop="body_template">
              <el-input 
                v-model="httpBody" 
                type="textarea" 
                :rows="8"
                placeholder='JSON格式，支持变量，如:
{
  "alert": {
    "rule": "{rule_name}",
    "level": "{level}",
    "value": "{current_value}",
    "threshold": "{threshold}",
    "time": "{fired_at}"
  }
}'
                show-word-limit
                maxlength="2000"
              />
            </el-form-item>
            
            <el-form-item label="SSL验证">
              <el-switch 
                v-model="httpConfig.verify_ssl"
                active-text="验证SSL证书"
                inactive-text="跳过SSL验证"
              />
            </el-form-item>
            
            <div class="variable-help">
              <div class="help-title">
                <el-icon><InfoFilled /></el-icon>
                <span>支持的变量</span>
              </div>
              <div class="variable-tags">
                <el-tag size="small" v-for="variable in httpVariables" :key="variable">
                  {{ variable }}
                </el-tag>
              </div>
            </div>
          </div>
        </template>

        <!-- 乐聊配置 -->
        <template v-if="templateForm.type === 'lechat'">
          <div class="config-section">
            <h4 class="section-title">
              <el-icon><ChatLineSquare /></el-icon>
              乐聊发送模式
            </h4>
            
            <el-form-item label="发送模式" prop="mode">
              <el-radio-group v-model="lechatConfig.mode" @change="handleModeChange">
                <el-radio value="group">
                  <span class="mode-option">
                    <el-icon><UserFilled /></el-icon>
                    群组模式
                  </span>
                </el-radio>
                <el-radio value="personal">
                  <span class="mode-option">
                    <el-icon><User /></el-icon>
                    个人模式
                  </span>
                </el-radio>
              </el-radio-group>
              <div class="form-tip">
                <el-icon><InfoFilled /></el-icon>
                <span>{{ lechatConfig.mode === 'group' ? '发送到乐聊群组' : '发送给指定个人（支持批量）' }}</span>
              </div>
            </el-form-item>
          </div>

          <div class="config-section">
            <h4 class="section-title">
              <el-icon><ChatLineSquare /></el-icon>
              乐聊接口配置
            </h4>
            
            <el-form-item label="接口URL" prop="url">
              <el-input 
                v-model="lechatConfig.url" 
                :placeholder="lechatConfig.mode === 'group' ? '如: http://your-host/api/message/sendTeam' : '如: http://your-host/api/message/sendPersonal'"
                clearable
              />
            </el-form-item>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="发送者ID" prop="fromId">
                  <el-input 
                    v-model="lechatConfig.fromId" 
                    placeholder="如: lyj-dw"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item v-if="lechatConfig.mode === 'group'" label="群组ID" prop="groupId">
                  <el-input 
                    v-model="lechatConfig.groupId" 
                    placeholder="如: group-123456"
                    clearable
                  />
                </el-form-item>
                <el-form-item v-else label="用户工号" prop="userIds">
                  <el-input 
                    v-model="lechatConfig.userIds" 
                    placeholder="多个工号用逗号分隔，如: 233655,056518,283669"
                    clearable
                  />
                  <div class="form-tip">
                    <el-icon><InfoFilled /></el-icon>
                    <span>支持多个工号，用逗号分隔，将根据映射表转换为对应用户ID</span>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-form-item label="扩展字段(ext)" prop="ext">
              <el-input 
                v-model="lechatConfig.ext" 
                type="textarea" 
                :rows="3"
                placeholder='JSON格式，如:
{
  "group": "oa",
  "hait": ["10001"],
  "atName": ["@张三(研发部)"],
  "haitPosition": [0]
}'
                show-word-limit
                maxlength="500"
              />
              <div class="form-tip">
                <el-icon><InfoFilled /></el-icon>
                <span>用于配置@人信息和系统标识，若无@人可简化为 {"group":"oa"}</span>
              </div>
            </el-form-item>
            
            <el-form-item label="消息体模板" prop="body_template">
              <el-input 
                v-model="lechatConfig.body_template" 
                type="textarea" 
                :rows="8"
                placeholder='JSON格式，支持变量，如:
{
  "robot": {"type": "robotAnswer"},
  "type": "multi",
  "msgs": [
    {
      "text": "🚨 【{level}】告警通知\\n规则: {rule_name}\\n当前值: {current_value}\\n时间: {trigger_time}",
      "type": "text"
    }
  ]
}'
                show-word-limit
                maxlength="1500"
              />
            </el-form-item>

            <!-- 个人模式用户映射配置 -->
            <template v-if="lechatConfig.mode === 'personal'">
              <el-form-item label="用户映射表" prop="userMapping">
                <el-input 
                  v-model="lechatConfig.userMapping" 
                  type="textarea" 
                  :rows="6"
                  placeholder='JSON格式，工号到用户ID的映射，如:
{
  "233655": "br",
  "056518": "056518",
  "283669": "dq",
  "357768": "GaoYuFei"
}'
                  show-word-limit
                  maxlength="2000"
                />
                <div class="form-tip">
                  <el-icon><InfoFilled /></el-icon>
                  <span>将工号映射为乐聊用户ID，如果工号在映射表中不存在，则直接使用工号作为用户ID</span>
                </div>
              </el-form-item>
            </template>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="推送内容" prop="pushcontent">
                  <el-input 
                    v-model="lechatConfig.pushcontent" 
                    placeholder="锁屏推送提示内容（可选）"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="发送选项" prop="option">
                  <el-input 
                    v-model="lechatConfig.option" 
                    placeholder='如: {"push":true}（可选）'
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <div class="variable-help">
              <div class="help-title">
                <el-icon><InfoFilled /></el-icon>
                <span>支持的变量</span>
              </div>
              <div class="variable-tags">
                <el-tag size="small" v-for="variable in lechatVariables" :key="variable">
                  {{ variable }}
                </el-tag>
              </div>
            </div>
          </div>
        </template>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">
            取消
          </el-button>
          <el-button type="primary" @click="saveTemplate" :loading="submitting">
            <el-icon v-if="!submitting"><Check /></el-icon>
            {{ submitting ? '保存中...' : '保存模板' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, InfoFilled, Message, Link, Edit, Check, ChatLineSquare, User, UserFilled } from '@element-plus/icons-vue'
import { AlertService } from '@/services/alertService'
import type { AlertNotifyTemplate } from '@/types'

// 数据
const templates = ref<AlertNotifyTemplate[]>([])
const loading = ref(false)
const submitting = ref(false)

// 对话框
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentTemplateId = ref<number | null>(null)

// 表单
const formRef = ref()
const templateForm = ref({
  name: '',
  type: 'email'
})

// 邮件配置
const emailConfig = ref({
  smtp_host: '',
  smtp_port: 465,
  from: '',
  user: '',
  password: '',
  ssl: true,
  subject_template: '【{level}】{rule_name} 告警通知',
  content_template: '<h2>告警详情</h2><p>规则: {rule_name}</p><p>等级: {level}</p><p>当前值: {current_value}</p>'
})

const toEmails = ref('')

// HTTP配置
const httpConfig = ref({
  url: '',
  method: 'POST',
  timeout: 10,
  verify_ssl: true
})

const httpHeaders = ref('{"Content-Type": "application/json"}')
const httpBody = ref('{"rule": "{rule_name}", "level": "{level}", "value": "{current_value}"}')

// 乐聊配置
const lechatConfig = ref({
  mode: 'group',
  url: '',
  fromId: '',
  groupId: '',
  userIds: '',
  ext: '{"group":"oa"}',
  body_template: '{"robot":{"type":"robotAnswer"},"type":"multi","msgs":[{"text":"🚨 【{level}】告警通知\\n规则: {rule_name}\\n当前值: {current_value}\\n时间: {trigger_time}","type":"text"}]}',
  pushcontent: '',
  option: '{"push":true}',
  userMapping: '{}'
})

// 表单验证规则
const templateRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择模板类型', trigger: 'change' }]
}

// 变量列表
const emailVariables = [
  '{rule_name}', '{level}', '{current_value}', '{threshold}', 
  '{fired_at}', '{description}', '{labels}'
]

const httpVariables = [
  '{rule_name}', '{level}', '{current_value}', '{threshold}', 
  '{fired_at}', '{description}', '{labels}'
]

const lechatVariables = [
  '{rule_name}', '{level}', '{current_value}', '{threshold}', 
  '{trigger_time}', '{description}', '{labels}'
]

// 计算属性
const dialogTitle = computed(() => isEdit.value ? '编辑告警模板' : '新增告警模板')

// 方法
const formatTime = (time: string) => {
  return new Date(time).toLocaleString()
}

const getTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = {
    'email': '邮件',
    'http': 'HTTP',
    'lechat': '乐聊'
  }
  return typeMap[type] || type
}

const getTypeTag = (type: string) => {
  const tagMap: Record<string, string> = {
    'email': 'success',
    'http': 'primary',
    'lechat': 'warning'
  }
  return tagMap[type] || 'info'
}

const getConfigPreview = (template: AlertNotifyTemplate) => {
  try {
    const params = typeof template.params === 'string' ? JSON.parse(template.params) : template.params
    if (template.type === 'email') {
      return `SMTP: ${params.smtp_host}:${params.smtp_port} -> ${params.to?.join(', ') || '未设置'}`
    } else if (template.type === 'http') {
      return `${params.method || 'POST'} ${params.url || '未设置'}`
    } else if (template.type === 'lechat') {
      const mode = params.mode || 'group'
      if (mode === 'group') {
        return `乐聊群组: ${params.fromId || '未设置'} -> ${params.groupId || '未设置'}`
      } else {
        const userCount = params.userIds ? params.userIds.split(',').length : 0
        return `乐聊个人: ${params.fromId || '未设置'} -> ${userCount}个用户`
      }
    }
  } catch (error) {
    return '配置格式错误'
  }
  return '未知类型'
}

// 加载数据
const loadTemplates = async () => {
  loading.value = true
  try {
    const data = await AlertService.getTemplates()
    templates.value = data
    console.log('模板数据:', data)
  } catch (error) {
    console.error('加载模板失败:', error)
    ElMessage.error('加载模板失败')
  } finally {
    loading.value = false
  }
}

// 对话框操作
const showCreateDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const editTemplate = (template: AlertNotifyTemplate) => {
  isEdit.value = true
  currentTemplateId.value = template.id
  templateForm.value = {
    name: template.name,
    type: template.type
  }
  
  try {
    const params = typeof template.params === 'string' ? JSON.parse(template.params) : template.params
    if (template.type === 'email') {
      emailConfig.value = { ...emailConfig.value, ...params }
      toEmails.value = params.to?.join(', ') || ''
    } else if (template.type === 'http') {
      httpConfig.value = { ...httpConfig.value, ...params }
      httpHeaders.value = JSON.stringify(params.headers || {}, null, 2)
      httpBody.value = JSON.stringify(params.body_template || {}, null, 2)
    } else if (template.type === 'lechat') {
      lechatConfig.value = { 
        ...lechatConfig.value, 
        ...params,
        mode: params.mode || 'group',
        body_template: JSON.stringify(params.body_template || {}, null, 2),
        ext: JSON.stringify(params.ext || {}, null, 2),
        userMapping: JSON.stringify(params.userMapping || {}, null, 2)
      }
    }
  } catch (error) {
    ElMessage.error('解析模板配置失败')
  }
  
  dialogVisible.value = true
}

const selectType = (type: 'email' | 'http' | 'lechat') => {
  templateForm.value.type = type
}

const handleModeChange = (mode: 'group' | 'personal') => {
  console.log('乐聊模式切换:', mode)
  // 根据模式切换，重置相关配置
  if (mode === 'group') {
    // 群组模式：清空个人模式配置
    lechatConfig.value.userIds = ''
    lechatConfig.value.userMapping = '{}'
    // 设置群组模式的默认URL
    if (!lechatConfig.value.url || lechatConfig.value.url.includes('sendPersonal')) {
      lechatConfig.value.url = 'http://your-host/api/message/sendTeam'
    }
  } else {
    // 个人模式：清空群组模式配置
    lechatConfig.value.groupId = ''
    // 设置个人模式的默认URL
    if (!lechatConfig.value.url || lechatConfig.value.url.includes('sendTeam')) {
      lechatConfig.value.url = 'http://your-host/api/message/sendPersonal'
    }
  }
}

const resetForm = () => {
  templateForm.value = {
    name: '',
    type: 'email'
  }
  
  emailConfig.value = {
    smtp_host: '',
    smtp_port: 465,
    from: '',
    user: '',
    password: '',
    ssl: true,
    subject_template: '【{level}】{rule_name} 告警通知',
    content_template: '<h2>告警详情</h2><p>规则: {rule_name}</p><p>等级: {level}</p><p>当前值: {current_value}</p>'
  }
  
  toEmails.value = ''
  
  httpConfig.value = {
    url: '',
    method: 'POST',
    timeout: 10,
    verify_ssl: true
  }
  
  httpHeaders.value = '{"Content-Type": "application/json"}'
  httpBody.value = '{"rule": "{rule_name}", "level": "{level}", "value": "{current_value}"}'
  
  lechatConfig.value = {
    mode: 'group',
    url: 'http://your-host/api/message/sendTeam',
    fromId: '',
    groupId: '',
    userIds: '',
    ext: '{"group":"oa"}',
    body_template: '{"robot":{"type":"robotAnswer"},"type":"multi","msgs":[{"text":"🚨 【{level}】告警通知\\n规则: {rule_name}\\n当前值: {current_value}\\n时间: {trigger_time}","type":"text"}]}',
    pushcontent: '',
    option: '{"push":true}',
    userMapping: '{}'
  }
}

const saveTemplate = async () => {
  try {
    if (!templateForm.value.name) {
      ElMessage.error('请输入模板名称')
      return
    }
    
    let params: any = {}
    
    if (templateForm.value.type === 'email') {
      if (!emailConfig.value.smtp_host || !emailConfig.value.from || !toEmails.value) {
        ElMessage.error('请填写必要的邮件配置')
        return
      }
      
      params = {
        ...emailConfig.value,
        to: toEmails.value.split(',').map(email => email.trim()).filter(email => email),
        require_auth: !!(emailConfig.value.user && emailConfig.value.password)
      }
    } else if (templateForm.value.type === 'http') {
      if (!httpConfig.value.url) {
        ElMessage.error('请填写请求URL')
        return
      }
      
      try {
        params = {
          ...httpConfig.value,
          headers: JSON.parse(httpHeaders.value),
          body_template: JSON.parse(httpBody.value)
        }
      } catch (error) {
        ElMessage.error('请检查JSON格式是否正确')
        return
      }
    } else if (templateForm.value.type === 'lechat') {
      // 根据模式验证必填字段
      if (!lechatConfig.value.url || !lechatConfig.value.fromId) {
        ElMessage.error('请填写必要的乐聊配置：URL、发送者ID')
        return
      }
      
      if (lechatConfig.value.mode === 'group' && !lechatConfig.value.groupId) {
        ElMessage.error('群组模式需要填写群组ID')
        return
      }
      
      if (lechatConfig.value.mode === 'personal' && !lechatConfig.value.userIds) {
        ElMessage.error('个人模式需要填写用户工号')
        return
      }
      
      try {
        // 基础参数
        params = {
          mode: lechatConfig.value.mode,
          url: lechatConfig.value.url,
          fromId: lechatConfig.value.fromId,
          ext: JSON.parse(lechatConfig.value.ext),
          body_template: JSON.parse(lechatConfig.value.body_template)
        } as any
        
        // 根据模式添加特定参数
        if (lechatConfig.value.mode === 'group') {
          params.groupId = lechatConfig.value.groupId
        } else if (lechatConfig.value.mode === 'personal') {
          params.userIds = lechatConfig.value.userIds
          // 个人模式的用户映射表
          if (lechatConfig.value.userMapping) {
            params.userMapping = JSON.parse(lechatConfig.value.userMapping)
          }
        }
        
        // 处理可选字段
        if (lechatConfig.value.pushcontent) {
          params.pushcontent = lechatConfig.value.pushcontent
        }
        if (lechatConfig.value.option) {
          params.option = JSON.parse(lechatConfig.value.option)
        }
      } catch (error) {
        ElMessage.error('请检查JSON格式是否正确')
        return
      }
    }
    
    const templateData = {
      name: templateForm.value.name,
      type: templateForm.value.type as 'email' | 'http' | 'lechat',
      params: params
    }
    
    submitting.value = true
    
    if (isEdit.value && currentTemplateId.value) {
      await AlertService.updateTemplate(currentTemplateId.value, {
        name: templateData.name,
        params: templateData.params
      })
      ElMessage.success('模板更新成功')
    } else {
      await AlertService.createTemplate(templateData)
      ElMessage.success('模板创建成功')
    }
    
    dialogVisible.value = false
    loadTemplates()
  } catch (error) {
    console.error('保存模板失败:', error)
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

const copyTemplate = (template: AlertNotifyTemplate) => {
  isEdit.value = false
  templateForm.value = {
    name: `${template.name} - 副本`,
    type: template.type
  }
  
  try {
    const params = typeof template.params === 'string' ? JSON.parse(template.params) : template.params
    if (template.type === 'email') {
      emailConfig.value = { ...emailConfig.value, ...params }
      toEmails.value = params.to?.join(', ') || ''
    } else if (template.type === 'http') {
      httpConfig.value = { ...httpConfig.value, ...params }
      httpHeaders.value = JSON.stringify(params.headers || {}, null, 2)
      httpBody.value = JSON.stringify(params.body_template || {}, null, 2)
    } else if (template.type === 'lechat') {
      lechatConfig.value = { 
        ...lechatConfig.value, 
        ...params,
        mode: params.mode || 'group',
        body_template: JSON.stringify(params.body_template || {}, null, 2),
        ext: JSON.stringify(params.ext || {}, null, 2),
        userMapping: JSON.stringify(params.userMapping || {}, null, 2)
      }
    }
  } catch (error) {
    ElMessage.error('解析模板配置失败')
  }
  
  dialogVisible.value = true
}

const deleteTemplate = async (template: AlertNotifyTemplate) => {
  try {
    await ElMessageBox.confirm('确定要删除这个告警模板吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await AlertService.deleteTemplate(template.id)
    ElMessage.success('模板删除成功')
    loadTemplates()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除模板失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadTemplates()
})
</script>

<style scoped>
.alert-templates {
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
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.header-content:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 48px rgba(102, 126, 234, 0.15);
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

.template-count {
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
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.content-container:hover {
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.15);
}

/* 表格容器 */
.table-container {
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.table-container:hover {
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.15);
}

.templates-table {
  border-radius: 20px;
  overflow: hidden;
}

.templates-table :deep(.el-table__row) {
  transition: all 0.3s ease;
}

.templates-table :deep(.el-table__row:hover) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%) !important;
  transform: scale(1.01);
}

.templates-table :deep(.el-table th) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%);
  color: #2d3748;
  font-weight: 600;
  border-bottom: 1px solid rgba(102, 126, 234, 0.15);
}

.templates-table :deep(.el-table td) {
  border-bottom: 1px solid rgba(102, 126, 234, 0.08);
  background: rgba(255, 255, 255, 0.6);
}

.config-preview {
  color: #718096;
  font-size: 13px;
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
.template-dialog :deep(.el-dialog) {
  border-radius: 16px;
  background: #fff;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
}

.template-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  color: #2d3748;
  padding: 24px 32px 0 32px;
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  border-radius: 16px 16px 0 0;
}

.template-dialog :deep(.el-dialog__title) {
  color: #2d3748;
  font-weight: 700;
}

.template-form {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  padding: 20px 24px;
}

.template-form .el-form-item {
  margin-bottom: 16px;
}

/* 模板类型选择紧凑按钮组 */
.type-group {
  display: flex;
  gap: 12px;
}
.type-btn {
  min-width: 120px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  background: rgba(255, 255, 255, 0.8);
  color: #667eea;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  padding: 0 16px;
}
.type-btn.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.config-section {
  margin: 20px 0;
  padding: 16px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 按钮区优化 */
.dialog-footer {
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.9);
  border-top: 1px solid rgba(102, 126, 234, 0.2);
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  border-radius: 0 0 16px 16px;
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

/* 表单提示 */
.form-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  color: #5f6368;
  font-size: 12px;
}

/* 变量帮助 */
.variable-help {
  margin-top: 12px;
  padding: 12px;
  background: #e8f0fe;
  border-radius: 6px;
  border: 1px solid #cfe2ff;
}

.help-title {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  color: #1a73e8;
  font-weight: 500;
  font-size: 14px;
}

.variable-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.variable-tags .el-tag {
  font-family: 'Courier New', monospace;
  background: #e8f0fe;
  border-color: #1a73e8;
  color: #1a73e8;
  border-radius: 4px;
  font-weight: 400;
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

/* 乐聊模式选项 */
.mode-option {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}
</style> 