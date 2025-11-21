/**
 * 好友模块 API
 * @version: v1.0.0
 * @date: 2024-11-21
 */
import { http } from './request'

// 发送好友申请
export const sendFriendRequest = (friendId, message = '') => {
  return http.post('/api/v1/friendships/request', {
    friend_id: friendId,
    message
  })
}

// 接受好友申请
export const acceptFriendRequest = (friendshipId) => {
  return http.put(`/api/v1/friendships/${friendshipId}/accept`)
}

// 拒绝好友申请
export const rejectFriendRequest = (friendshipId) => {
  return http.put(`/api/v1/friendships/${friendshipId}/reject`)
}

// 获取好友列表
export const getFriendsList = () => {
  return http.get('/api/v1/friendships/list')
}

// 获取好友申请列表
export const getFriendRequests = () => {
  return http.get('/api/v1/friendships/requests')
}

// 获取好友推荐
export const getFriendRecommendations = () => {
  return http.get('/api/v1/friendships/recommendations')
}

// 删除好友
export const deleteFriend = (friendshipId) => {
  return http.delete(`/api/v1/friendships/${friendshipId}`)
}

export default {
  sendFriendRequest,
  acceptFriendRequest,
  rejectFriendRequest,
  getFriendsList,
  getFriendRequests,
  getFriendRecommendations,
  deleteFriend
}
