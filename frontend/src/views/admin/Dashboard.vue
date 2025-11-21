<template>
  <div class="admin-dashboard">
    <h2>管理员控制台</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <el-statistic title="学生总数" :value="stats.total_students">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <el-statistic title="课程总数" :value="stats.total_courses">
            <template #prefix>
              <el-icon><Reading /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <el-statistic title="今日选课" :value="stats.today_enrollments">
            <template #prefix>
              <el-icon><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <el-statistic title="交易总额" :value="stats.total_transactions" prefix="¥">
            <template #prefix>
              <el-icon><Money /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>选课趋势（近7天）</span>
          </template>
          <div ref="enrollmentChart" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>院系学生分布</span>
          </template>
          <div ref="departmentChart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近活动 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <span>最近活动</span>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="activity in recentActivities"
          :key="activity.id"
          :timestamp="formatDate(activity.created_at)"
          placement="top"
        >
          <el-card>
            <p>{{ activity.description }}</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { User, Reading, Document, Money } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import request from '@/api/request'
import dayjs from 'dayjs'

const enrollmentChart = ref(null)
const departmentChart = ref(null)
let enrollmentChartInstance = null
let departmentChartInstance = null

const stats = reactive({
  total_students: 0,
  total_courses: 0,
  today_enrollments: 0,
  total_transactions: 0
})

const recentActivities = ref([])

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const { data } = await request.get('/api/v1/admin/statistics')
    Object.assign(stats, data)
  } catch (error) {
    // 使用模拟数据
    stats.total_students = 1256
    stats.total_courses = 89
    stats.today_enrollments = 45
    stats.total_transactions = 125680
  }
}

// 获取最近活动
const fetchActivities = async () => {
  try {
    const { data } = await request.get('/api/v1/admin/activities')
    recentActivities.value = data
  } catch (error) {
    // 模拟数据
    recentActivities.value = [
      { id: 1, description: '学生 张三 选修了 高等数学', created_at: new Date() },
      { id: 2, description: '新课程 Python编程 已发布', created_at: new Date(Date.now() - 3600000) },
      { id: 3, description: '学生 李四 完成了转账 ¥100', created_at: new Date(Date.now() - 7200000) }
    ]
  }
}

// 初始化选课趋势图表
const initEnrollmentChart = () => {
  enrollmentChartInstance = echarts.init(enrollmentChart.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '选课数',
        type: 'line',
        smooth: true,
        data: [120, 132, 101, 134, 90, 230, 210],
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
            ]
          }
        }
      }
    ]
  }
  enrollmentChartInstance.setOption(option)
}

// 初始化院系分布图表
const initDepartmentChart = () => {
  departmentChartInstance = echarts.init(departmentChart.value)
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '学生数',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 335, name: '计算机学院' },
          { value: 310, name: '商学院' },
          { value: 234, name: '文学院' },
          { value: 135, name: '理学院' },
          { value: 242, name: '工学院' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  departmentChartInstance.setOption(option)
}

// 窗口大小变化时重绘图表
const handleResize = () => {
  enrollmentChartInstance?.resize()
  departmentChartInstance?.resize()
}

onMounted(() => {
  fetchStats()
  fetchActivities()
  initEnrollmentChart()
  initDepartmentChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  enrollmentChartInstance?.dispose()
  departmentChartInstance?.dispose()
})
</script>

<style scoped lang="scss">
.admin-dashboard {
  padding: 20px;

  h2 {
    margin-bottom: 20px;
  }
}

.stat-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}
</style>
