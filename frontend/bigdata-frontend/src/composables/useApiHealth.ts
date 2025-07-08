import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'

// API健康检查组合式函数
export function useApiHealth() {
  const isApiHealthy = ref(true)
  const healthCheckTimer = ref<number | null>(null)
  const lastCheckTime = ref<Date | null>(null)

  // 检查API健康状态
  const checkApiHealth = async (): Promise<boolean> => {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 3000)

      const response = await fetch('/api/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        },
        signal: controller.signal
      })

      clearTimeout(timeoutId)
      
      if (response.ok) {
        const data = await response.json()
        return data.status === 'healthy' || data.code === 0
      }
      return false
    } catch (error) {
      // 超时或网络错误
      return false
    }
  }

  // 执行健康检查
  const performHealthCheck = async () => {
    const wasHealthy = isApiHealthy.value
    const healthy = await checkApiHealth()
    
    isApiHealthy.value = healthy
    lastCheckTime.value = new Date()

    // 状态变化时显示消息
    if (!wasHealthy && healthy) {
      ElMessage.success('后端服务连接已恢复')
    } else if (wasHealthy && !healthy) {
      console.warn('后端服务连接异常，切换到离线模式')
    }
  }

  // 开始健康检查
  const startHealthCheck = () => {
    // 立即检查一次
    performHealthCheck()
    
    // 每30秒检查一次
    healthCheckTimer.value = window.setInterval(performHealthCheck, 30000)
  }

  // 停止健康检查
  const stopHealthCheck = () => {
    if (healthCheckTimer.value) {
      clearInterval(healthCheckTimer.value)
      healthCheckTimer.value = null
    }
  }

  return {
    isApiHealthy,
    lastCheckTime,
    checkApiHealth,
    performHealthCheck,
    startHealthCheck,
    stopHealthCheck
  }
}