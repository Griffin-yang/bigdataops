<template>
  <div class="layout-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '240px'" class="sidebar">
        <div class="logo" :class="{ 'collapsed': isCollapse }">
          <el-icon class="logo-icon"><DataBoard /></el-icon>
          <transition name="fade">
            <span v-show="!isCollapse" class="logo-text">大数据运维平台</span>
          </transition>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          :default-openeds="defaultOpeneds"
          :collapse="isCollapse"
          :unique-opened="false"
          class="sidebar-menu"
          :router="false"
          @select="handleMenuSelect"
        >
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <template #title>首页</template>
          </el-menu-item>
          
          <el-sub-menu index="user-management">
            <template #title>
              <el-icon><User /></el-icon>
              <span>用户管理</span>
            </template>
            <el-menu-item index="/users">
              <el-icon><UserFilled /></el-icon>
              <template #title>LDAP用户</template>
            </el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="alert-management">
            <template #title>
              <el-icon><Bell /></el-icon>
              <span>告警管理</span>
            </template>
            <el-menu-item index="/alert-rules">
              <el-icon><Warning /></el-icon>
              <template #title>告警规则</template>
            </el-menu-item>
            <el-menu-item index="/alert-templates">
              <el-icon><Message /></el-icon>
              <template #title>告警模板</template>
            </el-menu-item>
            <el-menu-item index="/alert-history">
              <el-icon><Clock /></el-icon>
              <template #title>告警历史</template>
            </el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="cluster-monitoring">
            <template #title>
              <el-icon><Monitor /></el-icon>
              <span>集群监控</span>
            </template>
            <el-menu-item index="/monitoring">
              <el-icon><DataBoard /></el-icon>
              <template #title>系统监控</template>
            </el-menu-item>
            <el-menu-item index="/cluster/overview">
              <el-icon><Monitor /></el-icon>
              <template #title>集群总览</template>
            </el-menu-item>
            <el-menu-item index="/cluster/components">
              <el-icon><Setting /></el-icon>
              <template #title>组件监控</template>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container>
        <!-- 顶部导航 -->
        <el-header class="header">
          <div class="header-left">
            <el-button 
              @click="toggleCollapse" 
              :icon="isCollapse ? Expand : Fold" 
              text 
              class="collapse-btn"
            />
            
            <!-- 面包屑导航 -->
            <el-breadcrumb separator="/" class="breadcrumb">
              <el-breadcrumb-item to="/dashboard">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="breadcrumbItems.length > 0" 
                v-for="item in breadcrumbItems" 
                :key="item.name"
                :to="item.path || undefined"
              >
                {{ item.name }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-dropdown">
                <el-icon><Avatar /></el-icon>
                <span class="username">管理员</span>
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <!-- 主要内容 -->
        <el-main class="main-content">
          <RouterView :key="route.fullPath" />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  House,
  User,
  UserFilled,
  Bell,
  Warning,
  Message,
  Clock,
  Monitor,
  Fold,
  Expand,
  Avatar,
  ArrowDown,
  SwitchButton,
  DataBoard,
  Setting
} from '@element-plus/icons-vue'
import { ROUTES, STORAGE_KEYS } from '@/constants'
import { useApiHealth } from '@/composables/useApiHealth'

const route = useRoute()
const router = useRouter()
const { isApiHealthy, startHealthCheck, stopHealthCheck } = useApiHealth()

// 侧边栏折叠状态
const isCollapse = ref(false)

// 计算当前激活的菜单项
const activeMenu = computed(() => {
  return route.path
})

// 计算默认展开的子菜单
const defaultOpeneds = computed(() => {
  const path = route.path
  const openeds = []
  
  if (path.startsWith('/users')) {
    openeds.push('user-management')
  }
  if (path.startsWith('/alert-')) {
    openeds.push('alert-management')
  }
  if (path.startsWith('/monitoring') || path.startsWith('/cluster/')) {
    openeds.push('cluster-monitoring')
  }
  
  return openeds
})

// 面包屑导航
const breadcrumbItems = computed(() => {
  const path = route.path
  const items = []
  
  // 路由映射
  const routeMap: Record<string, { name: string; parent?: string; parentName?: string }> = {
    '/users': { name: 'LDAP用户管理', parent: 'user-management', parentName: '用户管理' },
    '/alert-rules': { name: '告警规则', parent: 'alert-management', parentName: '告警管理' },
    '/alert-templates': { name: '告警模板', parent: 'alert-management', parentName: '告警管理' },
    '/alert-history': { name: '告警历史', parent: 'alert-management', parentName: '告警管理' },
    '/monitoring': { name: '系统监控', parent: 'cluster-monitoring', parentName: '集群监控' },
    '/cluster/overview': { name: '集群总览', parent: 'cluster-monitoring', parentName: '集群监控' },
    '/cluster/components': { name: '组件监控', parent: 'cluster-monitoring', parentName: '集群监控' }
  }
  
  const current = routeMap[path]
  if (current) {
    if (current.parent && current.parentName) {
      items.push({ name: current.parentName, path: null })
    }
    items.push({ name: current.name, path })
  }
  
  return items
})

// 方法
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const handleMenuSelect = async (index: string) => {
  console.log('菜单选择:', index, '当前路径:', route.path)
  
  // 跳过父菜单项（不是实际路由路径的菜单项）
  if (index === 'user-management' || index === 'alert-management' || index === 'cluster-monitoring') {
    return
  }
  
  // 强制路由切换，确保页面内容更新
  if (index && index.startsWith('/')) {
    try {
      if (index === route.path) {
        // 同一个路径，先跳转到临时路由再跳回来，强制组件重新渲染
        await router.replace('/')
        await nextTick()
        await router.replace(index)
        console.log('路由强制刷新成功:', index)
      } else {
        // 不同路径，直接跳转
        await router.push(index)
        console.log('路由切换成功:', index)
      }
    } catch (error) {
      console.error('路由跳转失败:', error)
      // 如果路由跳转失败，显示错误信息
      ElMessage.error('页面跳转失败，请稍后重试')
      
      // 尝试强制刷新页面
      setTimeout(() => {
        if (confirm('页面可能出现问题，是否刷新页面？')) {
          window.location.reload()
        }
      }, 1000)
    }
  }
}

const handleCommand = (command: string) => {
  if (command === 'logout') {
    localStorage.removeItem(STORAGE_KEYS.TOKEN)
    localStorage.removeItem(STORAGE_KEYS.USERNAME)
    localStorage.removeItem(STORAGE_KEYS.USER_INFO)
    ElMessage.success('退出登录成功')
    router.push(ROUTES.LOGIN)
  }
}

// 面包屑点击处理
const handleBreadcrumbClick = async (item: any) => {
  if (item.path && item.path !== route.path) {
    try {
      await router.push(item.path)
      console.log('面包屑导航成功:', item.path)
    } catch (error) {
      console.error('面包屑导航失败:', error)
      ElMessage.error('页面跳转失败')
    }
  }
}

// 监听路由变化
watch(() => route.path, (newPath, oldPath) => {
  console.log('路由变化:', oldPath, '->', newPath)
}, { immediate: true })

// 生命周期
onMounted(() => {
  startHealthCheck()
})

onUnmounted(() => {
  stopHealthCheck()
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  position: relative;
  overflow: hidden;
  background: #faf9f7;
}

/* 侧边栏样式 */
.sidebar {
  background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  transition: width 0.3s ease;
  position: relative;
  z-index: 1000;
  flex-shrink: 0;
  height: 100vh;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.logo.collapsed {
  padding: 0 16px;
}

.logo-icon {
  font-size: 28px;
  color: #64b5f6;
  margin-right: 12px;
  transition: all 0.3s ease;
}

.logo.collapsed .logo-icon {
  margin-right: 0;
  font-size: 20px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  white-space: nowrap;
}

/* 菜单样式 */
.sidebar-menu {
  border: none;
  background: transparent;
  --el-menu-item-height: 48px;
  --el-menu-sub-item-height: 40px;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  margin: 4px 12px;
  padding-left: 20px !important;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background: linear-gradient(135deg, rgba(100, 181, 246, 0.2) 0%, rgba(129, 212, 250, 0.2) 100%);
  color: #ffffff;
  transform: translateX(4px);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #64b5f6 0%, #81d4fa 100%);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(100, 181, 246, 0.4);
}

.sidebar-menu :deep(.el-sub-menu.is-opened > .el-sub-menu__title) {
  background: linear-gradient(135deg, rgba(100, 181, 246, 0.25) 0%, rgba(129, 212, 250, 0.25) 100%);
  color: #ffffff;
  transform: translateX(6px);
  box-shadow: 0 4px 12px rgba(100, 181, 246, 0.2);
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item) {
  margin: 2px 12px;
  padding-left: 48px !important;
  background: transparent;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item:hover) {
  background: linear-gradient(135deg, rgba(100, 181, 246, 0.25) 0%, rgba(129, 212, 250, 0.25) 100%);
  color: #ffffff;
  transform: translateX(6px);
  box-shadow: 0 4px 12px rgba(100, 181, 246, 0.2);
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item.is-active) {
  background: linear-gradient(135deg, #64b5f6 0%, #81d4fa 100%);
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(100, 181, 246, 0.4);
  transform: translateX(4px);
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item.is-active)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 16px;
  background: #ffffff;
  border-radius: 2px 0 0 2px;
  box-shadow: 0 2px 8px rgba(255, 255, 255, 0.3);
}

.sidebar-menu :deep(.el-icon) {
  color: inherit;
  margin-right: 12px;
  font-size: 18px;
}

/* 折叠状态样式 */
.sidebar-menu.el-menu--collapse :deep(.el-menu-item),
.sidebar-menu.el-menu--collapse :deep(.el-sub-menu__title) {
  margin: 4px 8px;
  padding-left: 0 !important;
  justify-content: center;
  border-radius: 8px;
}

/* 顶部导航 */
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-bottom: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
  position: relative;
}

.header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-btn {
  margin-right: 16px;
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
  padding: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
  transform: scale(1.1);
}

.breadcrumb {
  font-size: 14px;
}

.breadcrumb :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: #ffffff;
  font-weight: 600;
}

.breadcrumb :deep(.el-breadcrumb__inner) {
  color: rgba(255, 255, 255, 0.8);
}

.breadcrumb :deep(.el-breadcrumb__inner:hover) {
  color: #ffffff;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.username {
  margin: 0 8px;
  font-size: 14px;
  color: #ffffff;
  font-weight: 500;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 20px;
  transition: background-color 0.3s ease;
  color: rgba(255, 255, 255, 0.9);
}

/* 主内容区 */
.main-content {
  background: transparent;
  padding: 0;
  overflow: hidden;
  width: 100%;
  flex: 1;
  height: calc(100vh - 60px);
}

/* 强制移除所有可能的白色背景 */
.sidebar-menu :deep(.el-menu--vertical) {
  background: transparent !important;
}

.sidebar-menu :deep(.el-sub-menu__title),
.sidebar-menu :deep(.el-menu-item) {
  background: transparent !important;
  background-color: transparent !important;
}

.sidebar-menu :deep(.el-sub-menu .el-menu) {
  background: transparent !important;
  background-color: transparent !important;
}

.sidebar-menu :deep(.el-sub-menu .el-menu .el-menu-item) {
  background: transparent !important;
  background-color: transparent !important;
  color: rgba(255, 255, 255, 0.8) !important;
}

/* 强制覆盖Element Plus的默认白色背景 */
.sidebar :deep(.el-menu),
.sidebar :deep(.el-menu-vertical),
.sidebar :deep(.el-sub-menu),
.sidebar :deep(.el-sub-menu .el-menu),
.sidebar :deep(.el-menu-item),
.sidebar :deep(.el-sub-menu__title) {
  background: transparent !important;
  background-color: transparent !important;
}

/* 确保展开状态下的子菜单也是透明的 */
.sidebar :deep(.el-sub-menu.is-opened .el-menu) {
  background: transparent !important;
  background-color: transparent !important;
}

.sidebar :deep(.el-sub-menu.is-opened .el-menu-item) {
  background: transparent !important;
  background-color: rgba(0, 0, 0, 0) !important;
  color: rgba(255, 255, 255, 0.8) !important;
}

.sidebar :deep(.el-sub-menu.is-opened .el-menu-item:hover) {
  background: linear-gradient(135deg, rgba(100, 181, 246, 0.25) 0%, rgba(129, 212, 250, 0.25) 100%) !important;
  background-color: transparent !important;
  color: #ffffff !important;
}

.sidebar :deep(.el-sub-menu.is-opened .el-menu-item.is-active) {
  background: linear-gradient(135deg, #64b5f6 0%, #81d4fa 100%) !important;
  background-color: transparent !important;
  color: #ffffff !important;
}

/* 重新定义二级菜单项的样式 */
.sidebar-menu :deep(.el-sub-menu .el-menu-item) {
  margin: 2px 12px !important;
  padding-left: 48px !important;
  background: transparent !important;
  background-color: transparent !important;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8) !important;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  border: none;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item:hover) {
  background: linear-gradient(135deg, rgba(100, 181, 246, 0.25) 0%, rgba(129, 212, 250, 0.25) 100%) !important;
  background-color: transparent !important;
  color: #ffffff !important;
  transform: translateX(6px);
  box-shadow: 0 4px 12px rgba(100, 181, 246, 0.2);
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item.is-active) {
  background: linear-gradient(135deg, #64b5f6 0%, #81d4fa 100%) !important;
  background-color: transparent !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(100, 181, 246, 0.4);
  transform: translateX(4px);
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item.is-active)::after {
  content: '';
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 16px;
  background: #ffffff;
  border-radius: 2px 0 0 2px;
  box-shadow: 0 2px 8px rgba(255, 255, 255, 0.3);
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 64px !important;
  }
  
  .logo-text {
    display: none;
  }
  
  .breadcrumb {
    display: none;
  }
}

/* 大屏优化 */
@media (min-width: 1920px) {
  .sidebar {
    width: 280px;
  }
  
  .main-content {
    padding: 0;
  }
  
  .logo-text {
    font-size: 20px;
  }
  
  .sidebar-menu :deep(.el-menu-item),
  .sidebar-menu :deep(.el-sub-menu__title) {
    font-size: 15px;
  }
}

/* 确保布局完全填充 */
@media (min-width: 1200px) {
  .layout-container {
    min-height: 100vh;
  }
  
  .sidebar {
    max-width: 300px;
  }
}
</style> 