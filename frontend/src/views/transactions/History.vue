<template>
  <div class="history-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>交易记录</span>
          <div class="balance-info">
            当前余额: <span class="amount">¥{{ balance }}</span>
          </div>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-select v-model="filterType" placeholder="交易类型" clearable>
          <el-option label="全部" value="" />
          <el-option label="转入" value="in" />
          <el-option label="转出" value="out" />
        </el-select>

        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />

        <el-button type="primary" @click="fetchHistory">查询</el-button>
        <el-button @click="resetFilter">重置</el-button>
      </div>

      <!-- 交易列表 -->
      <el-table :data="transactions" v-loading="loading" stripe>
        <el-table-column label="时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'in' ? 'success' : 'danger'">
              {{ row.direction === 'in' ? '转入' : '转出' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="金额" width="120">
          <template #default="{ row }">
            <span :class="row.direction === 'in' ? 'amount-in' : 'amount-out'">
              {{ row.direction === 'in' ? '+' : '-' }}¥{{ row.amount }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="对方">
          <template #default="{ row }">
            {{ row.counterparty_name }} ({{ row.counterparty_id }})
          </template>
        </el-table-column>

        <el-table-column prop="description" label="备注" show-overflow-tooltip />

        <el-table-column label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag
              v-if="row.risk_level"
              :type="getRiskType(row.risk_level)"
              size="small"
            >
              {{ row.risk_level }}
            </el-tag>
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
          @size-change="fetchHistory"
          @current-change="fetchHistory"
        />
      </div>
    </el-card>

    <!-- 统计信息 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="8">
        <el-card class="stat-card">
          <el-statistic title="总转入" :value="statistics.total_in" prefix="¥" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <el-statistic title="总转出" :value="statistics.total_out" prefix="¥" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <el-statistic title="交易次数" :value="statistics.total_count" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'
import dayjs from 'dayjs'

const loading = ref(false)
const transactions = ref([])
const balance = ref(0)
const filterType = ref('')
const dateRange = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const statistics = reactive({
  total_in: 0,
  total_out: 0,
  total_count: 0
})

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 获取风险等级类型
const getRiskType = (level) => {
  const types = {
    low: 'success',
    medium: 'warning',
    high: 'danger'
  }
  return types[level] || 'info'
}

// 获取余额
const fetchBalance = async () => {
  try {
    const { data } = await request.get('/api/v1/transactions/balance')
    balance.value = data.balance
  } catch (error) {
    console.error('获取余额失败', error)
  }
}

// 获取交易历史
const fetchHistory = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (filterType.value) {
      params.direction = filterType.value
    }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }

    const { data } = await request.get('/api/v1/transactions/history', { params })
    transactions.value = data.items || data
    total.value = data.total || data.length
  } catch (error) {
    ElMessage.error('获取交易记录失败')
  } finally {
    loading.value = false
  }
}

// 获取统计信息
const fetchStatistics = async () => {
  try {
    const { data } = await request.get('/api/v1/transactions/statistics')
    Object.assign(statistics, data)
  } catch (error) {
    console.error('获取统计信息失败', error)
  }
}

// 重置筛选
const resetFilter = () => {
  filterType.value = ''
  dateRange.value = []
  currentPage.value = 1
  fetchHistory()
}

onMounted(() => {
  fetchBalance()
  fetchHistory()
  fetchStatistics()
})
</script>

<style scoped lang="scss">
.history-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.balance-info {
  font-size: 14px;
  color: #606266;

  .amount {
    font-size: 18px;
    font-weight: bold;
    color: #409eff;
  }
}

.filter-section {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.amount-in {
  color: #67c23a;
  font-weight: bold;
}

.amount-out {
  color: #f56c6c;
  font-weight: bold;
}

.stat-card {
  text-align: center;
}
</style>
