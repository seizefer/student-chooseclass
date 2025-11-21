<template>
  <div class="recommendations-container">
    <el-card>
      <template #header>
        <span>推荐好友</span>
      </template>

      <el-row :gutter="20">
        <el-col
          v-for="user in recommendations"
          :key="user.student_id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <el-card class="user-card" shadow="hover">
            <div class="user-info">
              <el-avatar :size="60" :src="user.avatar || defaultAvatar" />
              <h4>{{ user.name }}</h4>
              <p class="student-id">{{ user.student_id }}</p>
              <p class="department">{{ user.department_name }}</p>
              <p class="mutual" v-if="user.mutual_friends > 0">
                <el-icon><User /></el-icon>
                {{ user.mutual_friends }} 个共同好友
              </p>
            </div>
            <el-button
              type="primary"
              size="small"
              @click="sendRequest(user.student_id)"
              :loading="user.loading"
            >
              添加好友
            </el-button>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-if="recommendations.length === 0" description="暂无推荐好友" />
    </el-card>

    <!-- 搜索添加好友 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <span>搜索用户</span>
      </template>

      <el-input
        v-model="searchQuery"
        placeholder="输入学号或姓名搜索"
        @keyup.enter="searchUsers"
      >
        <template #append>
          <el-button @click="searchUsers">搜索</el-button>
        </template>
      </el-input>

      <el-table :data="searchResults" style="margin-top: 20px" v-if="searchResults.length > 0">
        <el-table-column label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :size="40" :src="row.avatar || defaultAvatar" />
          </template>
        </el-table-column>

        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="student_id" label="学号" />
        <el-table-column prop="department_name" label="院系" />

        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="sendRequest(row.student_id)"
              :disabled="row.is_friend"
            >
              {{ row.is_friend ? '已添加' : '添加' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import request from '@/api/request'

const recommendations = ref([])
const searchQuery = ref('')
const searchResults = ref([])
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 获取推荐好友
const fetchRecommendations = async () => {
  try {
    const { data } = await request.get('/api/v1/friendships/recommendations')
    recommendations.value = data.map(u => ({ ...u, loading: false }))
  } catch (error) {
    ElMessage.error('获取推荐好友失败')
  }
}

// 搜索用户
const searchUsers = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  try {
    const { data } = await request.get('/api/v1/students/list', {
      params: { query: searchQuery.value }
    })
    searchResults.value = data
  } catch (error) {
    ElMessage.error('搜索失败')
  }
}

// 发送好友请求
const sendRequest = async (studentId) => {
  try {
    await request.post('/api/v1/friendships/request', {
      friend_id: studentId
    })
    ElMessage.success('好友请求已发送')
    // 从推荐列表中移除
    recommendations.value = recommendations.value.filter(
      u => u.student_id !== studentId
    )
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '发送请求失败')
  }
}

onMounted(() => {
  fetchRecommendations()
})
</script>

<style scoped lang="scss">
.recommendations-container {
  padding: 20px;
}

.user-card {
  text-align: center;
  margin-bottom: 20px;

  .user-info {
    padding: 10px 0;

    h4 {
      margin: 10px 0 5px;
    }

    .student-id {
      color: #909399;
      font-size: 12px;
    }

    .department {
      color: #606266;
      font-size: 13px;
      margin: 5px 0;
    }

    .mutual {
      color: #409eff;
      font-size: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
    }
  }
}
</style>
