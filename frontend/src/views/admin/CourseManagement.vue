<template>
  <div class="course-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>课程管理</span>
          <el-button type="primary" @click="showAddDialog">添加课程</el-button>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <div class="filter-section">
        <el-input
          v-model="searchQuery"
          placeholder="搜索课程名称"
          style="width: 200px"
          clearable
        />
        <el-select v-model="filterDepartment" placeholder="选择院系" clearable>
          <el-option
            v-for="dept in departments"
            :key="dept.id"
            :label="dept.name"
            :value="dept.id"
          />
        </el-select>
        <el-button type="primary" @click="fetchCourses">搜索</el-button>
      </div>

      <!-- 课程列表 -->
      <el-table :data="courses" v-loading="loading" stripe>
        <el-table-column prop="course_id" label="课程号" width="120" />
        <el-table-column prop="name" label="课程名称" />
        <el-table-column prop="instructor" label="教师" width="100" />
        <el-table-column prop="credits" label="学分" width="80" />
        <el-table-column label="容量" width="100">
          <template #default="{ row }">
            {{ row.current_enrollment }}/{{ row.capacity }}
          </template>
        </el-table-column>
        <el-table-column prop="schedule" label="上课时间" show-overflow-tooltip />
        <el-table-column prop="location" label="地点" width="100" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="editCourse(row)">编辑</el-button>
            <el-popconfirm
              title="确定要删除该课程吗?"
              @confirm="deleteCourse(row.course_id)"
            >
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchCourses"
          @current-change="fetchCourses"
        />
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑课程' : '添加课程'"
      width="600px"
    >
      <el-form
        ref="courseForm"
        :model="courseFormData"
        :rules="courseRules"
        label-width="100px"
      >
        <el-form-item label="课程号" prop="course_id">
          <el-input v-model="courseFormData.course_id" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="courseFormData.name" />
        </el-form-item>
        <el-form-item label="院系" prop="department_id">
          <el-select v-model="courseFormData.department_id" style="width: 100%">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="教师" prop="instructor">
          <el-input v-model="courseFormData.instructor" />
        </el-form-item>
        <el-form-item label="学分" prop="credits">
          <el-input-number v-model="courseFormData.credits" :min="1" :max="10" />
        </el-form-item>
        <el-form-item label="容量" prop="capacity">
          <el-input-number v-model="courseFormData.capacity" :min="1" :max="500" />
        </el-form-item>
        <el-form-item label="上课时间" prop="schedule">
          <el-input v-model="courseFormData.schedule" placeholder="如: 周一 8:00-9:40" />
        </el-form-item>
        <el-form-item label="上课地点" prop="location">
          <el-input v-model="courseFormData.location" />
        </el-form-item>
        <el-form-item label="课程描述">
          <el-input
            v-model="courseFormData.description"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="先修课程">
          <el-select
            v-model="courseFormData.prerequisites"
            multiple
            placeholder="选择先修课程"
            style="width: 100%"
          >
            <el-option
              v-for="course in allCourses"
              :key="course.course_id"
              :label="course.name"
              :value="course.course_id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCourse">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const loading = ref(false)
const courses = ref([])
const allCourses = ref([])
const departments = ref([])
const searchQuery = ref('')
const filterDepartment = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const courseForm = ref(null)

const courseFormData = reactive({
  course_id: '',
  name: '',
  department_id: null,
  instructor: '',
  credits: 3,
  capacity: 50,
  schedule: '',
  location: '',
  description: '',
  prerequisites: []
})

const courseRules = {
  course_id: [{ required: true, message: '请输入课程号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  department_id: [{ required: true, message: '请选择院系', trigger: 'change' }],
  instructor: [{ required: true, message: '请输入教师姓名', trigger: 'blur' }],
  credits: [{ required: true, message: '请输入学分', trigger: 'blur' }],
  capacity: [{ required: true, message: '请输入容量', trigger: 'blur' }]
}

// 获取课程列表
const fetchCourses = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      query: searchQuery.value,
      department_id: filterDepartment.value
    }
    const { data } = await request.get('/api/v1/courses', { params })
    courses.value = data.items || data
    total.value = data.total || data.length
  } catch (error) {
    ElMessage.error('获取课程列表失败')
  } finally {
    loading.value = false
  }
}

// 获取所有课程（用于先修课程选择）
const fetchAllCourses = async () => {
  try {
    const { data } = await request.get('/api/v1/courses', {
      params: { page_size: 1000 }
    })
    allCourses.value = data.items || data
  } catch (error) {
    console.error('获取课程失败', error)
  }
}

// 获取院系列表
const fetchDepartments = async () => {
  try {
    const { data } = await request.get('/api/v1/departments')
    departments.value = data
  } catch (error) {
    console.error('获取院系失败', error)
  }
}

// 显示添加对话框
const showAddDialog = () => {
  isEdit.value = false
  Object.assign(courseFormData, {
    course_id: '',
    name: '',
    department_id: null,
    instructor: '',
    credits: 3,
    capacity: 50,
    schedule: '',
    location: '',
    description: '',
    prerequisites: []
  })
  dialogVisible.value = true
}

// 编辑课程
const editCourse = (course) => {
  isEdit.value = true
  Object.assign(courseFormData, {
    course_id: course.course_id,
    name: course.name,
    department_id: course.department_id,
    instructor: course.instructor,
    credits: course.credits,
    capacity: course.capacity,
    schedule: course.schedule,
    location: course.location,
    description: course.description,
    prerequisites: course.prerequisites || []
  })
  dialogVisible.value = true
}

// 保存课程
const saveCourse = async () => {
  try {
    await courseForm.value.validate()
    if (isEdit.value) {
      await request.put(`/api/v1/courses/${courseFormData.course_id}`, courseFormData)
      ElMessage.success('更新成功')
    } else {
      await request.post('/api/v1/courses', courseFormData)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchCourses()
    fetchAllCourses()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

// 删除课程
const deleteCourse = async (courseId) => {
  try {
    await request.delete(`/api/v1/courses/${courseId}`)
    ElMessage.success('删除成功')
    fetchCourses()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchCourses()
  fetchAllCourses()
  fetchDepartments()
})
</script>

<style scoped lang="scss">
.course-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-section {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
