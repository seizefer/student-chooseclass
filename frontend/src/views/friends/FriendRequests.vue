<template>
  <div class="requests-container">
    <el-card>
      <template #header>
        <span>好友请求</span>
      </template>

      <!-- 收到的请求 -->
      <h4>收到的请求</h4>
      <el-table :data="receivedRequests" v-loading="loading" stripe>
        <el-table-column label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :size="40" :src="row.avatar || defaultAvatar" />
          </template>
        </el-table-column>

        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="student_id" label="学号" />
        <el-table-column prop="department_name" label="院系" />

        <el-table-column label="请求时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="acceptRequest(row.friendship_id)"
            >
              接受
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="rejectRequest(row.friendship_id)"
            >
              拒绝
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="receivedRequests.length === 0" description="暂无好友请求" />

      <!-- 发出的请求 -->
      <h4 style="margin-top: 30px">发出的请求</h4>
      <el-table :data="sentRequests" stripe>
        <el-table-column label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :size="40" :src="row.avatar || defaultAvatar" />
          </template>
        </el-table-column>

        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="student_id" label="学号" />

        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="请求时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              size="small"
              @click="cancelRequest(row.friendship_id)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="sentRequests.length === 0" description="暂无发出的请求" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'
import dayjs from 'dayjs'

const loading = ref(false)
const receivedRequests = ref([])
const sentRequests = ref([])
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    accepted: 'success',
    declined: 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    pending: '待处理',
    accepted: '已接受',
    declined: '已拒绝'
  }
  return texts[status] || status
}

// 获取好友请求
const fetchRequests = async () => {
  loading.value = true
  try {
    const { data } = await request.get('/api/v1/friendships/requests')
    receivedRequests.value = data.received || []
    sentRequests.value = data.sent || []
  } catch (error) {
    ElMessage.error('获取好友请求失败')
  } finally {
    loading.value = false
  }
}

// 接受请求
const acceptRequest = async (friendshipId) => {
  try {
    await request.put(`/api/v1/friendships/${friendshipId}/accept`)
    ElMessage.success('已接受好友请求')
    fetchRequests()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 拒绝请求
const rejectRequest = async (friendshipId) => {
  try {
    await request.put(`/api/v1/friendships/${friendshipId}/reject`)
    ElMessage.success('已拒绝好友请求')
    fetchRequests()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 取消请求
const cancelRequest = async (friendshipId) => {
  try {
    await request.delete(`/api/v1/friendships/${friendshipId}`)
    ElMessage.success('已取消请求')
    fetchRequests()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchRequests()
})
</script>

<style scoped lang="scss">
.requests-container {
  padding: 20px;
}

h4 {
  margin-bottom: 15px;
  color: #303133;
}
</style>
