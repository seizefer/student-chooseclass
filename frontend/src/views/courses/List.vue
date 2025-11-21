<!--
课程列表页面
@version: v1.0.0
@date: 2024-12-06
-->
<template>
  <div class="course-list-container">
    <div class="page-header">
      <h1>📚 课程列表</h1>
      <p>浏览所有可选课程</p>
    </div>
    
    <div class="course-grid">
      <div 
        v-for="course in courses" 
        :key="course.id"
        class="course-card"
      >
        <div class="course-info">
          <h3>{{ course.name }}</h3>
          <p class="course-code">课程代码: {{ course.code }}</p>
          <p class="course-teacher">授课教师: {{ course.teacher }}</p>
          <p class="course-time">上课时间: {{ course.time }}</p>
          <p class="course-credits">学分: {{ course.credits }}</p>
        </div>
        
        <div class="course-actions">
          <el-button type="primary" size="small">
            <el-icon><Plus /></el-icon>
            选课
          </el-button>
          <el-button size="small">
            <el-icon><View /></el-icon>
            详情
          </el-button>
        </div>
      </div>
    </div>
    
    <div v-if="courses.length === 0" class="empty-state">
      <el-icon class="empty-icon"><DocumentRemove /></el-icon>
      <p>暂无课程信息</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, View, DocumentRemove } from '@element-plus/icons-vue'

// 示例课程数据
const courses = ref([
  {
    id: 1,
    name: '高等数学',
    code: 'MATH101',
    teacher: '张教授',
    time: '周一 8:00-10:00',
    credits: 4
  },
  {
    id: 2,
    name: '大学英语',
    code: 'ENG101',
    teacher: '李老师',
    time: '周二 14:00-16:00',
    credits: 3
  },
  {
    id: 3,
    name: '计算机基础',
    code: 'CS101',
    teacher: '王教授',
    time: '周三 10:00-12:00',
    credits: 3
  },
  {
    id: 4,
    name: '数据结构',
    code: 'CS201',
    teacher: '赵老师',
    time: '周四 16:00-18:00',
    credits: 4
  }
])

onMounted(() => {
  // 这里可以调用API获取课程数据
  console.log('课程列表页面已加载')
})
</script>

<style lang="scss" scoped>
.course-list-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
  
  h1 {
    color: #2c3e50;
    margin-bottom: 10px;
    font-size: 2em;
  }
  
  p {
    color: #7f8c8d;
    font-size: 16px;
  }
}

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.course-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid #f0f0f0;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  }
}

.course-info {
  margin-bottom: 15px;
  
  h3 {
    color: #2c3e50;
    margin-bottom: 10px;
    font-size: 1.2em;
  }
  
  p {
    color: #7f8c8d;
    font-size: 14px;
    margin-bottom: 5px;
    
    &.course-code {
      color: #409eff;
      font-weight: 500;
    }
  }
}

.course-actions {
  display: flex;
  gap: 10px;
  
  .el-button {
    flex: 1;
  }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
  
  .empty-icon {
    font-size: 4em;
    margin-bottom: 20px;
    color: #e6e6e6;
  }
  
  p {
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .course-grid {
    grid-template-columns: 1fr;
  }
  
  .course-actions {
    flex-direction: column;
  }
}
</style>