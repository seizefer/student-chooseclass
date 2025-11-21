<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人资料</span>
          <el-button type="primary" @click="toggleEdit">
            {{ isEditing ? '取消' : '编辑' }}
          </el-button>
        </div>
      </template>

      <!-- 头像上传 -->
      <div class="avatar-section">
        <el-upload
          class="avatar-uploader"
          :action="uploadUrl"
          :headers="uploadHeaders"
          :show-file-list="false"
          :on-success="handleAvatarSuccess"
          :before-upload="beforeAvatarUpload"
          :disabled="!isEditing"
        >
          <el-avatar :size="100" :src="userInfo.avatar || defaultAvatar">
            <el-icon v-if="isEditing"><Plus /></el-icon>
          </el-avatar>
        </el-upload>
        <p class="avatar-tip" v-if="isEditing">点击上传头像</p>
      </div>

      <!-- 用户信息表单 -->
      <el-form
        ref="profileForm"
        :model="userInfo"
        :rules="rules"
        label-width="100px"
        :disabled="!isEditing"
      >
        <el-form-item label="学号">
          <el-input v-model="userInfo.student_id" disabled />
        </el-form-item>

        <el-form-item label="姓名" prop="name">
          <el-input v-model="userInfo.name" />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userInfo.email">
            <template #append v-if="!userInfo.email_verified">
              <el-button @click="sendVerification">验证</el-button>
            </template>
          </el-input>
          <el-tag v-if="userInfo.email_verified" type="success" size="small">已验证</el-tag>
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input v-model="userInfo.phone" />
        </el-form-item>

        <el-form-item label="院系">
          <el-select v-model="userInfo.department_id" placeholder="选择院系">
            <el-option
              v-for="dept in departments"
              :key="dept.id"
              :label="dept.name"
              :value="dept.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="入学年份">
          <el-date-picker
            v-model="userInfo.enrollment_year"
            type="year"
            placeholder="选择年份"
          />
        </el-form-item>

        <el-form-item label="账户余额">
          <el-input :value="'¥' + userInfo.balance" disabled />
        </el-form-item>

        <el-form-item v-if="isEditing">
          <el-button type="primary" @click="saveProfile">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 修改密码 -->
    <el-card class="password-card">
      <template #header>
        <span>修改密码</span>
      </template>

      <el-form
        ref="passwordForm"
        :model="passwordData"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="当前密码" prop="current_password">
          <el-input v-model="passwordData.current_password" type="password" show-password />
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordData.new_password" type="password" show-password />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="passwordData.confirm_password" type="password" show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="changePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import request from '@/api/request'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const profileForm = ref(null)
const passwordForm = ref(null)
const isEditing = ref(false)
const departments = ref([])
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 上传配置
const uploadUrl = '/api/v1/upload/avatar'
const uploadHeaders = {
  Authorization: `Bearer ${authStore.token}`
}

// 用户信息
const userInfo = reactive({
  student_id: '',
  name: '',
  email: '',
  phone: '',
  department_id: null,
  enrollment_year: null,
  balance: 0,
  avatar: '',
  email_verified: false
})

// 密码修改
const passwordData = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 密码验证规则
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordData.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  current_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 获取用户信息
const fetchUserInfo = async () => {
  try {
    const { data } = await request.get('/api/v1/students/profile')
    Object.assign(userInfo, data)
  } catch (error) {
    ElMessage.error('获取用户信息失败')
  }
}

// 获取院系列表
const fetchDepartments = async () => {
  try {
    const { data } = await request.get('/api/v1/departments')
    departments.value = data
  } catch (error) {
    console.error('获取院系列表失败', error)
  }
}

// 切换编辑模式
const toggleEdit = () => {
  isEditing.value = !isEditing.value
  if (!isEditing.value) {
    fetchUserInfo() // 取消时重新加载数据
  }
}

// 保存个人资料
const saveProfile = async () => {
  try {
    await profileForm.value.validate()
    await request.put('/api/v1/students/profile', {
      name: userInfo.name,
      email: userInfo.email,
      phone: userInfo.phone,
      department_id: userInfo.department_id
    })
    ElMessage.success('保存成功')
    isEditing.value = false
  } catch (error) {
    if (error !== false) {
      ElMessage.error('保存失败')
    }
  }
}

// 修改密码
const changePassword = async () => {
  try {
    await passwordForm.value.validate()
    await request.put('/api/v1/students/password', {
      current_password: passwordData.current_password,
      new_password: passwordData.new_password
    })
    ElMessage.success('密码修改成功')
    // 清空表单
    passwordData.current_password = ''
    passwordData.new_password = ''
    passwordData.confirm_password = ''
  } catch (error) {
    if (error !== false) {
      ElMessage.error(error.response?.data?.detail || '密码修改失败')
    }
  }
}

// 发送邮箱验证
const sendVerification = async () => {
  try {
    await request.post('/api/v1/auth/send-verification')
    ElMessage.success('验证邮件已发送，请查收')
  } catch (error) {
    ElMessage.error('发送验证邮件失败')
  }
}

// 头像上传成功
const handleAvatarSuccess = (response) => {
  userInfo.avatar = response.url
  ElMessage.success('头像上传成功')
}

// 头像上传前验证
const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB')
    return false
  }
  return true
}

onMounted(() => {
  fetchUserInfo()
  fetchDepartments()
})
</script>

<style scoped lang="scss">
.profile-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.profile-card,
.password-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avatar-section {
  text-align: center;
  margin-bottom: 20px;
}

.avatar-uploader {
  cursor: pointer;
}

.avatar-tip {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}
</style>
