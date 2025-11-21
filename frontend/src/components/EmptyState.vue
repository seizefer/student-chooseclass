<template>
  <div class="empty-state">
    <div class="empty-icon">
      <el-icon :size="64">
        <component :is="icon" />
      </el-icon>
    </div>
    <h3 class="empty-title">{{ title }}</h3>
    <p class="empty-description">{{ description }}</p>
    <div class="empty-action" v-if="actionText">
      <el-button type="primary" @click="$emit('action')">
        {{ actionText }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import {
  Document, User, Message, Bell, ShoppingCart, Reading
} from '@element-plus/icons-vue'

defineProps({
  icon: {
    type: [String, Object],
    default: () => Document
  },
  title: {
    type: String,
    default: '暂无数据'
  },
  description: {
    type: String,
    default: ''
  },
  actionText: {
    type: String,
    default: ''
  }
})

defineEmits(['action'])
</script>

<style scoped lang="scss">
.empty-state {
  padding: 60px 20px;
  text-align: center;

  .empty-icon {
    color: #c0c4cc;
    margin-bottom: 20px;
  }

  .empty-title {
    font-size: 16px;
    color: #606266;
    margin: 0 0 10px;
  }

  .empty-description {
    font-size: 14px;
    color: #909399;
    margin: 0 0 20px;
  }
}
</style>
