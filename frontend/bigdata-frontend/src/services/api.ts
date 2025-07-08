import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import { API_BASE_URL, RESPONSE_CODE, STORAGE_KEYS } from '@/constants'
import type { ApiResponse } from '@/types'

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000, // 减少超时时间，防止长时间等待
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(STORAGE_KEYS.TOKEN)
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response
    
    // 检查业务状态码
    if (data.code !== RESPONSE_CODE.SUCCESS) {
      ElMessage.error(data.msg || '请求失败')
      return Promise.reject(new Error(data.msg || '请求失败'))
    }
    
    return response
  },
  (error) => {
    // 处理HTTP错误状态码
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          ElMessage.error('登录已过期，请重新登录')
          localStorage.removeItem(STORAGE_KEYS.TOKEN)
          localStorage.removeItem(STORAGE_KEYS.USERNAME)
          window.location.href = '/login'
          break
        case 403:
          ElMessage.error('权限不足')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data?.msg || `请求错误: ${status}`)
      }
    } else if (error.request) {
      // 网络错误或超时，不显示错误信息，让调用方决定如何处理
      console.warn('网络请求失败:', error.message)
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        // 超时错误，静默处理
        console.warn('API请求超时，可能是后端服务未启动')
      } else {
        ElMessage.error('网络连接失败，请检查网络')
      }
    } else {
      ElMessage.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

// 通用请求方法
class ApiService {
  static get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return apiClient.get<ApiResponse<T>>(url, config).then(res => res.data.data)
  }

  static post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return apiClient.post<ApiResponse<T>>(url, data, config).then(res => res.data.data)
  }

  static put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return apiClient.put<ApiResponse<T>>(url, data, config).then(res => res.data.data)
  }

  static delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return apiClient.delete<ApiResponse<T>>(url, config).then(res => res.data.data)
  }

  static patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return apiClient.patch<ApiResponse<T>>(url, data, config).then(res => res.data.data)
  }
}

export default ApiService 