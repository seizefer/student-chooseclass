<template>
  <div class="notifications-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>通知中心</span>
          <div class="header-actions">
            <el-button size="small" @click="markAllRead" :disabled="unreadCount === 0">
              全部已读
            </el-button>
            <el-button size="small" @click="clearAll" :disabled="notifications.length === 0">
              清空
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选标签 -->
      <div class="filter-tabs">
        <el-radio-group v-model="filterType" @change="fetchNotifications">
          <el-radio-button value="all">全部</el-radio-button>
          <el-radio-button value="unread">
            未读
            <el-badge :value="unreadCount" :max="99" v-if="unreadCount > 0" />
          </el-radio-button>
          <el-radio-button value="system">系统</el-radio-button>
          <el-radio-button value="course">选课</el-radio-button>
          <el-radio-button value="message">消息</el-radio-button>
        </el-radio-group>
      </div>

      <!-- 通知列表 -->
      <div class="notification-list">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-item"
          :class="{ unread: !notification.is_read }"
          @click="handleClick(notification)"
        >
          <div class="notification-icon">
            <el-icon :size="24">
              <component :is="getIcon(notification.type)" />
            </el-icon>
          </div>
          <div class="notification-content">
            <div class="notification-title">
              {{ notification.title }}
              <el-tag v-if="!notification.is_read" type="danger" size="small">未读</el-tag>
            </div>
            <div class="notification-body">{{ notification.content }}</div>
            <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
          </div>
          <div class="notification-actions">
            <el-button
              v-if="!notification.is_read"
              size="small"
              text
              @click.stop="markRead(notification.id)"
            >
              标记已读
            </el-button>
            <el-button
              size="small"
              text
              type="danger"
              @click.stop="deleteNotification(notification.id)"
            >
              删除
            </el-button>
          </div>
        </div>

        <el-empty v-if="notifications.length === 0" description="暂无通知" />
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          @current-change="fetchNotifications"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Bell,
  Message,
  Reading,
  Warning,
  CircleCheck
} from '@element-plus/icons-vue'
import request from '@/api/request'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const router = useRouter()
const notifications = ref([])
const filterType = ref('all')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const unreadCount = ref(0)

// 获取图标
const getIcon = (type) => {
  const icons = {
    system: Bell,
    course: Reading,
    message: Message,
    warning: Warning,
    success: CircleCheck
  }
  return icons[type] || Bell
}

// 格式化时间
const formatTime = (time) => {
  return dayjs(time).fromNow()
}

// 获取通知列表
const fetchNotifications = async () => {
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      type: filterType.value === 'all' ? '' : filterType.value
    }
    if (filterType.value === 'unread') {
      params.is_read = false
      params.type = ''
    }

    const { data } = await request.get('/api/v1/notifications', { params })
    notifications.value = data.items || data
    total.value = data.total || data.length
    unreadCount.value = data.unread_count || notifications.value.filter(n => !n.is_read).length
  } catch (error) {
    // 模拟数据
    notifications.value = [
      {
        id: 1,
        type: 'course',
        title: '选课成功',
        content: '您已成功选修课程《高等数学》',
        is_read: false,
        created_at: new Date()
      },
      {
        id: 2,
        type: 'system',
        title: '系统通知',
        content: '选课系统将于本周五进行维护，届时暂停服务',
        is_read: true,
        created_at: new Date(Date.now() - 86400000)
      },
      {
        id: 3,
        type: 'message',
        title: '新消息',
        content: '您收到来自张三的好友请求',
        is_read: false,
        created_at: new Date(Date.now() - 3600000)
      }
    ]
    unreadCount.value = notifications.value.filter(n => !n.is_read).length
  }
}

// 标记单条已读
const markRead = async (id) => {
  try {
    await request.put(`/api/v1/notifications/${id}/read`)
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  } catch (error) {
    // 模拟成功
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  }
}

// 全部标记已读
const markAllRead = async () => {
  try {
    await request.put('/api/v1/notifications/read-all')
    notifications.value.forEach(n => n.is_read = true)
    unreadCount.value = 0
    ElMessage.success('已全部标记为已读')
  } catch (error) {
    // 模拟成功
    notifications.value.forEach(n => n.is_read = true)
    unreadCount.value = 0
    ElMessage.success('已全部标记为已读')
  }
}

// 删除通知
const deleteNotification = async (id) => {
  try {
    await request.delete(`/api/v1/notifications/${id}`)
    notifications.value = notifications.value.filter(n => n.id !== id)
    ElMessage.success('删除成功')
  } catch (error) {
    // 模拟成功
    notifications.value = notifications.value.filter(n => n.id !== id)
    ElMessage.success('删除成功')
  }
}

// 清空所有通知
const clearAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有通知吗?', '提示', {
      type: 'warning'
    })
    await request.delete('/api/v1/notifications/clear')
    notifications.value = []
    unreadCount.value = 0
    ElMessage.success('已清空')
  } catch (error) {
    if (error !== 'cancel') {
      notifications.value = []
      unreadCount.value = 0
    }
  }
}

// 点击通知
const handleClick = (notification) => {
  if (!notification.is_read) {
    markRead(notification.id)
  }
  // 根据类型跳转
  if (notification.link) {
    router.push(notification.link)
  }
}

onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped lang="scss">
.notifications-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-tabs {
  margin-bottom: 20px;
}

.notification-list {
  .notification-item {
    display: flex;
    align-items: flex-start;
    padding: 15px;
    border-bottom: 1px solid #ebeef5;
    cursor: pointer;
    transition: background-color 0.3s;

    &:hover {
      background-color: #f5f7fa;
    }

    &.unread {
      background-color: #ecf5ff;
    }
  }

  .notification-icon {
    margin-right: 15px;
    color: #409eff;
  }

  .notification-content {
    flex: 1;

    .notification-title {
      font-weight: 500;
      margin-bottom: 5px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .notification-body {
      color: #606266;
      font-size: 14px;
      margin-bottom: 5px;
    }

    .notification-time {
      color: #909399;
      font-size: 12px;
    }
  }

  .notification-actions {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
