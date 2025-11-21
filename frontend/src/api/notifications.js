/**
 * 通知模块 API
 * @version: v1.0.0
 * @date: 2024-11-21
 */
import { http } from './request'

// 获取通知列表
export const getNotifications = (params = {}) => {
  return http.get('/api/v1/notifications', params)
}

// 标记通知为已读
export const markAsRead = (notificationId) => {
  return http.put(`/api/v1/notifications/${notificationId}/read`)
}

// 标记所有通知为已读
export const markAllAsRead = () => {
  return http.put('/api/v1/notifications/read-all')
}

// 删除通知
export const deleteNotification = (notificationId) => {
  return http.delete(`/api/v1/notifications/${notificationId}`)
}

// 清空所有通知
export const clearAll = () => {
  return http.delete('/api/v1/notifications/clear')
}

// 获取未读通知数量
export const getUnreadCount = () => {
  return http.get('/api/v1/notifications/unread/count')
}

export default {
  getNotifications,
  markAsRead,
  markAllAsRead,
  deleteNotification,
  clearAll,
  getUnreadCount
}
