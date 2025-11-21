<!--
消息管理主页面
@version: v1.0.0
@date: 2024-12-06
-->
<template>
  <div class="messages">
    <div class="page-header">
      <h1>消息中心</h1>
      <p>管理您的所有消息</p>
    </div>

    <el-row :gutter="20">
      <!-- 左侧消息列表 -->
      <el-col :xs="24" :lg="16">
        <div class="messages-panel">
          <!-- 消息标签页 -->
          <el-tabs v-model="activeTab" class="message-tabs">
            <el-tab-pane label="收件箱" name="inbox">
              <div class="tab-header">
                <el-input
                  v-model="searchQuery"
                  placeholder="搜索消息..."
                  prefix-icon="Search"
                  clearable
                  style="width: 300px"
                />
                <el-button type="primary" @click="markAllAsRead">
                  全部标记为已读
                </el-button>
              </div>
              
              <div class="messages-list">
                <div
                  v-for="message in filteredInboxMessages"
                  :key="message.id"
                  class="message-item"
                  :class="{ unread: !message.isRead, selected: selectedMessage?.id === message.id }"
                  @click="selectMessage(message)"
                >
                  <el-avatar :size="40" class="message-avatar">
                    <el-icon><User /></el-icon>
                  </el-avatar>
                  
                  <div class="message-content">
                    <div class="message-header">
                      <span class="sender">{{ message.sender }}</span>
                      <span class="time">{{ formatTime(message.time) }}</span>
                    </div>
                    <div class="subject">{{ message.subject }}</div>
                    <div class="preview">{{ message.preview }}</div>
                  </div>
                  
                  <div class="message-status">
                    <el-badge v-if="!message.isRead" is-dot />
                    <el-icon v-if="message.hasAttachment"><Paperclip /></el-icon>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="发件箱" name="sent">
              <div class="tab-header">
                <el-input
                  v-model="searchQuery"
                  placeholder="搜索消息..."
                  prefix-icon="Search"
                  clearable
                  style="width: 300px"
                />
                <el-button type="primary" @click="$router.push('/messages/compose')">
                  <el-icon><Edit /></el-icon>
                  新建消息
                </el-button>
              </div>
              
              <div class="messages-list">
                <div
                  v-for="message in filteredSentMessages"
                  :key="message.id"
                  class="message-item"
                  :class="{ selected: selectedMessage?.id === message.id }"
                  @click="selectMessage(message)"
                >
                  <el-avatar :size="40" class="message-avatar">
                    <el-icon><User /></el-icon>
                  </el-avatar>
                  
                  <div class="message-content">
                    <div class="message-header">
                      <span class="sender">发送给: {{ message.recipient }}</span>
                      <span class="time">{{ formatTime(message.time) }}</span>
                    </div>
                    <div class="subject">{{ message.subject }}</div>
                    <div class="preview">{{ message.preview }}</div>
                  </div>
                  
                  <div class="message-status">
                    <el-tag :type="getStatusType(message.status)" size="small">
                      {{ getStatusText(message.status) }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>

          <!-- 空状态 -->
          <el-empty
            v-if="currentMessages.length === 0"
            :description="activeTab === 'inbox' ? '暂无收到的消息' : '暂无发送的消息'"
          >
            <el-button type="primary" @click="$router.push('/messages/compose')">
              发送第一条消息
            </el-button>
          </el-empty>
        </div>
      </el-col>

      <!-- 右侧消息详情 -->
      <el-col :xs="24" :lg="8">
        <div class="message-detail-panel">
          <div v-if="selectedMessage" class="message-detail">
            <div class="detail-header">
              <h3>{{ selectedMessage.subject }}</h3>
              <div class="detail-meta">
                <p><strong>发件人:</strong> {{ selectedMessage.sender }}</p>
                <p><strong>收件人:</strong> {{ selectedMessage.recipient || '我' }}</p>
                <p><strong>时间:</strong> {{ formatDateTime(selectedMessage.time) }}</p>
              </div>
            </div>
            
            <div class="detail-content">
              <div v-html="selectedMessage.content"></div>
            </div>
            
            <div class="detail-actions">
              <el-button @click="replyMessage" v-if="activeTab === 'inbox'">
                <el-icon><Reply /></el-icon>
                回复
              </el-button>
              <el-button @click="forwardMessage">
                <el-icon><Share /></el-icon>
                转发
              </el-button>
              <el-button type="danger" @click="deleteMessage">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>
          
          <el-empty v-else description="选择一条消息查看详情" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  User, Search, Edit, Paperclip, Reply, Share, Delete 
} from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const activeTab = ref('inbox')
const searchQuery = ref('')
const selectedMessage = ref(null)
const inboxMessages = ref([])
const sentMessages = ref([])

// 模拟数据
const mockInboxMessages = [
  {
    id: 1,
    sender: '张同学',
    recipient: '我',
    subject: '关于课程作业的问题',
    preview: '你好，请问这次的数学作业什么时候提交？',
    content: '<p>你好，</p><p>请问这次的数学作业什么时候提交？我有几道题不太理解，能否请教一下？</p><p>谢谢！</p>',
    time: new Date().getTime() - 1000 * 60 * 30,
    isRead: false,
    hasAttachment: false
  },
  {
    id: 2,
    sender: '李老师',
    recipient: '我',
    subject: '课程安排通知',
    preview: '下周的英语课因为节假日调整到周三...',
    content: '<p>各位同学，</p><p>下周的英语课因为节假日调整到周三下午2:00-4:00，教室不变。</p><p>请大家相互转告。</p>',
    time: new Date().getTime() - 1000 * 60 * 60 * 2,
    isRead: true,
    hasAttachment: false
  },
  {
    id: 3,
    sender: '王同学',
    recipient: '我',
    subject: '图书馆学习邀请',
    preview: '明天下午有空一起去图书馆学习吗？',
    content: '<p>嗨！</p><p>明天下午有空一起去图书馆学习吗？我们可以一起复习线性代数。</p>',
    time: new Date().getTime() - 1000 * 60 * 60 * 24,
    isRead: false,
    hasAttachment: true
  }
]

const mockSentMessages = [
  {
    id: 4,
    sender: '我',
    recipient: '赵同学',
    subject: '作业答案分享',
    preview: '这是昨天布置的作业答案，希望对你有帮助...',
    content: '<p>这是昨天布置的作业答案，希望对你有帮助。</p><p>有问题随时联系我。</p>',
    time: new Date().getTime() - 1000 * 60 * 60 * 6,
    status: 'sent'
  },
  {
    id: 5,
    sender: '我',
    recipient: '陈老师',
    subject: '请假申请',
    preview: '由于身体不适，申请请假一天...',
    content: '<p>尊敬的老师，</p><p>由于身体不适，申请请假一天。课程内容我会找同学补习。</p><p>谢谢理解。</p>',
    time: new Date().getTime() - 1000 * 60 * 60 * 48,
    status: 'read'
  }
]

// 计算属性
const currentMessages = computed(() => {
  return activeTab.value === 'inbox' ? inboxMessages.value : sentMessages.value
})

const filteredInboxMessages = computed(() => {
  if (!searchQuery.value) return inboxMessages.value
  
  const query = searchQuery.value.toLowerCase()
  return inboxMessages.value.filter(msg =>
    msg.sender.toLowerCase().includes(query) ||
    msg.subject.toLowerCase().includes(query) ||
    msg.preview.toLowerCase().includes(query)
  )
})

const filteredSentMessages = computed(() => {
  if (!searchQuery.value) return sentMessages.value
  
  const query = searchQuery.value.toLowerCase()
  return sentMessages.value.filter(msg =>
    msg.recipient.toLowerCase().includes(query) ||
    msg.subject.toLowerCase().includes(query) ||
    msg.preview.toLowerCase().includes(query)
  )
})

// 方法
const formatTime = (timestamp) => {
  const now = new Date()
  const date = new Date(timestamp)
  const diff = now.getTime() - timestamp

  if (diff < 1000 * 60 * 60 * 24) {
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  } else {
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric'
    })
  }
}

const formatDateTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const statusMap = {
    'sent': 'info',
    'read': 'success',
    'failed': 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'sent': '已发送',
    'read': '已读',
    'failed': '发送失败'
  }
  return statusMap[status] || '未知'
}

const selectMessage = (message) => {
  selectedMessage.value = message
  
  // 如果是收件箱未读消息，标记为已读
  if (activeTab.value === 'inbox' && !message.isRead) {
    message.isRead = true
    // 这里可以调用API标记为已读
  }
}

const markAllAsRead = () => {
  inboxMessages.value.forEach(msg => {
    msg.isRead = true
  })
  ElMessage.success('已标记所有消息为已读')
}

const replyMessage = () => {
  router.push({
    path: '/messages/compose',
    query: {
      reply: selectedMessage.value.id,
      to: selectedMessage.value.sender,
      subject: `Re: ${selectedMessage.value.subject}`
    }
  })
}

const forwardMessage = () => {
  router.push({
    path: '/messages/compose',
    query: {
      forward: selectedMessage.value.id,
      subject: `Fwd: ${selectedMessage.value.subject}`,
      content: selectedMessage.value.content
    }
  })
}

const deleteMessage = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这条消息吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 从对应列表中删除消息
    if (activeTab.value === 'inbox') {
      const index = inboxMessages.value.findIndex(msg => msg.id === selectedMessage.value.id)
      if (index > -1) {
        inboxMessages.value.splice(index, 1)
      }
    } else {
      const index = sentMessages.value.findIndex(msg => msg.id === selectedMessage.value.id)
      if (index > -1) {
        sentMessages.value.splice(index, 1)
      }
    }
    
    selectedMessage.value = null
    ElMessage.success('消息已删除')
  } catch {
    ElMessage.info('已取消删除')
  }
}

const loadMessages = async () => {
  try {
    const token = localStorage.getItem('token')
    const headers = { 'Authorization': `Bearer ${token}` }

    // 尝试调用真实 API
    try {
      // 获取收件箱
      const inboxRes = await fetch('http://localhost:8000/api/v1/messages/inbox', { headers })
      if (inboxRes.ok) {
        const inboxData = await inboxRes.json()
        if (inboxData.data?.items?.length > 0) {
          inboxMessages.value = inboxData.data.items.map(msg => ({
            id: msg.message_id,
            sender: msg.sender_name || msg.sender_id,
            recipient: msg.recipient_name || msg.recipient_id,
            subject: msg.subject,
            preview: msg.content.substring(0, 50) + '...',
            content: `<p>${msg.content}</p>`,
            time: new Date(msg.created_at).getTime(),
            isRead: msg.is_read,
            hasAttachment: false
          }))
        } else {
          inboxMessages.value = mockInboxMessages
        }
      }

      // 获取发件箱
      const sentRes = await fetch('http://localhost:8000/api/v1/messages/sent', { headers })
      if (sentRes.ok) {
        const sentData = await sentRes.json()
        if (sentData.data?.items?.length > 0) {
          sentMessages.value = sentData.data.items.map(msg => ({
            id: msg.message_id,
            sender: '我',
            recipient: msg.recipient_name || msg.recipient_id,
            subject: msg.subject,
            preview: msg.content.substring(0, 50) + '...',
            content: `<p>${msg.content}</p>`,
            time: new Date(msg.created_at).getTime(),
            status: msg.is_read ? 'read' : 'sent'
          }))
        } else {
          sentMessages.value = mockSentMessages
        }
      }
    } catch (apiError) {
      console.warn('API调用失败，使用模拟数据:', apiError)
      inboxMessages.value = mockInboxMessages
      sentMessages.value = mockSentMessages
    }

    // 如果没有数据，使用模拟数据
    if (inboxMessages.value.length === 0) {
      inboxMessages.value = mockInboxMessages
    }
    if (sentMessages.value.length === 0) {
      sentMessages.value = mockSentMessages
    }
  } catch (error) {
    console.error('加载消息失败:', error)
    inboxMessages.value = mockInboxMessages
    sentMessages.value = mockSentMessages
  }
}

// 组件挂载
onMounted(() => {
  loadMessages()
})
</script>

<style lang="scss" scoped>
.messages {
  padding: 20px;
  height: calc(100vh - 120px);
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

.messages-panel {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 600px;
  overflow: hidden;
}

.message-tabs {
  height: 100%;
  
  :deep(.el-tabs__content) {
    height: calc(100% - 54px);
    overflow: hidden;
  }
  
  :deep(.el-tab-pane) {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color-light);
}

.messages-list {
  flex: 1;
  overflow-y: auto;
}

.message-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color-lighter);
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: var(--fill-color-lighter);
  }

  &.selected {
    background-color: var(--color-primary-light-9);
    border-left: 3px solid var(--color-primary);
  }

  &.unread {
    background-color: var(--color-primary-light-9);
    font-weight: 500;
  }
}

.message-avatar {
  margin-right: 12px;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  
  .sender {
    font-weight: 500;
    color: var(--text-color-primary);
  }
  
  .time {
    font-size: 12px;
    color: var(--text-color-secondary);
  }
}

.subject {
  font-size: 14px;
  color: var(--text-color-regular);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preview {
  font-size: 12px;
  color: var(--text-color-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.message-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
}

.message-detail-panel {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 600px;
  overflow: hidden;
}

.message-detail {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.detail-header {
  margin-bottom: 20px;
  
  h3 {
    margin: 0 0 12px 0;
    color: var(--text-color-primary);
  }
}

.detail-meta {
  p {
    margin: 4px 0;
    font-size: 14px;
    color: var(--text-color-regular);
  }
}

.detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  border-top: 1px solid var(--border-color-lighter);
  border-bottom: 1px solid var(--border-color-lighter);
  
  :deep(p) {
    margin: 8px 0;
    line-height: 1.6;
  }
}

.detail-actions {
  padding-top: 20px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

@media (max-width: 1024px) {
  .messages {
    padding: 10px;
  }
  
  .messages-panel,
  .message-detail-panel {
    height: auto;
    min-height: 400px;
  }
}
</style> 