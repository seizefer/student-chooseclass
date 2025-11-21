<!--
欢迎页面 - 用于测试前端连接
@version: v1.0.0  
@date: 2024-12-06
-->
<template>
  <div class="welcome-container">
    <div class="welcome-card">
      <h1>🎉 欢迎使用在线大学生选课系统</h1>
      <p class="subtitle">前端已成功启动并连接！</p>
      
      <div class="features">
        <div class="feature-item">
          <el-icon><Star /></el-icon>
          <span>课程管理</span>
        </div>
        <div class="feature-item">
          <el-icon><User /></el-icon>
          <span>好友系统</span>
        </div>
        <div class="feature-item">
          <el-icon><ChatLineRound /></el-icon>
          <span>消息通信</span>
        </div>
        <div class="feature-item">
          <el-icon><Money /></el-icon>
          <span>转账功能</span>
        </div>
      </div>
      
      <div class="actions">
        <el-button type="primary" size="large" @click="goToLogin">
          <el-icon><Right /></el-icon>
          立即登录
        </el-button>
        <el-button size="large" @click="goToRegister">
          注册账户
        </el-button>
      </div>
      
      <div class="status">
        <el-tag type="success">前端状态: 正常运行</el-tag>
        <el-tag type="info">版本: v1.2.0</el-tag>
        <el-tag type="warning">后端状态: {{ backendStatus }}</el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Star, User, ChatLineRound, Money, Right } from '@element-plus/icons-vue'

const router = useRouter()
const backendStatus = ref('检测中...')

// 检测后端状态
const checkBackendStatus = async () => {
  try {
    const response = await fetch('http://localhost:8000/health')
    if (response.ok) {
      backendStatus.value = '正常连接'
    } else {
      backendStatus.value = '连接异常'
    }
  } catch (error) {
    backendStatus.value = '无法连接'
  }
}

// 页面跳转
const goToLogin = () => {
  router.push('/login')
}

const goToRegister = () => {
  router.push('/register')
}

onMounted(() => {
  checkBackendStatus()
})
</script>

<style lang="scss" scoped>
.welcome-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.welcome-card {
  background: white;
  border-radius: 20px;
  padding: 60px 40px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 100%;
}

h1 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 2.5em;
  font-weight: 600;
}

.subtitle {
  color: #7f8c8d;
  font-size: 1.2em;
  margin-bottom: 40px;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px;
  border-radius: 10px;
  background: #f8f9fa;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
  }
  
  .el-icon {
    font-size: 2em;
    color: #409eff;
  }
  
  span {
    font-weight: 500;
    color: #2c3e50;
  }
}

.actions {
  margin-bottom: 30px;
  
  .el-button {
    margin: 0 10px;
    padding: 12px 30px;
  }
}

.status {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .welcome-card {
    padding: 40px 20px;
  }
  
  h1 {
    font-size: 2em;
  }
  
  .features {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style> 