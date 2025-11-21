<!--
仪表盘首页
@version: v1.2.0
@date: 2024-12-06
-->
<template>
  <div class="dashboard">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-text">
        <h1>欢迎回来，{{ authStore.userName }}！</h1>
        <p>今天是{{ currentDate }}，祝您学习愉快！</p>
      </div>
      <div class="weather-info">
        <el-icon class="weather-icon"><Sunny /></el-icon>
        <span>{{ currentTime }}</span>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="24" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card clickable" @click="goToCourses">
          <div class="stat-icon courses">
            <el-icon><Reading /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.courseCount }}</div>
            <div class="stat-label">已选课程</div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card clickable" @click="goToFriends">
          <div class="stat-icon friends">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.friendCount }}</div>
            <div class="stat-label">好友数量</div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card clickable" @click="goToMessages">
          <div class="stat-icon messages">
            <el-icon><ChatLineRound /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ stats.unreadMessages }}</div>
            <div class="stat-label">未读消息</div>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card clickable" @click="goToTransactions">
          <div class="stat-icon balance">
            <el-icon><Wallet /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">¥{{ stats.balance }}</div>
            <div class="stat-label">账户余额</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 主要内容区域 -->
    <el-row :gutter="24" class="content-row">
      <!-- 左侧内容 -->
      <el-col :xs="24" :lg="16">
        <!-- 快捷操作 -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">快捷操作</h3>
          </div>
          <div class="quick-actions">
            <el-button
              v-for="action in quickActions"
              :key="action.name"
              :type="action.type"
              size="large"
              class="action-btn"
              @click="handleQuickAction(action.path)"
            >
              <el-icon><component :is="action.icon" /></el-icon>
              {{ action.name }}
            </el-button>
          </div>
        </div>

        <!-- 最近课程 -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">最近课程</h3>
            <el-link type="primary" @click="$router.push('/courses/my-courses')">查看全部</el-link>
          </div>
          <div class="recent-courses">
            <div
              v-for="course in recentCourses"
              :key="course.id"
              class="course-item"
              @click="viewCourseDetail(course.id)"
            >
              <div class="course-info">
                <h4>{{ course.name }}</h4>
                <p>{{ course.teacher }} · {{ course.department }}</p>
              </div>
              <div class="course-status">
                <el-tag :type="getCourseStatusType(course.status)">
                  {{ course.status }}
                </el-tag>
              </div>
            </div>
            
            <el-empty v-if="recentCourses.length === 0" description="暂无课程数据" />
          </div>
        </div>
      </el-col>

      <!-- 右侧侧边栏 -->
      <el-col :xs="24" :lg="8">
        <!-- 消息通知 -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">最新消息</h3>
            <el-link type="primary" @click="$router.push('/messages')">查看全部</el-link>
          </div>
          <div class="messages-list">
            <div
              v-for="message in recentMessages"
              :key="message.id"
              class="message-item"
              @click="viewMessage(message.id)"
            >
              <el-avatar :size="32" class="message-avatar">
                <el-icon><User /></el-icon>
              </el-avatar>
              <div class="message-content">
                <div class="message-sender">{{ message.sender }}</div>
                <div class="message-preview">{{ message.content }}</div>
                <div class="message-time">{{ formatTime(message.time) }}</div>
              </div>
              <el-badge
                v-if="!message.isRead"
                is-dot
                class="message-badge"
              />
            </div>
            
            <el-empty v-if="recentMessages.length === 0" description="暂无消息" />
          </div>
        </div>

        <!-- 系统公告 -->
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">系统公告</h3>
          </div>
          <div class="announcements">
            <div
              v-for="announcement in announcements"
              :key="announcement.id"
              class="announcement-item"
            >
              <div class="announcement-title">{{ announcement.title }}</div>
              <div class="announcement-time">{{ formatDate(announcement.date) }}</div>
            </div>
            
            <el-empty v-if="announcements.length === 0" description="暂无公告" />
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Sunny, Reading, User, ChatLineRound, Wallet,
  Plus, Search, Message as MessageBox, CreditCard
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const stats = reactive({
  courseCount: 0,
  friendCount: 0,
  unreadMessages: 0,
  balance: 0
})

const recentCourses = ref([])
const recentMessages = ref([])
const announcements = ref([])

// 当前日期和时间
const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

const currentTime = ref('')

// 快捷操作配置
const quickActions = [
  { name: '浏览课程', icon: Search, type: 'primary', path: '/courses' },
  { name: '选课管理', icon: Plus, type: 'success', path: '/courses/my-courses' },
  { name: '发送消息', icon: MessageBox, type: 'warning', path: '/messages/compose' },
  { name: '转账', icon: CreditCard, type: 'danger', path: '/transactions/transfer' }
]

// 处理快捷操作
const handleQuickAction = (path) => {
  router.push(path)
}

// 查看课程详情
const viewCourseDetail = (courseId) => {
  router.push(`/courses/${courseId}`)
}

// 查看消息详情
const viewMessage = (messageId) => {
  router.push(`/messages/${messageId}`)
}

// 导航到不同页面
const goToCourses = () => {
  router.push('/courses/my-courses')
}

const goToFriends = () => {
  router.push('/friends')
}

const goToMessages = () => {
  router.push('/messages')
}

const goToTransactions = () => {
  router.push('/transactions')
}

// 获取课程状态类型
const getCourseStatusType = (status) => {
  const statusMap = {
    '进行中': 'success',
    '已结束': 'info',
    '未开始': 'warning'
  }
  return statusMap[status] || 'info'
}

// 格式化时间
const formatTime = (time) => {
  return new Date(time).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化日期
const formatDate = (date) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

// 更新当前时间
const updateCurrentTime = () => {
  currentTime.value = new Date().toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 加载仪表盘数据
const loadDashboardData = async () => {
  try {
    const token = localStorage.getItem('token')
    const headers = { 'Authorization': `Bearer ${token}` }

    // 尝试获取真实数据
    try {
      // 获取选课数量
      const coursesRes = await fetch('http://localhost:8000/api/v1/enrollments/my-courses', { headers })
      if (coursesRes.ok) {
        const coursesData = await coursesRes.json()
        stats.courseCount = coursesData.data?.length || 0
      }

      // 获取好友数量
      const friendsRes = await fetch('http://localhost:8000/api/v1/friendships/list', { headers })
      if (friendsRes.ok) {
        const friendsData = await friendsRes.json()
        stats.friendCount = friendsData.data?.length || 0
      }

      // 获取未读消息数
      const messagesRes = await fetch('http://localhost:8000/api/v1/messages/unread/count', { headers })
      if (messagesRes.ok) {
        const messagesData = await messagesRes.json()
        stats.unreadMessages = messagesData.data?.unread_count || 0
      }

      // 获取余额
      const balanceRes = await fetch('http://localhost:8000/api/v1/transactions/balance', { headers })
      if (balanceRes.ok) {
        const balanceData = await balanceRes.json()
        stats.balance = balanceData.data?.balance || 0
      }
    } catch (apiError) {
      console.warn('API调用失败，使用模拟数据')
      // 使用模拟数据
      stats.courseCount = 5
      stats.friendCount = 12
      stats.unreadMessages = 3
      stats.balance = 1234.56
    }

    // 如果没有获取到数据，使用默认值
    if (stats.courseCount === 0 && stats.friendCount === 0) {
      stats.courseCount = 5
      stats.friendCount = 12
      stats.unreadMessages = 3
      stats.balance = 1234.56
    }

    recentCourses.value = [
      {
        id: 1,
        name: '高等数学A',
        teacher: '张教授',
        department: '数学系',
        status: '进行中'
      },
      {
        id: 2,
        name: '大学英语',
        teacher: '李老师',
        department: '外语系',
        status: '进行中'
      },
      {
        id: 3,
        name: '计算机基础',
        teacher: '王老师',
        department: '计算机系',
        status: '未开始'
      }
    ]

    recentMessages.value = [
      {
        id: 1,
        sender: '张同学',
        content: '你好，请问作业什么时候提交？',
        time: new Date().getTime() - 1000 * 60 * 30,
        isRead: false
      },
      {
        id: 2,
        sender: '李同学',
        content: '明天一起去图书馆吗？',
        time: new Date().getTime() - 1000 * 60 * 60,
        isRead: true
      }
    ]

    announcements.value = [
      {
        id: 1,
        title: '系统维护通知',
        date: new Date().getTime() - 1000 * 60 * 60 * 24
      },
      {
        id: 2,
        title: '选课系统更新说明',
        date: new Date().getTime() - 1000 * 60 * 60 * 48
      }
    ]
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
  }
}

// 组件挂载
onMounted(() => {
  console.log('📊 Dashboard组件已挂载!')
  console.log('👤 当前用户信息:', authStore.user)
  console.log('🔑 认证状态:', authStore.isAuthenticated)
  console.log('🎫 Token存在:', !!authStore.token)

  loadDashboardData()
  updateCurrentTime()

  // 每分钟更新一次时间
  setInterval(updateCurrentTime, 60000)
})
</script>

<style lang="scss" scoped>
.dashboard {
  padding: 0;
}

.welcome-section {
  background: linear-gradient(135deg, var(--primary-color) 0%, #667eea 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .welcome-text {
    h1 {
      font-size: 28px;
      margin: 0 0 8px;
      font-weight: 600;
    }
    
    p {
      font-size: 16px;
      margin: 0;
      opacity: 0.9;
    }
  }
  
  .weather-info {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    
    .weather-icon {
      font-size: 24px;
    }
  }
  
  @media (max-width: 768px) {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-color);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-base);
  transition: transform 0.3s ease;

  &.clickable {
    cursor: pointer;

    &:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-hover);
    }
  }

  &:hover {
    transform: translateY(-2px);
  }
  
  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
    
    &.courses {
      background: linear-gradient(135deg, #667eea, #764ba2);
    }
    
    &.friends {
      background: linear-gradient(135deg, #f093fb, #f5576c);
    }
    
    &.messages {
      background: linear-gradient(135deg, #4facfe, #00f2fe);
    }
    
    &.balance {
      background: linear-gradient(135deg, #43e97b, #38f9d7);
    }
  }
  
  .stat-content {
    .stat-number {
      font-size: 28px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 4px;
    }
    
    .stat-label {
      font-size: 14px;
      color: var(--text-secondary);
    }
  }
}

.content-row {
  .card {
    background: var(--bg-color);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: var(--shadow-base);
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      
      .card-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
      }
    }
  }
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  
  .action-btn {
    height: 60px;
    font-size: 16px;
    border-radius: 8px;
    
    .el-icon {
      margin-right: 8px;
      font-size: 18px;
    }
  }
}

.recent-courses {
  .course-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0;
    border-bottom: 1px solid var(--border-lighter);
    cursor: pointer;
    transition: background-color 0.3s ease;
    
    &:hover {
      background-color: var(--bg-lighter);
      margin: 0 -16px;
      padding: 16px;
      border-radius: 8px;
    }
    
    &:last-child {
      border-bottom: none;
    }
    
    .course-info {
      h4 {
        font-size: 16px;
        font-weight: 500;
        color: var(--text-primary);
        margin: 0 0 4px;
      }
      
      p {
        font-size: 14px;
        color: var(--text-secondary);
        margin: 0;
      }
    }
  }
}

.messages-list {
  .message-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 16px 0;
    border-bottom: 1px solid var(--border-lighter);
    cursor: pointer;
    position: relative;
    transition: background-color 0.3s ease;
    
    &:hover {
      background-color: var(--bg-lighter);
      margin: 0 -16px;
      padding: 16px;
      border-radius: 8px;
    }
    
    &:last-child {
      border-bottom: none;
    }
    
    .message-content {
      flex: 1;
      
      .message-sender {
        font-size: 14px;
        font-weight: 500;
        color: var(--text-primary);
        margin-bottom: 4px;
      }
      
      .message-preview {
        font-size: 13px;
        color: var(--text-secondary);
        margin-bottom: 4px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      .message-time {
        font-size: 12px;
        color: var(--text-placeholder);
      }
    }
    
    .message-badge {
      position: absolute;
      top: 16px;
      right: 8px;
    }
  }
}

.announcements {
  .announcement-item {
    padding: 12px 0;
    border-bottom: 1px solid var(--border-lighter);
    
    &:last-child {
      border-bottom: none;
    }
    
    .announcement-title {
      font-size: 14px;
      color: var(--text-primary);
      margin-bottom: 4px;
    }
    
    .announcement-time {
      font-size: 12px;
      color: var(--text-placeholder);
    }
  }
}

@media (max-width: 768px) {
  .quick-actions {
    grid-template-columns: 1fr;
  }
  
  .stats-row {
    .el-col {
      margin-bottom: 16px;
    }
  }
}
</style> 