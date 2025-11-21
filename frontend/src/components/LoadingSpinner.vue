<template>
  <div class="loading-spinner" :class="{ 'fullscreen': fullscreen }">
    <el-icon class="spinner-icon" :size="size">
      <Loading />
    </el-icon>
    <span v-if="text" class="loading-text">{{ text }}</span>
  </div>
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue'

defineProps({
  // 加载文字
  text: {
    type: String,
    default: ''
  },
  // 图标大小
  size: {
    type: Number,
    default: 32
  },
  // 是否全屏
  fullscreen: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped lang="scss">
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;

  &.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.9);
    z-index: 9999;
  }

  .spinner-icon {
    animation: spin 1s linear infinite;
    color: var(--el-color-primary);
  }

  .loading-text {
    margin-top: 12px;
    color: #606266;
    font-size: 14px;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
