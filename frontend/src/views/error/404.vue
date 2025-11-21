<!--
404错误页面
@version: v1.2.0
@date: 2024-12-06
-->
<template>
  <div class="error-page">
    <div class="error-content">
      <div class="error-illustration">
        <div class="error-number">404</div>
        <div class="error-icon">
          <el-icon><Warning /></el-icon>
        </div>
      </div>
      
      <div class="error-text">
        <h1>页面不存在</h1>
        <p>抱歉，您访问的页面不存在或已被删除</p>
      </div>
      
      <div class="error-actions">
        <el-button type="primary" size="large" @click="goHome">
          <el-icon><House /></el-icon>
          返回首页
        </el-button>
        <el-button size="large" @click="goBack">
          <el-icon><Back /></el-icon>
          返回上页
        </el-button>
      </div>
    </div>
    
    <!-- 背景装饰 -->
    <div class="background">
      <div class="cloud cloud-1"></div>
      <div class="cloud cloud-2"></div>
      <div class="cloud cloud-3"></div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Warning, House, Back } from '@element-plus/icons-vue'

const router = useRouter()

// 返回首页
const goHome = () => {
  router.push('/')
}

// 返回上一页
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}
</script>

<style lang="scss" scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  position: relative;
  overflow: hidden;
}

.error-content {
  text-align: center;
  z-index: 10;
  color: white;
}

.error-illustration {
  position: relative;
  margin-bottom: 40px;
  
  .error-number {
    font-size: 150px;
    font-weight: bold;
    line-height: 1;
    text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    
    @media (max-width: 768px) {
      font-size: 100px;
    }
  }
  
  .error-icon {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 60px;
    color: rgba(255, 255, 255, 0.8);
    animation: bounce 2s infinite;
    
    @media (max-width: 768px) {
      font-size: 40px;
    }
  }
}

.error-text {
  margin-bottom: 40px;
  
  h1 {
    font-size: 36px;
    font-weight: 600;
    margin: 0 0 15px;
    
    @media (max-width: 768px) {
      font-size: 24px;
    }
  }
  
  p {
    font-size: 18px;
    opacity: 0.9;
    margin: 0;
    
    @media (max-width: 768px) {
      font-size: 16px;
    }
  }
}

.error-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: center;
    gap: 15px;
  }
  
  .el-button {
    padding: 12px 24px;
    font-size: 16px;
    border-radius: 8px;
    
    .el-icon {
      margin-right: 8px;
    }
  }
}

.background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  
  .cloud {
    position: absolute;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50px;
    animation: float 20s infinite linear;
    
    &::before {
      content: '';
      position: absolute;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 50px;
    }
    
    &::after {
      content: '';
      position: absolute;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 50px;
    }
    
    &.cloud-1 {
      width: 100px;
      height: 40px;
      top: 20%;
      left: -150px;
      animation-duration: 25s;
      
      &::before {
        width: 50px;
        height: 50px;
        top: -25px;
        left: 10px;
      }
      
      &::after {
        width: 60px;
        height: 20px;
        top: -10px;
        right: 10px;
      }
    }
    
    &.cloud-2 {
      width: 80px;
      height: 30px;
      top: 60%;
      left: -120px;
      animation-duration: 30s;
      animation-delay: -10s;
      
      &::before {
        width: 40px;
        height: 40px;
        top: -20px;
        left: 15px;
      }
      
      &::after {
        width: 50px;
        height: 15px;
        top: -5px;
        right: 15px;
      }
    }
    
    &.cloud-3 {
      width: 120px;
      height: 50px;
      top: 40%;
      left: -180px;
      animation-duration: 35s;
      animation-delay: -20s;
      
      &::before {
        width: 60px;
        height: 60px;
        top: -30px;
        left: 20px;
      }
      
      &::after {
        width: 70px;
        height: 25px;
        top: -12px;
        right: 20px;
      }
    }
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translate(-50%, -50%) translateY(0);
  }
  40% {
    transform: translate(-50%, -50%) translateY(-10px);
  }
  60% {
    transform: translate(-50%, -50%) translateY(-5px);
  }
}

@keyframes float {
  from {
    transform: translateX(-200px);
  }
  to {
    transform: translateX(calc(100vw + 200px));
  }
}
</style> 