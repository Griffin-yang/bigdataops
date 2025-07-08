import ApiService from './api'
import type { User, LoginForm, PaginatedResponse } from '@/types'

interface LdapResponse<T> {
  success: boolean
  msg?: string
  data?: T
}

export class UserService {
  // 登录
  static async login(credentials: LoginForm): Promise<{token: string, username: string}> {
    const response = await ApiService.post<{token: string, username: string}>('/auth/login', credentials)
    return response
  }

  // 获取用户信息
  static async getCurrentUser(): Promise<User> {
    const response = await ApiService.get<User>('/auth/me')
    return response
  }

  // 获取用户列表
  static async getUserList(): Promise<PaginatedResponse<User>> {
    const response = await ApiService.get<PaginatedResponse<User>>('/users')
    return response
  }

  // LDAP用户管理 - 优化后的接口调用
  static async getUsers(env: string = 'prod'): Promise<any[]> {
    try {
      const response = await ApiService.post<any[]>('/ldap/users', { env })
      console.log('LDAP Users response:', response)
      return response || []
    } catch (error) {
      console.error('获取LDAP用户失败:', error)
      return []
    }
  }

  // 查询指定用户信息
  static async getUserInfo(uid: string, env: string = 'prod'): Promise<any | null> {
    try {
      const response = await ApiService.post<any>('/ldap/user/info', { uid, env })
      return response || null
    } catch (error) {
      console.error('获取用户详情失败:', error)
      return null
    }
  }

  // 查询所有组及其成员
  static async getAllGroups(env: string = 'prod'): Promise<any[]> {
    try {
      const response = await ApiService.post<any[]>('/ldap/groups', { env })
      console.log('LDAP Groups response:', response)
      return response || []
    } catch (error) {
      console.error('获取LDAP组失败:', error)
      return []
    }
  }

  // 查询指定组信息
  static async getGroupInfo(groupname: string, env: string = 'prod'): Promise<any | null> {
    try {
      const response = await ApiService.post<any>('/ldap/group/info', { groupname, env })
      return response || null
    } catch (error) {
      console.error('获取组详情失败:', error)
      return null
    }
  }

  // 创建用户
  static async createUser(params: {
    env: string
    username: string
    email?: string
    gidNumber?: string
    homeDirectory?: string
  }): Promise<{success: boolean, msg?: string, user?: any}> {
    try {
      const response = await ApiService.post<{success: boolean, user?: any}>('/ldap/user/create', params)
      return {
        success: response?.success || false,
        user: response?.user
      }
    } catch (error: any) {
      console.error('创建用户失败:', error)
      return {
        success: false,
        msg: error.message || '创建用户失败'
      }
    }
  }

  // 创建组
  static async createGroup(params: {
    env: string
    groupname: string
    gidNumber?: string
  }): Promise<{success: boolean, msg?: string, group?: any}> {
    try {
      const response = await ApiService.post<{success: boolean, group?: any}>('/ldap/group/create', params)
      return {
        success: response?.success || false,
        group: response?.group
      }
    } catch (error: any) {
      console.error('创建组失败:', error)
      return {
        success: false,
        msg: error.message || '创建组失败'
      }
    }
  }

  // 添加用户到组
  static async addUserToGroup(params: {
    env: string
    username: string
    groupname: string
  }): Promise<{success: boolean, msg?: string}> {
    try {
      const response = await ApiService.post<{success: boolean}>('/ldap/group/add', params)
      return {
        success: response?.success || false
      }
    } catch (error: any) {
      console.error('添加用户到组失败:', error)
      return {
        success: false,
        msg: error.message || '添加用户到组失败'
      }
    }
  }
} 