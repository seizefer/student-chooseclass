<!--
课程列表页面
@version: v1.1.0
@date: 2024-11-21
@changelog:
  v1.1.0: 添加搜索筛选、分页、API调用
  v1.0.0: 初始版本
-->
<template>
  <div class="course-list-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>📚 课程列表</h1>
      <p>浏览所有可选课程，支持搜索和筛选</p>
    </div>

    <!-- 搜索筛选区 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="搜索">
          <el-input
            v-model="filters.search"
            placeholder="课程名称/教师/课程号"
            clearable
            :prefix-icon="Search"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="院系">
          <el-select v-model="filters.departmentId" placeholder="全部院系" clearable>
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="学期">
          <el-select v-model="filters.semester" placeholder="全部学期" clearable>
            <el-option label="2024春季" value="2024春季" />
            <el-option label="2024秋季" value="2024秋季" />
            <el-option label="2025春季" value="2025春季" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部状态" clearable>
            <el-option label="开放选课" value="active" />
            <el-option label="已结束" value="closed" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 课程列表 -->
    <div v-loading="loading" class="course-content">
      <!-- 课程卡片网格 -->
      <div v-if="courses.length > 0" class="course-grid">
        <div
          v-for="course in courses"
          :key="course.course_id"
          class="course-card"
        >
          <div class="course-info">
            <div class="course-header">
              <h3>{{ course.course_name }}</h3>
              <el-tag :type="course.status === 'active' ? 'success' : 'info'" size="small">
                {{ course.status === 'active' ? '可选' : '已结束' }}
              </el-tag>
            </div>
            <p class="course-code">
              <el-icon><Document /></el-icon>
              {{ course.course_id }}
            </p>
            <p class="course-teacher">
              <el-icon><User /></el-icon>
              {{ course.teacher_name || '待定' }}
            </p>
            <p class="course-schedule">
              <el-icon><Clock /></el-icon>
              {{ course.schedule || '待安排' }}
            </p>
            <p class="course-department">
              <el-icon><School /></el-icon>
              {{ course.department_name || '未知院系' }}
            </p>
            <div class="course-stats">
              <span class="stat-item">
                <el-icon><Medal /></el-icon>
                {{ course.credits }} 学分
              </span>
              <span class="stat-item">
                <el-icon><UserFilled /></el-icon>
                {{ course.current_students }}/{{ course.max_students }}
              </span>
            </div>
          </div>

          <div class="course-actions">
            <el-button
              type="primary"
              size="small"
              :disabled="course.current_students >= course.max_students || course.status !== 'active'"
              @click="handleEnroll(course)"
            >
              <el-icon><Plus /></el-icon>
              {{ course.current_students >= course.max_students ? '已满' : '选课' }}
            </el-button>
            <el-button size="small" @click="handleViewDetail(course)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else-if="!loading" class="empty-state">
        <el-empty description="暂无课程信息">
          <el-button type="primary" @click="fetchCourses">刷新列表</el-button>
        </el-empty>
      </div>

      <!-- 分页 -->
      <div v-if="total > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[12, 24, 48, 96]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Search, Refresh, Plus, View, Document,
  User, Clock, Medal, UserFilled, School
} from '@element-plus/icons-vue'
import request from '@/api/request'

const router = useRouter()

// 数据状态
const loading = ref(false)
const courses = ref([])
const total = ref(0)
const departments = ref([
  { id: 'CS', name: '计算机学院' },
  { id: 'MATH', name: '理学院' },
  { id: 'ENG', name: '外国语学院' },
  { id: 'ECO', name: '经济管理学院' },
  { id: 'ART', name: '艺术学院' }
])

// 筛选条件
const filters = reactive({
  search: '',
  departmentId: '',
  semester: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 12
})

// 获取课程列表
const fetchCourses = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }

    // 添加筛选条件
    if (filters.search) params.search = filters.search
    if (filters.departmentId) params.department_id = filters.departmentId
    if (filters.semester) params.semester = filters.semester
    if (filters.status) params.status = filters.status

    const { data } = await request.get('/api/v1/courses', { params })

    courses.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.warn('API调用失败，使用模拟数据')
    // 模拟数据
    courses.value = [
      {
        course_id: 'MATH101',
        course_name: '高等数学',
        teacher_name: '张教授',
        department_name: '理学院',
        schedule: '周一 8:00-10:00, 周三 14:00-16:00',
        credits: 4,
        max_students: 100,
        current_students: 85,
        status: 'active'
      },
      {
        course_id: 'CS101',
        course_name: '计算机基础',
        teacher_name: '李老师',
        department_name: '计算机学院',
        schedule: '周二 10:00-12:00, 周四 16:00-18:00',
        credits: 3,
        max_students: 80,
        current_students: 72,
        status: 'active'
      },
      {
        course_id: 'ENG101',
        course_name: '大学英语',
        teacher_name: '王教授',
        department_name: '外国语学院',
        schedule: '周二 14:00-16:00',
        credits: 3,
        max_students: 60,
        current_students: 58,
        status: 'active'
      },
      {
        course_id: 'CS201',
        course_name: '数据结构',
        teacher_name: '赵老师',
        department_name: '计算机学院',
        schedule: '周四 10:00-12:00',
        credits: 4,
        max_students: 50,
        current_students: 50,
        status: 'active'
      }
    ]
    total.value = courses.value.length
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchCourses()
}

// 重置筛选
const resetFilters = () => {
  filters.search = ''
  filters.departmentId = ''
  filters.semester = ''
  filters.status = ''
  pagination.page = 1
  fetchCourses()
}

// 分页大小改变
const handleSizeChange = () => {
  pagination.page = 1
  fetchCourses()
}

// 页码改变
const handlePageChange = () => {
  fetchCourses()
}

// 选课
const handleEnroll = async (course) => {
  try {
    await request.post('/api/v1/enrollments', {
      course_id: course.course_id
    })
    ElMessage.success(`成功选修课程：${course.course_name}`)
    course.current_students++
  } catch (error) {
    const message = error.response?.data?.detail || '选课失败，请稍后重试'
    ElMessage.error(message)
  }
}

// 查看详情
const handleViewDetail = (course) => {
  router.push(`/courses/${course.course_id}`)
}

onMounted(() => {
  fetchCourses()
})
</script>

<style lang="scss" scoped>
.course-list-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
  text-align: center;

  h1 {
    color: #2c3e50;
    margin-bottom: 8px;
    font-size: 28px;
  }

  p {
    color: #909399;
    font-size: 14px;
  }
}

.filter-card {
  margin-bottom: 20px;

  .filter-form {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;

    .el-form-item {
      margin-bottom: 0;
    }
  }
}

.course-content {
  min-height: 400px;
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.course-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1px solid #ebeef5;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
  }
}

.course-info {
  margin-bottom: 16px;

  .course-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;

    h3 {
      margin: 0;
      font-size: 18px;
      color: #303133;
      flex: 1;
    }
  }

  p {
    display: flex;
    align-items: center;
    gap: 6px;
    margin: 8px 0;
    font-size: 13px;
    color: #606266;

    .el-icon {
      color: #909399;
    }

    &.course-code {
      color: #409eff;
      font-weight: 500;
    }
  }

  .course-stats {
    display: flex;
    gap: 16px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #f0f0f0;

    .stat-item {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 13px;
      color: #909399;
    }
  }
}

.course-actions {
  display: flex;
  gap: 10px;

  .el-button {
    flex: 1;
  }
}

.empty-state {
  padding: 60px 20px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

@media (max-width: 768px) {
  .course-grid {
    grid-template-columns: 1fr;
  }

  .filter-form {
    flex-direction: column;

    .el-form-item {
      width: 100%;
    }
  }

  .course-actions {
    flex-direction: column;
  }
}
</style>
