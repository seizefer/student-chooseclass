<template>
  <div class="page-header">
    <div class="header-content">
      <div class="title-section">
        <el-button
          v-if="showBack"
          :icon="ArrowLeft"
          circle
          @click="goBack"
        />
        <h1 class="page-title">{{ title }}</h1>
        <el-tag v-if="badge" :type="badgeType" size="small">{{ badge }}</el-tag>
      </div>
      <p v-if="description" class="page-description">{{ description }}</p>
    </div>
    <div v-if="$slots.extra" class="header-extra">
      <slot name="extra"></slot>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'

const props = defineProps({
  // 页面标题
  title: {
    type: String,
    required: true
  },
  // 描述信息
  description: {
    type: String,
    default: ''
  },
  // 标签文字
  badge: {
    type: String,
    default: ''
  },
  // 标签类型
  badgeType: {
    type: String,
    default: 'primary'
  },
  // 是否显示返回按钮
  showBack: {
    type: Boolean,
    default: false
  },
  // 自定义返回路径
  backPath: {
    type: String,
    default: ''
  }
})

const router = useRouter()

const goBack = () => {
  if (props.backPath) {
    router.push(props.backPath)
  } else {
    router.back()
  }
}
</script>

<style scoped lang="scss">
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;

  .header-content {
    flex: 1;

    .title-section {
      display: flex;
      align-items: center;
      gap: 12px;

      .page-title {
        margin: 0;
        font-size: 24px;
        font-weight: 600;
        color: #303133;
      }
    }

    .page-description {
      margin: 8px 0 0;
      color: #909399;
      font-size: 14px;
    }
  }

  .header-extra {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}
</style>
