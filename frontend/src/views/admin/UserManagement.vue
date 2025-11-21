<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="showAddDialog">添加用户</el-button>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <div class="filter-section">
        <el-input
          v-model="searchQuery"
          placeholder="搜索学号/姓名"
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
        <el-select v-model="filterStatus" placeholder="状态" clearable>
          <el-option label="正常" value="active" />
          <el-option label="禁用" value="disabled" />
        </el-select>
        <el-button type="primary" @click="fetchUsers">搜索</el-button>
      </div>

      <!-- 用户列表 -->
      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="student_id" label="学号" width="120" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="department_name" label="院系" width="120" />
        <el-table-column label="余额" width="100">
          <template #default="{ row }">
            ¥{{ row.balance }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="editUser(row)">编辑</el-button>
            <el-button
              size="small"
              :type="row.status === 'active' ? 'warning' : 'success'"
              @click="toggleStatus(row)"
            >
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-popconfirm
              title="确定要删除该用户吗?"
              @confirm="deleteUser(row.student_id)"
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
          @size-change="fetchUsers"
          @current-change="fetchUsers"
        />
      </div>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑用户' : '添加用户'"
      width="500px"
    >
      <el-form
        ref="userForm"
        :model="userFormData"
        :rules="userRules"
        label-width="80px"
      >
        <el-form-item label="学号" prop="student_id">
          <el-input v-model="userFormData.student_id" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="userFormData.name" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userFormData.email" />
        </el-form-item>
        <el-form-item label="院系" prop="department_id">
          <el-select v-model="userFormData.department_id" style="width: 100%">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="userFormData.password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'

const loading = ref(false)
const users = ref([])
const departments = ref([])
const searchQuery = ref('')
const filterDepartment = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const userForm = ref(null)

const userFormData = reactive({
  student_id: '',
  name: '',
  email: '',
  department_id: null,
  password: ''
})

const userRules = {
  student_id: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  department_id: [{ required: true, message: '请选择院系', trigger: 'change' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 获取用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      query: searchQuery.value,
      department_id: filterDepartment.value,
      status: filterStatus.value
    }
    const { data } = await request.get('/api/v1/students/list', { params })
    users.value = data.items || data
    total.value = data.total || data.length
  } catch (error) {
    // API调用失败时，使用模拟数据
    console.warn('API调用失败，使用模拟数据')
    const mockUsers = [
      {
        student_id: '2021001',
        name: '张三',
        email: 'zhangsan@example.com',
        department_name: '计算机学院',
        balance: 1000.50,
        status: 'active',
        grade: 2021
      },
      {
        student_id: '2021002',
        name: '李四',
        email: 'lisi@example.com',
        department_name: '商学院',
        balance: 850.00,
        status: 'active',
        grade: 2021
      },
      {
        student_id: '2021003',
        name: '王五',
        email: 'wangwu@example.com',
        department_name: '文学院',
        balance: 1200.25,
        status: 'active',
        grade: 2021
      },
      {
        student_id: '2021004',
        name: '赵六',
        email: 'zhaoliu@example.com',
        department_name: '理学院',
        balance: 0.00,
        status: 'disabled',
        grade: 2021
      }
    ]

    // 应用搜索和筛选
    let filteredUsers = mockUsers

    if (searchQuery.value) {
      filteredUsers = filteredUsers.filter(user =>
        user.student_id.includes(searchQuery.value) ||
        user.name.includes(searchQuery.value)
      )
    }

    if (filterDepartment.value) {
      filteredUsers = filteredUsers.filter(user =>
        user.department_name.includes(filterDepartment.value)
      )
    }

    if (filterStatus.value) {
      filteredUsers = filteredUsers.filter(user =>
        user.status === filterStatus.value
      )
    }

    // 分页
    const startIndex = (currentPage.value - 1) * pageSize.value
    const endIndex = startIndex + pageSize.value
    users.value = filteredUsers.slice(startIndex, endIndex)
    total.value = filteredUsers.length
  } finally {
    loading.value = false
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
  Object.assign(userFormData, {
    student_id: '',
    name: '',
    email: '',
    department_id: null,
    password: ''
  })
  dialogVisible.value = true
}

// 编辑用户
const editUser = (user) => {
  isEdit.value = true
  Object.assign(userFormData, {
    student_id: user.student_id,
    name: user.name,
    email: user.email,
    department_id: user.department_id,
    password: ''
  })
  dialogVisible.value = true
}

// 保存用户
const saveUser = async () => {
  try {
    await userForm.value.validate()
    if (isEdit.value) {
      await request.put(`/api/v1/students/${userFormData.student_id}`, userFormData)
      ElMessage.success('更新成功')
    } else {
      await request.post('/api/v1/auth/register', userFormData)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    fetchUsers()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

// 切换状态
const toggleStatus = async (user) => {
  try {
    const newStatus = user.status === 'active' ? 'disabled' : 'active'
    await request.put(`/api/v1/students/${user.student_id}/status`, {
      status: newStatus
    })
    ElMessage.success('状态更新成功')
    fetchUsers()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 删除用户
const deleteUser = async (studentId) => {
  try {
    await request.delete(`/api/v1/students/${studentId}`)
    ElMessage.success('删除成功')
    fetchUsers()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchUsers()
  fetchDepartments()
})
</script>

<style scoped lang="scss">
.user-management {
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
