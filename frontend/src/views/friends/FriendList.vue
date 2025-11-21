<template>
  <div class="friends-container">
    <!-- 快捷导航 -->
    <div class="quick-nav">
      <router-link to="/friends" class="nav-item active">
        <el-icon><User /></el-icon>
        好友列表
        <el-badge v-if="friendCount > 0" :value="friendCount" type="primary" />
      </router-link>
      <router-link to="/friends/requests" class="nav-item">
        <el-icon><Bell /></el-icon>
        好友请求
        <el-badge v-if="pendingCount > 0" :value="pendingCount" :is-dot="false" />
      </router-link>
      <router-link to="/friends/recommendations" class="nav-item">
        <el-icon><Star /></el-icon>
        推荐好友
      </router-link>
    </div>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的好友 ({{ friendCount }})</span>
          <el-input
            v-model="searchQuery"
            placeholder="搜索好友姓名或学号"
            style="width: 220px"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </template>

      <!-- 好友列表 -->
      <el-table :data="filteredFriends" v-loading="loading" stripe>
        <el-table-column label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :size="40" :src="row.avatar || defaultAvatar" />
          </template>
        </el-table-column>

        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="student_id" label="学号" />
        <el-table-column prop="department_name" label="院系" />

        <el-table-column label="添加时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="sendMessage(row)">
              发消息
            </el-button>
            <el-button size="small" @click="transfer(row)">
              转账
            </el-button>
            <el-popconfirm
              title="确定要删除该好友吗?"
              @confirm="removeFriend(row.friendship_id)"
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
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchFriends"
          @current-change="fetchFriends"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, User, Bell, Star } from '@element-plus/icons-vue'
import request from '@/api/request'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const friends = ref([])
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const pendingCount = ref(0)
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 好友数量
const friendCount = computed(() => friends.value.length)

// 过滤后的好友列表
const filteredFriends = computed(() => {
  if (!searchQuery.value) return friends.value
  const query = searchQuery.value.toLowerCase()
  return friends.value.filter(
    f => f.name.toLowerCase().includes(query) ||
         f.student_id.includes(query)
  )
})

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 获取好友列表
const fetchFriends = async () => {
  loading.value = true
  try {
    const { data } = await request.get('/api/v1/friendships/list', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    friends.value = data.items || data
    total.value = data.total || data.length
  } catch (error) {
    ElMessage.error('获取好友列表失败')
  } finally {
    loading.value = false
  }
}

// 发消息
const sendMessage = (friend) => {
  router.push({
    path: '/messages/compose',
    query: { to: friend.student_id }
  })
}

// 转账
const transfer = (friend) => {
  router.push({
    path: '/transactions/transfer',
    query: { to: friend.student_id }
  })
}

// 删除好友
const removeFriend = async (friendshipId) => {
  try {
    await request.delete(`/api/v1/friendships/${friendshipId}`)
    ElMessage.success('已删除好友')
    fetchFriends()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 获取待处理请求数量
const fetchPendingCount = async () => {
  try {
    const { data } = await request.get('/api/v1/friendships/requests')
    pendingCount.value = data.received?.length || 0
  } catch (error) {
    console.error('获取请求数量失败', error)
  }
}

onMounted(() => {
  fetchFriends()
  fetchPendingCount()
})
</script>

<style scoped lang="scss">
.friends-container {
  padding: 20px;
}

.quick-nav {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;

  .nav-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 20px;
    background: #fff;
    border-radius: 8px;
    text-decoration: none;
    color: #606266;
    font-size: 14px;
    transition: all 0.3s;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);

    &:hover {
      color: #409eff;
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }

    &.router-link-exact-active,
    &.active {
      background: #409eff;
      color: #fff;
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
