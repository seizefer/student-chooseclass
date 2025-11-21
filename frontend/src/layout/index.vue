<!--
主布局组件
@version: v1.2.0
@date: 2024-12-06
-->
<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <el-drawer
      v-model="mobileMenuOpen"
      :with-header="false"
      size="280px"
      class="mobile-menu"
    >
      <aside class="sidebar">
        <div class="logo">
          <el-icon><School /></el-icon>
          <span>选课系统</span>
        </div>
        
        <el-menu
          :default-active="activeMenu"
          :collapse="false"
          router
          class="sidebar-menu"
        >
          <template v-for="route in menuRoutes" :key="route.name">
            <el-sub-menu 
              v-if="route.children && route.children.length > 1" 
              :index="route.path"
            >
              <template #title>
                <el-icon><component :is="route.meta?.icon || 'Menu'" /></el-icon>
                <span>{{ route.meta?.title }}</span>
              </template>
              
              <el-menu-item
                v-for="child in route.children"
                :key="child.name"
                :index="child.path === '' ? route.path : `${route.path}/${child.path}`"
              >
                <el-icon><component :is="child.meta?.icon || 'Menu'" /></el-icon>
                <span>{{ child.meta?.title }}</span>
              </el-menu-item>
            </el-sub-menu>
            
            <el-menu-item 
              v-else 
              :index="route.children?.[0]?.path === '' ? route.path : route.path"
            >
              <el-icon><component :is="route.meta?.icon || route.children?.[0]?.meta?.icon || 'Menu'" /></el-icon>
              <span>{{ route.meta?.title || route.children?.[0]?.meta?.title }}</span>
            </el-menu-item>
          </template>
        </el-menu>
      </aside>
    </el-drawer>

    <!-- 桌面端侧边栏 -->
    <aside class="sidebar desktop-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="logo">
        <el-icon><School /></el-icon>
        <span v-show="!sidebarCollapsed">选课系统</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="sidebarCollapsed"
        router
        class="sidebar-menu"
      >
        <template v-for="route in menuRoutes" :key="route.name">
          <el-sub-menu 
            v-if="route.children && route.children.length > 1" 
            :index="route.path"
          >
            <template #title>
              <el-icon><component :is="route.meta?.icon || 'Menu'" /></el-icon>
              <span>{{ route.meta?.title }}</span>
            </template>
            
            <el-menu-item
              v-for="child in route.children"
              :key="child.name"
              :index="child.path === '' ? route.path : `${route.path}/${child.path}`"
            >
              <el-icon><component :is="child.meta?.icon || 'Menu'" /></el-icon>
              <span>{{ child.meta?.title }}</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-menu-item 
            v-else 
            :index="route.children?.[0]?.path === '' ? route.path : route.path"
          >
            <el-icon><component :is="route.meta?.icon || route.children?.[0]?.meta?.icon || 'Menu'" /></el-icon>
            <span>{{ route.meta?.title || route.children?.[0]?.meta?.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </aside>

    <!-- 主内容区 -->
    <div class="main-container" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <!-- 头部 -->
      <header class="header">
        <div class="header-left">
          <!-- 移动端菜单按钮 -->
          <el-button
            class="mobile-menu-btn"
            @click="mobileMenuOpen = true"
            text
          >
            <el-icon><Menu /></el-icon>
          </el-button>
          
          <!-- 桌面端折叠按钮 -->
          <el-button
            class="collapse-btn"
            @click="sidebarCollapsed = !sidebarCollapsed"
            text
          >
            <el-icon>
              <component :is="sidebarCollapsed ? 'Expand' : 'Fold'" />
            </el-icon>
          </el-button>
          
          <el-breadcrumb separator="/">
            <el-breadcrumb-item
              v-for="breadcrumb in breadcrumbs"
              :key="breadcrumb.path"
              :to="breadcrumb.path"
            >
              {{ breadcrumb.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 消息通知 -->
          <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="message-badge">
            <el-button text @click="$router.push('/messages/inbox')">
              <el-icon><Bell /></el-icon>
            </el-button>
          </el-badge>
          
          <!-- 用户菜单 -->
          <el-dropdown @command="handleUserMenuCommand">
            <div class="user-info">
              <el-avatar :size="32">
                <el-icon><User /></el-icon>
              </el-avatar>
              <span class="username">{{ authStore.userName }}</span>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 内容区域 -->
      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { 
  School, Menu, Expand, Fold, Bell, User, 
  ArrowDown, Setting, SwitchButton 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 响应式状态
const sidebarCollapsed = ref(false)
const mobileMenuOpen = ref(false)
const unreadCount = ref(0)

// 当前激活的菜单项
const activeMenu = computed(() => {
  return route.path
})

// 过滤菜单路由
const menuRoutes = computed(() => {
  return router.getRoutes().filter(route => {
    return route.meta?.requiresAuth && 
           !route.meta?.hidden && 
           route.path !== '/' &&
           !route.path.includes(':')
  })
})

// 面包屑导航
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta?.title)
  return matched.map(item => ({
    title: item.meta.title,
    path: item.path
  }))
})

// 用户菜单命令处理
const handleUserMenuCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      // TODO: 跳转到设置页面
      break
    case 'logout':
      await authStore.logout()
      router.push('/login')
      break
  }
}

// 获取未读消息数量
const fetchUnreadCount = async () => {
  try {
    // TODO: 调用API获取未读消息数量
    // const response = await http.get('/v1/messages/unread/count')
    // unreadCount.value = response.data.unread_count
  } catch (error) {
    console.error('获取未读消息数量失败:', error)
  }
}

// 监听路由变化，关闭移动端菜单
watch(() => route.path, () => {
  mobileMenuOpen.value = false
})

// 组件挂载时获取未读消息数量
onMounted(() => {
  fetchUnreadCount()
  
  // 定期刷新未读消息数量
  setInterval(fetchUnreadCount, 30000) // 30秒刷新一次
})
</script>

<style lang="scss" scoped>
.layout-container {
  display: flex;
  height: 100vh;
  background-color: var(--bg-light);
}

.sidebar {
  width: 250px;
  background: var(--bg-color);
  border-right: 1px solid var(--border-lighter);
  display: flex;
  flex-direction: column;
  
  &.collapsed {
    width: 64px;
  }
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    border-bottom: 1px solid var(--border-lighter);
    font-size: 18px;
    font-weight: bold;
    color: var(--primary-color);
    
    .el-icon {
      font-size: 24px;
    }
  }
  
  .sidebar-menu {
    flex: 1;
    border-right: none;
    
    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      height: 48px;
      line-height: 48px;
      
      .el-icon {
        margin-right: 8px;
        width: 20px;
        text-align: center;
      }
    }
  }
}

.desktop-sidebar {
  @media (max-width: 768px) {
    display: none;
  }
}

.mobile-menu {
  @media (min-width: 769px) {
    display: none !important;
  }
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 250px;
  transition: margin-left 0.3s ease;
  
  &.sidebar-collapsed {
    margin-left: 64px;
  }
  
  @media (max-width: 768px) {
    margin-left: 0;
  }
}

.header {
  height: 60px;
  background: var(--bg-color);
  border-bottom: 1px solid var(--border-lighter);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .mobile-menu-btn {
      display: none;
      
      @media (max-width: 768px) {
        display: inline-flex;
      }
    }
    
    .collapse-btn {
      @media (max-width: 768px) {
        display: none;
      }
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .message-badge {
      .el-button {
        padding: 8px;
      }
    }
    
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 5px 10px;
      border-radius: 6px;
      transition: background-color 0.3s;
      
      &:hover {
        background-color: var(--bg-lighter);
      }
      
      .username {
        font-size: 14px;
        
        @media (max-width: 768px) {
          display: none;
        }
      }
      
      .dropdown-icon {
        font-size: 12px;
        color: var(--text-secondary);
      }
    }
  }
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: var(--bg-light);
}

// 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style> 