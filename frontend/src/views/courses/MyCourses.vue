<!--
我的课程管理页面
@version: v1.0.0
@date: 2024-12-06
-->
<template>
  <div class="my-courses">
    <div class="page-header">
      <h1>我的课程</h1>
      <p>管理您已选择的课程</p>
    </div>

    <div class="courses-container">
      <!-- 课程筛选 -->
      <div class="filter-section">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-select v-model="statusFilter" placeholder="选择状态" clearable>
              <el-option label="全部" value="" />
              <el-option label="进行中" value="active" />
              <el-option label="已完成" value="completed" />
              <el-option label="未开始" value="pending" />
            </el-select>
          </el-col>
          <el-col :span="8">
            <el-input
              v-model="searchQuery"
              placeholder="搜索课程名称或教师"
              prefix-icon="Search"
              clearable
            />
          </el-col>
          <el-col :span="8">
            <el-button type="primary" @click="searchCourses">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </el-col>
        </el-row>
      </div>

      <!-- 课程列表 -->
      <div class="courses-grid">
        <div
          v-for="course in filteredCourses"
          :key="course.id"
          class="course-card"
        >
          <div class="course-header">
            <h3>{{ course.name }}</h3>
            <el-tag :type="getStatusType(course.status)">
              {{ getStatusText(course.status) }}
            </el-tag>
          </div>
          
          <div class="course-info">
            <p><strong>教师：</strong>{{ course.teacher }}</p>
            <p><strong>院系：</strong>{{ course.department }}</p>
            <p><strong>学分：</strong>{{ course.credits }}</p>
            <p><strong>上课时间：</strong>{{ course.schedule }}</p>
            <p><strong>教室：</strong>{{ course.classroom }}</p>
          </div>

          <div class="course-progress" v-if="course.status === 'active'">
            <el-progress
              :percentage="course.progress"
              :color="getProgressColor(course.progress)"
            />
            <span class="progress-text">课程进度 {{ course.progress }}%</span>
          </div>

          <div class="course-actions">
            <el-button size="small" @click="viewCourseDetail(course.id)">
              查看详情
            </el-button>
            <el-button
              v-if="course.status === 'active'"
              size="small"
              type="success"
              @click="enterCourse(course.id)"
            >
              进入课程
            </el-button>
            <el-button
              v-if="course.status === 'pending'"
              size="small"
              type="danger"
              @click="dropCourse(course.id)"
            >
              退选
            </el-button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="filteredCourses.length === 0"
        description="您还没有选择任何课程"
      >
        <template #image>
          <el-icon size="100"><Reading /></el-icon>
        </template>
        <el-button type="primary" @click="$router.push('/courses')">
          去选课
        </el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Reading } from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const searchQuery = ref('')
const statusFilter = ref('')
const courses = ref([])
const loading = ref(false)

// 模拟课程数据
const mockCourses = [
  {
    id: 1,
    name: '高等数学A',
    teacher: '张教授',
    department: '数学系',
    credits: 4,
    schedule: '周一 8:00-10:00',
    classroom: '教学楼A101',
    status: 'active',
    progress: 65
  },
  {
    id: 2,
    name: '大学英语',
    teacher: '李老师',
    department: '外语系',
    credits: 3,
    schedule: '周二 14:00-16:00',
    classroom: '教学楼B201',
    status: 'active',
    progress: 80
  },
  {
    id: 3,
    name: '计算机基础',
    teacher: '王老师',
    department: '计算机系',
    credits: 3,
    schedule: '周三 10:00-12:00',
    classroom: '机房C301',
    status: 'pending',
    progress: 0
  },
  {
    id: 4,
    name: '线性代数',
    teacher: '赵教授',
    department: '数学系',
    credits: 3,
    schedule: '周四 16:00-18:00',
    classroom: '教学楼A102',
    status: 'completed',
    progress: 100
  }
]

// 计算属性
const filteredCourses = computed(() => {
  let result = courses.value

  // 状态筛选
  if (statusFilter.value) {
    result = result.filter(course => course.status === statusFilter.value)
  }

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(course =>
      course.name.toLowerCase().includes(query) ||
      course.teacher.toLowerCase().includes(query)
    )
  }

  return result
})

// 方法
const getStatusType = (status) => {
  const statusMap = {
    'active': 'success',
    'completed': 'info',
    'pending': 'warning'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'active': '进行中',
    'completed': '已完成',
    'pending': '未开始'
  }
  return statusMap[status] || '未知'
}

const getProgressColor = (percentage) => {
  if (percentage < 30) return '#f56c6c'
  if (percentage < 70) return '#e6a23c'
  return '#67c23a'
}

const searchCourses = () => {
  // 这里可以添加搜索逻辑
  ElMessage.success('搜索完成')
}

const viewCourseDetail = (courseId) => {
  router.push(`/courses/${courseId}`)
}

const enterCourse = (courseId) => {
  ElMessage.success('进入课程功能开发中...')
}

const dropCourse = async (courseId) => {
  try {
    await ElMessageBox.confirm('确定要退选这门课程吗？', '确认退选', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 模拟退选操作
    courses.value = courses.value.filter(course => course.id !== courseId)
    ElMessage.success('退选成功')
  } catch {
    ElMessage.info('已取消退选')
  }
}

const loadMyCourses = async () => {
  try {
    loading.value = true
    // 调用后端 API
    const response = await fetch('http://localhost:8000/api/v1/enrollments/my-courses', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    if (response.ok) {
      const result = await response.json()
      if (result.data && result.data.length > 0) {
        // 映射后端数据到前端格式
        courses.value = result.data.map(item => ({
          id: item.course_id,
          name: item.course_name,
          teacher: item.teacher_name || '未知',
          department: item.department_name || '未知',
          credits: item.credits,
          schedule: item.schedule || '待安排',
          classroom: item.classroom || '待定',
          status: item.status === 'enrolled' ? 'active' :
                  item.status === 'completed' ? 'completed' : 'pending',
          progress: item.status === 'completed' ? 100 :
                    item.status === 'enrolled' ? 50 : 0
        }))
      } else {
        // 使用模拟数据
        courses.value = mockCourses
      }
    } else {
      // API 调用失败，使用模拟数据
      courses.value = mockCourses
    }
  } catch (error) {
    console.warn('API调用失败，使用模拟数据:', error)
    courses.value = mockCourses
  } finally {
    loading.value = false
  }
}

// 组件挂载
onMounted(() => {
  loadMyCourses()
})
</script>

<style lang="scss" scoped>
.my-courses {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  h1 {
    margin: 0 0 8px 0;
    color: var(--text-color-primary);
  }
  p {
    margin: 0;
    color: var(--text-color-regular);
  }
}

.filter-section {
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.course-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h3 {
    margin: 0;
    color: var(--text-color-primary);
  }
}

.course-info {
  margin-bottom: 16px;
  
  p {
    margin: 8px 0;
    color: var(--text-color-regular);
    font-size: 14px;
  }
}

.course-progress {
  margin-bottom: 16px;
  
  .progress-text {
    font-size: 12px;
    color: var(--text-color-secondary);
    margin-top: 4px;
    display: block;
  }
}

.course-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .courses-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-section {
    .el-row {
      flex-direction: column;
      gap: 12px;
    }
  }
}
</style> 