<template>
  <div class="user-management">
    <!-- 顶部操作栏 -->
    <div class="operation-bar">
      <div class="left-section">
        <el-select v-model="env" placeholder="选择环境" class="env-select">
          <el-option label="生产环境" value="prod" />
        </el-select>
        <el-input
          v-model="searchKeyword"
          :placeholder="`搜索${activeTab === 'users' ? '用户' : '组'}`"
          class="search-input"
          clearable
          @clear="handleSearch"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon class="search-icon"><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="right-section">
        <el-button type="primary" @click="showCreateUserDialog" v-if="activeTab === 'users'" class="action-btn">
          <el-icon><Plus /></el-icon>
          创建用户
        </el-button>
        <el-button type="success" @click="showCreateGroupDialog" class="action-btn">
          <el-icon><Plus /></el-icon>
          创建组
        </el-button>
      </div>
    </div>

    <!-- Tab切换 -->
    <div class="tabs-container">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="custom-tabs">
        <!-- 用户管理Tab -->
        <el-tab-pane label="用户管理" name="users">
          <div class="tab-content">
            <div class="content-header">
              <div class="header-info">
                <h3 class="title">用户列表</h3>
                <span class="count">共 {{ userList.length }} 个用户</span>
              </div>
              <el-button type="primary" link @click="refreshUserList" class="refresh-btn">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
            
            <div class="table-container">
              <el-table
                v-loading="loading"
                :data="filteredUsers"
                class="custom-table"
                stripe
                border
                size="large"
                :header-cell-style="{ backgroundColor: '#f8fafc', color: '#374151', fontWeight: '600' }"
              >
                <el-table-column prop="uid" label="用户ID" min-width="120" show-overflow-tooltip />
                <el-table-column prop="username" label="用户名" min-width="120" show-overflow-tooltip />
                <el-table-column prop="email" label="邮箱" min-width="200" show-overflow-tooltip />
                <el-table-column prop="gidNumber" label="GID" width="100" align="center" />
                <el-table-column prop="homeDirectory" label="主目录" min-width="200" show-overflow-tooltip />
                <el-table-column label="所属组" min-width="220">
                  <template #default="{ row }">
                    <div class="groups-container">
                      <el-tag
                        v-for="group in row.groups.slice(0, 3)"
                        :key="group"
                        class="group-tag"
                        size="small"
                        type="info"
                        effect="light"
                      >
                        {{ group }}
                      </el-tag>
                      <el-popover
                        v-if="row.groups.length > 3"
                        placement="top"
                        width="300"
                        trigger="hover"
                      >
                        <template #reference>
                          <el-tag size="small" type="warning" effect="light" class="more-tag">
                            +{{ row.groups.length - 3 }}
                          </el-tag>
                        </template>
                        <div class="all-groups">
                          <el-tag
                            v-for="group in row.groups"
                            :key="group"
                            size="small"
                            type="info"
                            effect="light"
                            class="popup-tag"
                          >
                            {{ group }}
                          </el-tag>
                        </div>
                      </el-popover>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="160" fixed="right" align="center">
                  <template #default="{ row }">
                    <div class="action-buttons">
                      <el-button type="primary" link @click="showUserDetail(row)" class="action-link">
                        详情
                      </el-button>
                      <el-button type="success" link @click="showAddToGroupDialog(row)" class="action-link">
                        加入组
                      </el-button>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-tab-pane>

        <!-- 组管理Tab -->
        <el-tab-pane label="组管理" name="groups">
          <div class="tab-content">
            <div class="content-header">
              <div class="header-info">
                <h3 class="title">组列表</h3>
                <span class="count">共 {{ groupList.length }} 个组</span>
              </div>
              <el-button type="primary" link @click="refreshGroupList" class="refresh-btn">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
            
            <div class="table-container">
              <el-table
                v-loading="groupLoading"
                :data="filteredGroups"
                class="custom-table"
                stripe
                border
                size="large"
                :header-cell-style="{ backgroundColor: '#f8fafc', color: '#374151', fontWeight: '600' }"
              >
                <el-table-column prop="groupname" label="组名" min-width="150" show-overflow-tooltip />
                <el-table-column prop="gidNumber" label="GID" width="100" align="center" />
                <el-table-column label="成员数量" width="120" align="center">
                  <template #default="{ row }">
                    <el-tag type="primary" effect="light" class="count-tag">
                      {{ row.members.length }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="成员列表" min-width="320">
                  <template #default="{ row }">
                    <div class="members-container">
                      <el-tag
                        v-for="member in row.members.slice(0, 4)"
                        :key="member.uid"
                        class="member-tag"
                        size="small"
                        type="success"
                        effect="light"
                      >
                        {{ member.username }}
                      </el-tag>
                      <el-popover
                        v-if="row.members.length > 4"
                        placement="top"
                        width="400"
                        trigger="hover"
                      >
                        <template #reference>
                          <el-tag size="small" type="warning" effect="light" class="more-tag">
                            +{{ row.members.length - 4 }}
                          </el-tag>
                        </template>
                        <div class="all-members">
                          <el-tag
                            v-for="member in row.members"
                            :key="member.uid"
                            size="small"
                            type="success"
                            effect="light"
                            class="popup-tag"
                          >
                            {{ member.username }}
                          </el-tag>
                        </div>
                      </el-popover>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="120" fixed="right" align="center">
                  <template #default="{ row }">
                    <el-button type="primary" link @click="showGroupDetail(row)" class="action-link">
                      详情
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 创建用户对话框 -->
    <el-dialog
      v-model="createUserDialog"
      title="创建用户"
      width="520px"
      class="custom-dialog"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createUserFormRef"
        :model="createUserForm"
        :rules="createUserRules"
        label-width="100px"
        class="custom-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="createUserForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="createUserForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="GID" prop="gidNumber">
          <el-input v-model="createUserForm.gidNumber" placeholder="请输入GID" />
        </el-form-item>
        <el-form-item label="主目录" prop="homeDirectory">
          <el-input v-model="createUserForm.homeDirectory" placeholder="请输入主目录" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="createUserDialog = false">取消</el-button>
          <el-button type="primary" @click="handleCreateUser" :loading="submitting">
            创建
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 创建组对话框 -->
    <el-dialog
      v-model="createGroupDialog"
      title="创建组"
      width="520px"
      class="custom-dialog"
      :close-on-click-modal="false"
    >
      <el-form
        ref="createGroupFormRef"
        :model="createGroupForm"
        :rules="createGroupRules"
        label-width="100px"
        class="custom-form"
      >
        <el-form-item label="组名" prop="groupname">
          <el-input v-model="createGroupForm.groupname" placeholder="请输入组名" />
        </el-form-item>
        <el-form-item label="GID" prop="gidNumber">
          <el-input v-model="createGroupForm.gidNumber" placeholder="请输入GID" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="createGroupDialog = false">取消</el-button>
          <el-button type="primary" @click="handleCreateGroup" :loading="submitting">
            创建
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 添加到组对话框 -->
    <el-dialog
      v-model="addToGroupDialog"
      title="添加到组"
      width="520px"
      class="custom-dialog"
      :close-on-click-modal="false"
    >
      <el-form
        ref="addToGroupFormRef"
        :model="addToGroupForm"
        :rules="addToGroupRules"
        label-width="100px"
        class="custom-form"
      >
        <el-form-item label="用户" prop="username">
          <el-input v-model="addToGroupForm.username" disabled />
        </el-form-item>
        <el-form-item label="选择组" prop="groupname">
          <el-select v-model="addToGroupForm.groupname" placeholder="请选择组" class="full-width">
            <el-option
              v-for="group in groupList"
              :key="group.groupname"
              :label="group.groupname"
              :value="group.groupname"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addToGroupDialog = false">取消</el-button>
          <el-button type="primary" @click="handleAddToGroup" :loading="submitting">
            添加
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 用户详情抽屉 -->
    <el-drawer
      v-model="userDetailDrawer"
      title="用户详情"
      size="520px"
      class="custom-drawer"
    >
      <template v-if="selectedUser">
        <div class="detail-content">
          <div class="detail-card">
                         <div class="detail-header">
               <el-icon class="header-icon"><UserIcon /></el-icon>
               <h4>基本信息</h4>
             </div>
            <div class="detail-body">
              <div class="detail-item">
                <label>用户ID：</label>
                <span class="value">{{ selectedUser.uid }}</span>
              </div>
              <div class="detail-item">
                <label>用户名：</label>
                <span class="value">{{ selectedUser.username }}</span>
              </div>
              <div class="detail-item">
                <label>邮箱：</label>
                <span class="value">{{ selectedUser.email || '-' }}</span>
              </div>
              <div class="detail-item">
                <label>GID：</label>
                <span class="value">{{ selectedUser.gidNumber || '-' }}</span>
              </div>
              <div class="detail-item">
                <label>主目录：</label>
                <span class="value">{{ selectedUser.homeDirectory || '-' }}</span>
              </div>
            </div>
          </div>
          
          <div class="detail-card">
            <div class="detail-header">
              <el-icon class="header-icon"><UserFilled /></el-icon>
              <h4>所属组</h4>
            </div>
            <div class="detail-body">
              <div class="groups-grid">
                <el-tag
                  v-for="group in selectedUser.groups"
                  :key="group"
                  class="detail-group-tag"
                  type="info"
                  effect="light"
                >
                  {{ group }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </template>
    </el-drawer>

    <!-- 组详情抽屉 -->
    <el-drawer
      v-model="groupDetailDrawer"
      title="组详情"
      size="600px"
      class="custom-drawer"
    >
      <template v-if="selectedGroup">
        <div class="detail-content">
          <div class="detail-card">
            <div class="detail-header">
              <el-icon class="header-icon"><UserFilled /></el-icon>
              <h4>基本信息</h4>
            </div>
            <div class="detail-body">
              <div class="detail-item">
                <label>组名：</label>
                <span class="value">{{ selectedGroup.groupname }}</span>
              </div>
              <div class="detail-item">
                <label>GID：</label>
                <span class="value">{{ selectedGroup.gidNumber || '-' }}</span>
              </div>
              <div class="detail-item">
                <label>成员数量：</label>
                <span class="value">{{ selectedGroup.members.length }}</span>
              </div>
            </div>
          </div>
          
          <div class="detail-card">
                         <div class="detail-header">
               <el-icon class="header-icon"><UserIcon /></el-icon>
               <h4>成员列表</h4>
             </div>
            <div class="detail-body">
              <div class="members-table-container">
                <el-table 
                  :data="selectedGroup.members" 
                  class="members-table"
                  size="default"
                  stripe
                  :header-cell-style="{ backgroundColor: '#f8fafc', color: '#374151', fontWeight: '600' }"
                >
                  <el-table-column prop="uid" label="用户ID" width="120" />
                  <el-table-column prop="username" label="用户名" width="120" />
                  <el-table-column prop="email" label="邮箱" show-overflow-tooltip />
                </el-table>
              </div>
            </div>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { Search, Plus, Refresh, User as UserIcon, UserFilled } from '@element-plus/icons-vue'
import { UserService } from '@/services'
import type { User, Group, CreateUserParam, CreateGroupParam, AddUserToGroupParam } from '@/types'

// Tab状态
const activeTab = ref('users')

// 环境选择
const env = ref('prod')

// 搜索
const searchKeyword = ref('')
const loading = ref(false)
const groupLoading = ref(false)
const submitting = ref(false)

// 用户列表
const userList = ref<User[]>([])
const filteredUsers = computed(() => {
  if (!searchKeyword.value) return userList.value
  const keyword = searchKeyword.value.toLowerCase()
  return userList.value.filter((user: User) => 
    user.uid.toLowerCase().includes(keyword) ||
    user.username.toLowerCase().includes(keyword) ||
    (user.email?.toLowerCase() || '').includes(keyword) ||
    user.groups.some((group: string) => group.toLowerCase().includes(keyword))
  )
})

// 组列表
const groupList = ref<Group[]>([])
const filteredGroups = computed(() => {
  if (!searchKeyword.value) return groupList.value
  const keyword = searchKeyword.value.toLowerCase()
  return groupList.value.filter((group: Group) => 
    group.groupname.toLowerCase().includes(keyword) ||
    (group.gidNumber?.toLowerCase() || '').includes(keyword) ||
    group.members.some((member: User) => 
      member.username.toLowerCase().includes(keyword) ||
      member.uid.toLowerCase().includes(keyword)
    )
  )
})

// 创建用户表单
const createUserDialog = ref(false)
const createUserFormRef = ref<FormInstance>()
const createUserForm = ref<CreateUserParam>({
  env: 'prod',
  username: '',
  email: '',
  gidNumber: '',
  homeDirectory: ''
})
const createUserRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }]
}

// 创建组表单
const createGroupDialog = ref(false)
const createGroupFormRef = ref<FormInstance>()
const createGroupForm = ref<CreateGroupParam>({
  env: env.value,
  groupname: '',
  gidNumber: ''
})
const createGroupRules = {
  groupname: [{ required: true, message: '请输入组名', trigger: 'blur' }]
}

// 添加到组表单
const addToGroupDialog = ref(false)
const addToGroupFormRef = ref<FormInstance>()
const addToGroupForm = ref<AddUserToGroupParam>({
  env: env.value,
  username: '',
  groupname: ''
})
const addToGroupRules = {
  groupname: [{ required: true, message: '请选择组', trigger: 'change' }]
}

// 用户详情
const userDetailDrawer = ref(false)
const selectedUser = ref<User | null>(null)

// 组详情
const groupDetailDrawer = ref(false)
const selectedGroup = ref<Group | null>(null)

// 方法
const handleTabChange = (tabName: string) => {
  searchKeyword.value = ''
  if (tabName === 'groups' && groupList.value.length === 0) {
    refreshGroupList()
  }
}

const refreshUserList = async () => {
  loading.value = true
  try {
    const data = await UserService.getUsers(env.value)
    userList.value = data
    console.log('用户数据:', data)
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const refreshGroupList = async () => {
  groupLoading.value = true
  try {
    const data = await UserService.getAllGroups(env.value)
    groupList.value = data
    console.log('组数据:', data)
  } catch (error) {
    console.error('获取组列表失败:', error)
    ElMessage.error('获取组列表失败')
  } finally {
    groupLoading.value = false
  }
}

const handleSearch = () => {
  // 搜索已经通过计算属性实现
}

const showCreateUserDialog = () => {
  createUserForm.value = {
    env: env.value,
    username: '',
    email: '',
    gidNumber: '',
    homeDirectory: ''
  }
  createUserDialog.value = true
}

const showCreateGroupDialog = () => {
  createGroupForm.value = {
    env: env.value,
    groupname: '',
    gidNumber: ''
  }
  createGroupDialog.value = true
}

const showAddToGroupDialog = (user: User) => {
  addToGroupForm.value = {
    env: env.value,
    username: user.uid,
    groupname: ''
  }
  addToGroupDialog.value = true
}

const showUserDetail = (user: User) => {
  selectedUser.value = user
  userDetailDrawer.value = true
}

const showGroupDetail = (group: Group) => {
  selectedGroup.value = group
  groupDetailDrawer.value = true
}

const handleCreateUser = async () => {
  if (!createUserFormRef.value) return
  
  await createUserFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitting.value = true
      try {
        const { username, email, gidNumber, homeDirectory } = createUserForm.value
        const result = await UserService.createUser({
          env: env.value,
          username,
          email,
          gidNumber,
          homeDirectory
        })
        
        if (result.success) {
          ElMessage.success('创建用户成功')
          createUserDialog.value = false
          refreshUserList()
        } else {
          ElMessage.error(result.msg || '创建用户失败')
        }
      } catch (error) {
        ElMessage.error('创建用户失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleCreateGroup = async () => {
  if (!createGroupFormRef.value) return
  
  await createGroupFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitting.value = true
      try {
        const { groupname, gidNumber } = createGroupForm.value
        const result = await UserService.createGroup({
          env: env.value,
          groupname,
          gidNumber
        })
        
        if (result.success) {
          ElMessage.success('创建组成功')
          createGroupDialog.value = false
          refreshGroupList()
        } else {
          ElMessage.error(result.msg || '创建组失败')
        }
      } catch (error) {
        ElMessage.error('创建组失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleAddToGroup = async () => {
  if (!addToGroupFormRef.value) return
  
  await addToGroupFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitting.value = true
      try {
        const { username, groupname } = addToGroupForm.value
        const result = await UserService.addUserToGroup({
          env: env.value,
          username,
          groupname
        })
        
        if (result.success) {
          ElMessage.success('添加到组成功')
          addToGroupDialog.value = false
          refreshUserList()
          refreshGroupList()
        } else {
          ElMessage.error('添加到组失败')
        }
      } catch (error) {
        ElMessage.error('添加到组失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 初始化
onMounted(() => {
  refreshUserList()
})
</script>

<style scoped>
.user-management {
  min-height: 100vh;
  background: #faf9f7 !important;
  padding: 24px;
}

/* 顶部操作栏 */
.operation-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  backdrop-filter: blur(20px);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.operation-bar:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 48px rgba(102, 126, 234, 0.15);
}

.left-section {
  display: flex;
  gap: 16px;
  align-items: center;
}

.right-section {
  display: flex;
  gap: 12px;
}

.env-select {
  width: 140px;
}

.search-input {
  width: 280px;
}

.search-icon {
  color: #718096;
}

.action-btn {
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

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

/* Tab容器 */
.tabs-container {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.tabs-container:hover {
  box-shadow: 0 16px 48px rgba(102, 126, 234, 0.15);
}

.custom-tabs {
  --el-color-primary: #667eea;
}

.tab-content {
  padding-top: 16px;
}

/* 内容头部 */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.2);
}

.header-info {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #2d3748;
}

.count {
  font-size: 14px;
  color: #718096;
  background: rgba(102, 126, 234, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
  font-weight: 500;
}

.refresh-btn {
  font-weight: 500;
  color: #667eea;
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

.custom-table {
  border-radius: 20px;
  overflow: hidden;
}

.custom-table :deep(.el-table__body-wrapper) {
  border-radius: 0 0 20px 20px;
}

.custom-table :deep(.el-table__row) {
  transition: all 0.3s ease;
}

.custom-table :deep(.el-table__row:hover) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%) !important;
  transform: translateY(-1px) scale(1.01);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.custom-table :deep(.el-table th) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%);
  color: #2d3748;
  font-weight: 600;
  border-bottom: 1px solid rgba(102, 126, 234, 0.15);
}

.custom-table :deep(.el-table td) {
  border-bottom: 1px solid rgba(102, 126, 234, 0.08);
  background: rgba(255, 255, 255, 0.7);
}

/* Tag样式 */
.groups-container,
.members-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.group-tag,
.member-tag {
  border-radius: 8px;
  font-weight: 500;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.count-tag {
  font-weight: 600;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.more-tag {
  cursor: pointer;
  border-radius: 8px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.all-groups,
.all-members {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.popup-tag {
  border-radius: 6px;
  font-weight: 500;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.action-link {
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 6px;
}

/* 对话框样式 */
.custom-dialog :deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.custom-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  color: #2d3748;
  padding: 20px 24px;
  margin: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.custom-dialog :deep(.el-dialog__title) {
  color: #2d3748;
  font-weight: 600;
}

.custom-form {
  padding: 20px 24px;
  background: rgba(255, 255, 255, 0.8);
}

.dialog-footer {
  padding: 20px 24px;
  text-align: right;
  background: rgba(255, 255, 255, 0.9);
  margin: 0;
  border-top: 1px solid rgba(102, 126, 234, 0.2);
}

.dialog-footer .el-button {
  height: 36px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.dialog-footer .el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.dialog-footer .el-button--primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

.full-width {
  width: 100%;
}

/* 抽屉样式 */
.custom-drawer :deep(.el-drawer__header) {
  background: #f8f9fa;
  color: #202124;
  padding: 20px 24px;
  margin: 0;
  border-bottom: 1px solid #e8eaed;
}

.custom-drawer :deep(.el-drawer__title) {
  color: #202124;
  font-weight: 500;
}

.custom-drawer :deep(.el-drawer__body) {
  padding: 0;
  background: #f8f9fa;
}

/* 详情内容 */
.detail-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-card {
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e8eaed;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.detail-header {
  background: #f8f9fa;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid #e8eaed;
}

.header-icon {
  color: #5f6368;
  font-size: 18px;
}

.detail-header h4 {
  margin: 0;
  color: #202124;
  font-weight: 500;
}

.detail-body {
  padding: 20px;
}

.detail-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f1f3f4;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-item label {
  font-weight: 500;
  color: #5f6368;
  width: 100px;
  flex-shrink: 0;
}

.detail-item .value {
  color: #202124;
  font-weight: 400;
}

.groups-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-group-tag {
  border-radius: 4px;
  font-weight: 400;
}

.members-table-container {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e8eaed;
}

.members-table {
  border-radius: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-management {
    padding: 16px;
  }
  
  .operation-bar {
    flex-direction: column;
    gap: 16px;
    padding: 16px;
  }
  
  .left-section,
  .right-section {
    width: 100%;
    justify-content: center;
  }
  
  .search-input {
    width: 100%;
  }
  
  .tabs-container {
    padding: 16px;
  }
  
  .detail-content {
    padding: 16px;
  }
}
</style> 