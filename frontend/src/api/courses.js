/**
 * 课程模块 API
 * @version: v1.0.0
 * @date: 2024-11-21
 */
import { http } from './request'

// 获取课程列表
export const getCourses = (params = {}) => {
  return http.get('/api/v1/courses', params)
}

// 获取课程详情
export const getCourseDetail = (courseId) => {
  return http.get(`/api/v1/courses/${courseId}`)
}

// 创建课程（管理员）
export const createCourse = (data) => {
  return http.post('/api/v1/courses', data)
}

// 更新课程（管理员）
export const updateCourse = (courseId, data) => {
  return http.put(`/api/v1/courses/${courseId}`, data)
}

// 删除课程（管理员）
export const deleteCourse = (courseId) => {
  return http.delete(`/api/v1/courses/${courseId}`)
}

// 搜索课程
export const searchCourses = (keyword, params = {}) => {
  return http.get('/api/v1/courses', { search: keyword, ...params })
}

export default {
  getCourses,
  getCourseDetail,
  createCourse,
  updateCourse,
  deleteCourse,
  searchCourses
}
