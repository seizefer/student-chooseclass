<!--
登录页面
@version: v1.2.0
@date: 2024-12-06
-->
<template>
  <div class="login-container">
    <div class="login-box">
      <div class="logo-section">
        <el-icon class="logo-icon"><School /></el-icon>
        <h1>在线选课系统</h1>
        <p>欢迎回来，请登录您的账户</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            size="large"
            placeholder="请输入学号或管理员账号"
            prefix-icon="User"
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            size="large"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <div class="form-options">
            <el-checkbox v-model="rememberMe">记住我</el-checkbox>
            <el-link type="primary" @click="showForgotPassword">忘记密码？</el-link>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="authStore.loading"
            class="login-btn"
            @click="handleLogin"
          >
            <span v-if="!authStore.loading">登录</span>
            <span v-else>登录中...</span>
          </el-button>
        </el-form-item>

        <el-form-item class="register-link">
          <span>还没有账户？</span>
          <el-link type="primary" @click="$router.push('/register')">立即注册</el-link>
        </el-form-item>
      </el-form>
    </div>

    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import { School } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 表单引用
const loginFormRef = ref()

// 表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 记住我选项
const rememberMe = ref(false)

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ]
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    // 验证表单
    await loginFormRef.value.validate()
    
    // 调用登录API
    const result = await authStore.login({
      username: loginForm.username.trim(),
      password: loginForm.password
    })
    
    if (result.success) {
      // 如果选择了记住我，保存用户名
      if (rememberMe.value) {
        localStorage.setItem('rememberedUsername', loginForm.username)
      } else {
        localStorage.removeItem('rememberedUsername')
      }

      // 登录成功，跳转到仪表盘页面
      const redirect = router.currentRoute.value.query.redirect
      const targetPath = (redirect && redirect !== '/login' && redirect !== '/register')
        ? redirect
        : '/app/dashboard'

      console.log('🔐 登录成功!')
      console.log('📊 用户信息:', result.data.user)
      console.log('🎫 Token:', result.data.access_token ? '已设置' : '未设置')
      console.log('🎯 准备跳转到:', targetPath)
      console.log('🔍 当前认证状态:', authStore.isAuthenticated)

      try {
        await router.push(targetPath)
        console.log('✅ 跳转完成，当前路由:', router.currentRoute.value.path)
        console.log('📍 最终URL:', window.location.href)
      } catch (navigationError) {
        console.error('❌ 导航错误:', navigationError)
        // 如果导航失败，强制跳转
        console.log('🔄 尝试强制跳转...')
        router.replace(targetPath)
      }
    } else {
      // 登录失败，抛出错误让用户看到
      throw new Error(result.message || '登录失败')
    }
  } catch (error) {
    console.error('登录失败:', error)
  }
}

// 显示忘记密码
const showForgotPassword = () => {
  ElMessage.info('请联系管理员重置密码')
}

// 组件挂载时恢复记住的用户名
onMounted(() => {
  const rememberedUsername = localStorage.getItem('rememberedUsername')
  if (rememberedUsername) {
    loginForm.username = rememberedUsername
    rememberMe.value = true
  }
})
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.login-box {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  z-index: 10;
  
  @media (max-width: 480px) {
    margin: 20px;
    padding: 30px 20px;
  }
}

.logo-section {
  text-align: center;
  margin-bottom: 40px;
  
  .logo-icon {
    font-size: 48px;
    color: var(--primary-color);
    margin-bottom: 15px;
  }
  
  h1 {
    font-size: 28px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 10px;
  }
  
  p {
    color: var(--text-secondary);
    font-size: 14px;
    margin: 0;
  }
}

.login-form {
  .el-form-item {
    margin-bottom: 24px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  .form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    font-size: 14px;
  }
  
  .login-btn {
    width: 100%;
    height: 44px;
    font-size: 16px;
    font-weight: 500;
    border-radius: 8px;
  }
  
  .register-link {
    text-align: center;
    font-size: 14px;
    
    span {
      color: var(--text-secondary);
      margin-right: 8px;
    }
  }
}

.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
  
  .circle {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
    animation: float 6s ease-in-out infinite;
    
    &.circle-1 {
      width: 120px;
      height: 120px;
      top: 10%;
      left: 10%;
      animation-delay: 0s;
    }
    
    &.circle-2 {
      width: 80px;
      height: 80px;
      top: 70%;
      right: 10%;
      animation-delay: 2s;
    }
    
    &.circle-3 {
      width: 60px;
      height: 60px;
      top: 30%;
      right: 20%;
      animation-delay: 4s;
    }
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  33% {
    transform: translateY(-20px) rotate(5deg);
  }
  66% {
    transform: translateY(10px) rotate(-5deg);
  }
}

// Element Plus样式覆盖
:deep(.el-input__wrapper) {
  padding: 12px 16px;
  border-radius: 8px;
}

:deep(.el-checkbox__label) {
  font-size: 14px;
}
</style> 