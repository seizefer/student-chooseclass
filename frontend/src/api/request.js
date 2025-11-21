/**
 * Axios请求封装
 * @version: v1.0.1
 * @date: 2024-12-06
 */
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// 创建axios实例
const request = axios.create({
  baseURL: 'http://localhost:8000',  // 修改为正确的后端地址
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const authStore = useAuthStore()
    
    // 添加认证token
    if (authStore.token) {
      config.headers['Authorization'] = `Bearer ${authStore.token}`
    }
    
    // 添加请求时间戳
    config.headers['X-Request-Time'] = Date.now()
    
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const { data } = response
    
    // 如果是文件下载等特殊响应，直接返回
    if (response.config.responseType === 'blob') {
      return response
    }
    
    // 检查业务状态码
    if (data.code === 200) {
      return data
    }
    
    // 业务错误处理
    if (data.code === 401) {
      // token过期或无效
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
      return Promise.reject(new Error('Unauthorized'))
    }
    
    if (data.code === 403) {
      ElMessage.error('权限不足')
      return Promise.reject(new Error('Forbidden'))
    }
    
    if (data.code === 404) {
      ElMessage.error('请求的资源不存在')
      return Promise.reject(new Error('Not Found'))
    }
    
    if (data.code >= 400) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || 'Request failed'))
    }
    
    return data
  },
  error => {
    console.error('响应错误:', error)
    
    let message = '网络错误'
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          message = data.message || '请求参数错误'
          break
        case 401:
          message = '登录已过期，请重新登录'
          const authStore = useAuthStore()
          authStore.logout()
          router.push('/login')
          break
        case 403:
          message = '权限不足'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        case 502:
          message = '网关错误'
          break
        case 503:
          message = '服务不可用'
          break
        case 504:
          message = '网关超时'
          break
        default:
          message = data.message || `请求失败 (${status})`
      }
    } else if (error.request) {
      if (error.code === 'ECONNABORTED') {
        message = '请求超时，请检查网络连接'
      } else {
        message = '网络连接失败，请检查网络'
      }
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 通用请求方法
export const http = {
  get(url, params = {}) {
    return request.get(url, { params })
  },
  
  post(url, data = {}) {
    return request.post(url, data)
  },
  
  put(url, data = {}) {
    return request.put(url, data)
  },
  
  delete(url, params = {}) {
    return request.delete(url, { params })
  },
  
  patch(url, data = {}) {
    return request.patch(url, data)
  },
  
  // 上传文件
  upload(url, formData, onUploadProgress) {
    return request.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress
    })
  },
  
  // 下载文件
  download(url, params = {}, filename) {
    return request.get(url, {
      params,
      responseType: 'blob'
    }).then(response => {
      const blob = new Blob([response.data])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename || 'download'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    })
  }
}

export default request 