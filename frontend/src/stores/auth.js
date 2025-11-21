/**
 * 用户认证状态管理
 * @version: v1.2.0
 * @date: 2024-12-06
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { http } from '@/api/request'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)
  const loading = ref(false)
  
  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userType = computed(() => user.value?.user_type || '')
  const userName = computed(() => user.value?.name || '')
  const userId = computed(() => user.value?.student_id || user.value?.admin_id || '')
  
  // 保存token到localStorage
  const setToken = (newToken) => {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
  }
  
  // 保存用户信息
  const setUser = (userData) => {
    user.value = userData
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
    } else {
      localStorage.removeItem('user')
    }
  }
  
  // 登录
  const login = async (credentials) => {
    try {
      loading.value = true
      const response = await http.post('/api/v1/auth/login', credentials)
      
      if (response.code === 200) {
        const { access_token, user: userData } = response.data
        setToken(access_token)
        setUser(userData)
        
        ElMessage.success('登录成功')
        return { success: true, data: response.data }
      } else {
        ElMessage.error(response.message || '登录失败')
        return { success: false, message: response.message }
      }
    } catch (error) {
      console.error('登录错误:', error)
      ElMessage.error('登录失败，请检查网络连接')
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }
  
  // 注册
  const register = async (userData) => {
    try {
      loading.value = true
      const response = await http.post('/api/v1/auth/register', userData)
      
      if (response.code === 200) {
        ElMessage.success('注册成功，请登录')
        return { success: true, data: response.data }
      } else {
        ElMessage.error(response.message || '注册失败')
        return { success: false, message: response.message }
      }
    } catch (error) {
      console.error('注册错误:', error)
      ElMessage.error('注册失败，请检查网络连接')
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }
  
  // 获取当前用户信息
  const fetchUserInfo = async () => {
    try {
      const response = await http.get('/api/v1/auth/me')
      
      if (response.code === 200) {
        setUser(response.data)
        return { success: true, data: response.data }
      } else {
        return { success: false, message: response.message }
      }
    } catch (error) {
      console.error('获取用户信息错误:', error)
      return { success: false, message: error.message }
    }
  }
  
  // 刷新token
  const refreshToken = async () => {
    try {
      const response = await http.post('/api/v1/auth/refresh')
      
      if (response.code === 200) {
        setToken(response.data.access_token)
        return { success: true, data: response.data }
      } else {
        // token刷新失败，需要重新登录
        logout()
        return { success: false, message: response.message }
      }
    } catch (error) {
      console.error('刷新token错误:', error)
      logout()
      return { success: false, message: error.message }
    }
  }
  
  // 登出
  const logout = async () => {
    try {
      // 调用登出API
      if (token.value) {
        await http.post('/api/v1/auth/logout')
      }
    } catch (error) {
      console.error('登出API调用失败:', error)
    } finally {
      // 清除本地状态
      setToken('')
      setUser(null)
      ElMessage.success('已退出登录')
    }
  }
  
  // 检查token有效性
  const checkAuth = async () => {
    if (!token.value) {
      return false
    }
    
    // 尝试获取用户信息验证token
    const result = await fetchUserInfo()
    return result.success
  }
  
  // 初始化
  const init = async () => {
    // 从localStorage恢复用户信息
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
      } catch (error) {
        console.error('解析用户信息失败:', error)
        localStorage.removeItem('user')
      }
    }
    
    // 如果有token，验证有效性
    if (token.value) {
      const isValid = await checkAuth()
      if (!isValid) {
        logout()
      }
    }
  }
  
  return {
    // 状态
    token,
    user,
    loading,
    
    // 计算属性
    isAuthenticated,
    userType,
    userName,
    userId,
    
    // 方法
    login,
    register,
    logout,
    fetchUserInfo,
    refreshToken,
    checkAuth,
    init,
    setToken,
    setUser
  }
}) 