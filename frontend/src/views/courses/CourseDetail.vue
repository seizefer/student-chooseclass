<template>
  <div class="course-detail">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <!-- 课程详情 -->
    <template v-else-if="course">
      <!-- 课程头部信息 -->
      <el-card class="course-header" shadow="never">
        <div class="header-content">
          <div class="course-cover">
            <el-image
              :src="course.cover || defaultCover"
              fit="cover"
              class="cover-image"
            >
              <template #error>
                <div class="image-placeholder">
                  <el-icon :size="48"><Reading /></el-icon>
                </div>
              </template>
            </el-image>
          </div>

          <div class="course-info">
            <h1 class="course-title">{{ course.name }}</h1>
            <div class="course-meta">
              <el-tag>{{ course.department_name }}</el-tag>
              <span class="meta-item">
                <el-icon><User /></el-icon>
                {{ course.instructor }}
              </span>
              <span class="meta-item">
                <el-icon><Medal /></el-icon>
                {{ course.credits }} 学分
              </span>
            </div>

            <div class="course-stats">
              <div class="stat-item">
                <span class="stat-value">{{ course.current_enrollment }}</span>
                <span class="stat-label">已选人数</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ course.capacity }}</span>
                <span class="stat-label">课程容量</span>
              </div>
              <div class="stat-item">
                <span class="stat-value" :class="{ 'text-danger': availableSeats <= 5 }">
                  {{ availableSeats }}
                </span>
                <span class="stat-label">剩余名额</span>
              </div>
            </div>

            <!-- 选课按钮 -->
            <div class="action-buttons">
              <el-button
                v-if="!isEnrolled"
                type="primary"
                size="large"
                :loading="enrolling"
                :disabled="availableSeats <= 0"
                @click="enrollCourse"
              >
                <el-icon v-if="!enrolling"><Plus /></el-icon>
                {{ availableSeats <= 0 ? '名额已满' : '立即选课' }}
              </el-button>

              <el-button
                v-else
                type="info"
                size="large"
                disabled
              >
                <el-icon><Check /></el-icon>
                已选修
              </el-button>

              <el-button size="large" @click="goBack">
                返回列表
              </el-button>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 课程详细信息 -->
      <el-row :gutter="20" class="detail-section">
        <el-col :span="16">
          <!-- 课程描述 -->
          <el-card>
            <template #header>
              <span>课程简介</span>
            </template>
            <div class="course-description">
              {{ course.description || '暂无课程描述' }}
            </div>
          </el-card>

          <!-- 先修课程 -->
          <el-card v-if="course.prerequisites && course.prerequisites.length > 0" class="mt-20">
            <template #header>
              <span>先修要求</span>
            </template>
            <div class="prerequisites">
              <el-tag
                v-for="prereq in course.prerequisites"
                :key="prereq"
                :type="hasCompleted(prereq) ? 'success' : 'danger'"
                class="prereq-tag"
              >
                {{ prereq }}
                <el-icon v-if="hasCompleted(prereq)"><Check /></el-icon>
                <el-icon v-else><Close /></el-icon>
              </el-tag>
            </div>
            <el-alert
              v-if="!meetsPrerequisites"
              type="warning"
              :closable="false"
              show-icon
            >
              您尚未完成所有先修课程，可能无法选修此课程
            </el-alert>
          </el-card>
        </el-col>

        <el-col :span="8">
          <!-- 上课信息 -->
          <el-card>
            <template #header>
              <span>上课信息</span>
            </template>
            <div class="schedule-info">
              <div class="info-item">
                <el-icon><Clock /></el-icon>
                <div>
                  <span class="label">上课时间</span>
                  <span class="value">{{ course.schedule || '待定' }}</span>
                </div>
              </div>
              <div class="info-item">
                <el-icon><Location /></el-icon>
                <div>
                  <span class="label">上课地点</span>
                  <span class="value">{{ course.location || '待定' }}</span>
                </div>
              </div>
              <div class="info-item">
                <el-icon><Calendar /></el-icon>
                <div>
                  <span class="label">课程周期</span>
                  <span class="value">{{ course.semester || '本学期' }}</span>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 教师信息 -->
          <el-card class="mt-20">
            <template #header>
              <span>授课教师</span>
            </template>
            <div class="instructor-info">
              <el-avatar :size="60">{{ course.instructor?.charAt(0) }}</el-avatar>
              <div class="instructor-detail">
                <h4>{{ course.instructor }}</h4>
                <p>{{ course.instructor_title || '讲师' }}</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 时间冲突警告 -->
      <el-dialog
        v-model="showConflictDialog"
        title="时间冲突提醒"
        width="400px"
      >
        <el-alert type="error" :closable="false" show-icon>
          <template #title>
            该课程与以下已选课程时间冲突：
          </template>
          <ul class="conflict-list">
            <li v-for="conflict in conflicts" :key="conflict.course_id">
              {{ conflict.name }} ({{ conflict.schedule }})
            </li>
          </ul>
        </el-alert>
        <template #footer>
          <el-button @click="showConflictDialog = false">知道了</el-button>
        </template>
      </el-dialog>
    </template>

    <!-- 空状态 -->
    <el-empty v-else description="课程不存在或已下架">
      <el-button type="primary" @click="goBack">返回课程列表</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Reading, User, Medal, Plus, Check, Close,
  Clock, Location, Calendar
} from '@element-plus/icons-vue'
import request from '@/api/request'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const enrolling = ref(false)
const course = ref(null)
const isEnrolled = ref(false)
const completedCourses = ref([])
const conflicts = ref([])
const showConflictDialog = ref(false)

const defaultCover = 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=400'

// 计算剩余名额
const availableSeats = computed(() => {
  if (!course.value) return 0
  return Math.max(0, course.value.capacity - course.value.current_enrollment)
})

// 检查是否满足先修要求
const meetsPrerequisites = computed(() => {
  if (!course.value?.prerequisites) return true
  return course.value.prerequisites.every(prereq =>
    completedCourses.value.includes(prereq)
  )
})

// 检查是否已完成某先修课程
const hasCompleted = (courseId) => {
  return completedCourses.value.includes(courseId)
}

// 获取课程详情
const fetchCourseDetail = async () => {
  const courseId = route.params.id
  loading.value = true

  try {
    const { data } = await request.get(`/api/v1/courses/${courseId}`)
    // 映射后端字段到前端字段
    course.value = {
      ...data,
      name: data.course_name,
      instructor: data.teacher_name,
      capacity: data.max_students,
      current_enrollment: data.current_students,
      location: data.schedule // 临时使用 schedule 作为上课地点
    }

    // 检查是否已选修
    await checkEnrollmentStatus(courseId)

    // 获取已完成课程（用于先修验证）
    await fetchCompletedCourses()
  } catch (error) {
    // API调用失败时，使用模拟数据
    console.warn('API调用失败，使用模拟数据')

    const mockCourses = {
      'MATH101': {
        id: 'MATH101',
        name: '高等数学',
        code: 'MATH101',
        department_name: '理学院',
        instructor: '张教授',
        credits: 4,
        hours: 64,
        description: '本课程系统介绍高等数学的基本概念、基本理论和基本方法，包括极限、导数、微分、不定积分、定积分等内容。通过本课程的学习，使学生掌握高等数学的基本理论和方法，为后续专业课程的学习奠定基础。',
        capacity: 100,
        current_enrollment: 85,
        semester: '2024春季',
        schedule: '周一 8:00-10:00, 周三 14:00-16:00',
        classroom: '教学楼A-101',
        prerequisites: [],
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-11-01T00:00:00Z'
      },
      'CS101': {
        id: 'CS101',
        name: '计算机基础',
        code: 'CS101',
        department_name: '计算机学院',
        instructor: '李老师',
        credits: 3,
        hours: 48,
        description: '本课程介绍计算机的基本原理和应用，包括计算机硬件、软件、操作系统、编程基础等内容。通过实践教学，帮助学生掌握计算机的基本操作和简单编程技能。',
        capacity: 80,
        current_enrollment: 72,
        semester: '2024春季',
        schedule: '周二 10:00-12:00, 周四 16:00-18:00',
        classroom: '计算机实验室B-201',
        prerequisites: [],
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-11-01T00:00:00Z'
      }
    }

    course.value = mockCourses[courseId] || {
      id: courseId,
      name: '示例课程',
      code: courseId,
      department_name: '计算机学院',
      instructor: '示例教师',
      credits: 3,
      hours: 48,
      description: '这是一个示例课程的详细介绍。',
      capacity: 100,
      current_enrollment: 50,
      semester: '2024春季',
      schedule: '周一 8:00-10:00',
      classroom: '教学楼A-101',
      prerequisites: [],
      status: 'active',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-11-01T00:00:00Z'
    }

    // 模拟选课状态检查
    enrolled.value = false
    canEnroll.value = true
  } finally {
    loading.value = false
  }
}

// 检查选课状态
const checkEnrollmentStatus = async (courseId) => {
  try {
    const { data } = await request.get('/api/v1/enrollments/my-courses')
    const enrolled = data.find(e => e.course_id === courseId)
    isEnrolled.value = !!enrolled
  } catch (error) {
    console.error('检查选课状态失败', error)
  }
}

// 获取已完成课程
const fetchCompletedCourses = async () => {
  try {
    const { data } = await request.get('/api/v1/enrollments/my-courses', {
      params: { status: 'completed' }
    })
    completedCourses.value = data.map(e => e.course_id)
  } catch (error) {
    console.error('获取已完成课程失败', error)
  }
}

// 选课
const enrollCourse = async () => {
  if (!course.value) return

  enrolling.value = true
  try {
    await request.post('/api/v1/enrollments', {
      course_id: course.value.course_id
    })

    ElMessage.success('选课成功！')
    isEnrolled.value = true
    course.value.current_enrollment++
  } catch (error) {
    const detail = error.response?.data?.detail

    // 检查是否是时间冲突
    if (detail?.includes('冲突')) {
      conflicts.value = error.response?.data?.conflicts || []
      showConflictDialog.value = true
    } else {
      ElMessage.error(detail || '选课失败')
    }
  } finally {
    enrolling.value = false
  }
}

// 返回列表
const goBack = () => {
  router.push('/courses')
}

onMounted(() => {
  fetchCourseDetail()
})
</script>

<style scoped lang="scss">
.course-detail {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.loading-container {
  padding: 40px;
}

.course-header {
  margin-bottom: 20px;

  .header-content {
    display: flex;
    gap: 30px;
  }

  .course-cover {
    flex-shrink: 0;
    width: 300px;
    height: 200px;
    border-radius: 8px;
    overflow: hidden;

    .cover-image {
      width: 100%;
      height: 100%;
    }

    .image-placeholder {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f5f7fa;
      color: #c0c4cc;
    }
  }

  .course-info {
    flex: 1;

    .course-title {
      font-size: 24px;
      font-weight: 600;
      margin: 0 0 15px;
    }

    .course-meta {
      display: flex;
      align-items: center;
      gap: 20px;
      margin-bottom: 20px;

      .meta-item {
        display: flex;
        align-items: center;
        gap: 5px;
        color: #606266;
      }
    }

    .course-stats {
      display: flex;
      gap: 40px;
      margin-bottom: 25px;

      .stat-item {
        text-align: center;

        .stat-value {
          display: block;
          font-size: 28px;
          font-weight: 600;
          color: #409eff;

          &.text-danger {
            color: #f56c6c;
          }
        }

        .stat-label {
          font-size: 12px;
          color: #909399;
        }
      }
    }

    .action-buttons {
      display: flex;
      gap: 10px;
    }
  }
}

.detail-section {
  .mt-20 {
    margin-top: 20px;
  }
}

.course-description {
  line-height: 1.8;
  color: #606266;
  white-space: pre-wrap;
}

.prerequisites {
  margin-bottom: 15px;

  .prereq-tag {
    margin-right: 10px;
    margin-bottom: 10px;
  }
}

.schedule-info {
  .info-item {
    display: flex;
    align-items: flex-start;
    gap: 15px;
    padding: 12px 0;
    border-bottom: 1px solid #ebeef5;

    &:last-child {
      border-bottom: none;
    }

    .el-icon {
      font-size: 20px;
      color: #409eff;
      margin-top: 2px;
    }

    .label {
      display: block;
      font-size: 12px;
      color: #909399;
      margin-bottom: 4px;
    }

    .value {
      font-weight: 500;
    }
  }
}

.instructor-info {
  display: flex;
  align-items: center;
  gap: 15px;

  .instructor-detail {
    h4 {
      margin: 0 0 5px;
    }

    p {
      margin: 0;
      font-size: 12px;
      color: #909399;
    }
  }
}

.conflict-list {
  margin: 10px 0 0;
  padding-left: 20px;

  li {
    margin-bottom: 5px;
  }
}

// 响应式
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
  }

  .course-cover {
    width: 100% !important;
  }

  .detail-section {
    .el-col {
      width: 100%;
      max-width: 100%;
    }
  }
}
</style>
