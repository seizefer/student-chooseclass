/**
 * 转账/交易模块 API
 * @version: v1.0.0
 * @date: 2024-11-21
 */
import { http } from './request'

// 转账
export const transfer = (data) => {
  return http.post('/api/v1/transactions/transfer', data)
}

// 获取余额
export const getBalance = () => {
  return http.get('/api/v1/transactions/balance')
}

// 获取交易历史
export const getHistory = (params = {}) => {
  return http.get('/api/v1/transactions/history', params)
}

// 获取交易详情
export const getTransaction = (transactionId) => {
  return http.get(`/api/v1/transactions/${transactionId}`)
}

// 充值（管理员）
export const recharge = (studentId, amount) => {
  return http.post('/api/v1/transactions/recharge', {
    student_id: studentId,
    amount
  })
}

export default {
  transfer,
  getBalance,
  getHistory,
  getTransaction,
  recharge
}
