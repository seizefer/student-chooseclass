/**
 * 消息模块 API
 * @version: v1.0.0
 * @date: 2024-11-21
 */
import { http } from './request'

// 发送消息
export const sendMessage = (data) => {
  return http.post('/api/v1/messages/send', data)
}

// 获取收件箱
export const getInbox = (params = {}) => {
  return http.get('/api/v1/messages/inbox', params)
}

// 获取发件箱
export const getSent = (params = {}) => {
  return http.get('/api/v1/messages/sent', params)
}

// 获取消息详情
export const getMessage = (messageId) => {
  return http.get(`/api/v1/messages/${messageId}`)
}

// 更新消息状态（已读/未读）
export const updateMessageStatus = (messageId, isRead) => {
  return http.put(`/api/v1/messages/${messageId}/status`, { is_read: isRead })
}

// 删除消息
export const deleteMessage = (messageId) => {
  return http.delete(`/api/v1/messages/${messageId}`)
}

// 获取未读消息数量
export const getUnreadCount = () => {
  return http.get('/api/v1/messages/unread/count')
}

export default {
  sendMessage,
  getInbox,
  getSent,
  getMessage,
  updateMessageStatus,
  deleteMessage,
  getUnreadCount
}
