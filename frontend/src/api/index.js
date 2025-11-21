/**
 * API 模块统一导出
 * @version: v1.0.0
 * @date: 2024-11-21
 */

export { default as coursesApi } from './courses'
export { default as enrollmentsApi } from './enrollments'
export { default as friendsApi } from './friends'
export { default as messagesApi } from './messages'
export { default as notificationsApi } from './notifications'
export { default as transactionsApi } from './transactions'

// 导出所有单独的函数
export * from './courses'
export * from './enrollments'
export * from './friends'
export * from './messages'
export * from './notifications'
export * from './transactions'
