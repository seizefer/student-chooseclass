/**
 * 选课模块 API
 * @version: v1.0.0
 * @date: 2024-11-21
 */
import { http } from './request'

// 选课
export const enrollCourse = (courseId) => {
  return http.post('/api/v1/enrollments', { course_id: courseId })
}

// 退课
export const dropCourse = (enrollmentId) => {
  return http.delete(`/api/v1/enrollments/${enrollmentId}`)
}

// 获取我的选课列表
export const getMyCourses = (status = null) => {
  const params = status ? { status } : {}
  return http.get('/api/v1/enrollments/my-courses', params)
}

// 获取课程选课学生列表（管理员）
export const getCourseEnrollments = (courseId) => {
  return http.get(`/api/v1/enrollments/course/${courseId}`)
}

// 录入成绩（管理员）
export const updateGrade = (enrollmentId, data) => {
  return http.put(`/api/v1/enrollments/${enrollmentId}/grade`, data)
}

// 获取选课统计（管理员）
export const getEnrollmentStatistics = () => {
  return http.get('/api/v1/enrollments/statistics')
}

export default {
  enrollCourse,
  dropCourse,
  getMyCourses,
  getCourseEnrollments,
  updateGrade,
  getEnrollmentStatistics
}
