/**
 * Vue路由配置
 * @version: v1.0.1
 * @date: 2024-12-06
 */
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 已存在的路由组件
const Welcome = () => import('@/views/Welcome.vue')
const Layout = () => import('@/layout/index.vue')
const Login = () => import('@/views/auth/Login.vue')
const Register = () => import('@/views/auth/Register.vue')
const Dashboard = () => import('@/views/dashboard/index.vue')

// 课程相关组件
const CourseList = () => import('@/views/courses/List.vue')
const MyCourses = () => import('@/views/courses/MyCourses.vue')

// 消息相关组件
const Messages = () => import('@/views/messages/index.vue')
const ComposeMessage = () => import('@/views/messages/Compose.vue')

// 交易相关组件
const TransferMoney = () => import('@/views/transactions/Transfer.vue')

// 暂时注释掉不存在的组件 - 需要后续创建
// const CourseDetail = () => import('@/views/courses/Detail.vue')
// const FriendList = () => import('@/views/friends/List.vue')
// const FriendRequests = () => import('@/views/friends/Requests.vue')
// const FriendRecommendations = () => import('@/views/friends/Recommendations.vue')
// const TransactionHistory = () => import('@/views/transactions/History.vue')
// const Balance = () => import('@/views/transactions/Balance.vue')
// const Inbox = () => import('@/views/messages/Inbox.vue')
// const Sent = () => import('@/views/messages/Sent.vue')
// const Profile = () => import('@/views/profile/index.vue')

const routes = [
  {
    path: '/',
    name: 'Welcome',
    component: Welcome,
    meta: { 
      title: '欢迎页面',
      requiresAuth: false 
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { 
      title: '登录',
      requiresAuth: false 
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { 
      title: '注册',
      requiresAuth: false 
    }
  },
  {
    path: '/app',
    component: Layout,
    redirect: '/app/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { 
          title: '仪表盘',
          icon: 'el-icon-s-home' 
        }
      }
    ]
  },
  {
    path: '/courses',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'CourseList',
        component: CourseList,
        meta: { 
          title: '课程列表',
          icon: 'el-icon-reading' 
        }
      },
      {
        path: 'my-courses',
        name: 'MyCourses',
        component: MyCourses,
        meta: { 
          title: '我的课程',
          icon: 'el-icon-reading' 
        }
      }
    ]
  },
  {
    path: '/messages',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Messages',
        component: Messages,
        meta: { 
          title: '消息中心',
          icon: 'el-icon-message' 
        }
      },
      {
        path: 'compose',
        name: 'ComposeMessage',
        component: ComposeMessage,
        meta: { 
          title: '编写消息',
          icon: 'el-icon-edit' 
        }
      }
    ]
  },
  {
    path: '/transactions',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'transfer',
        name: 'TransferMoney',
        component: TransferMoney,
        meta: { 
          title: '转账汇款',
          icon: 'el-icon-money' 
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { 
      title: '页面不存在' 
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 学生选课系统`
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // 未登录，重定向到登录页
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }
  
  // 已登录用户访问登录页，重定向到首页
  if (authStore.isAuthenticated && (to.path === '/login' || to.path === '/register')) {
    next('/app')
    return
  }
  
  next()
})

export default router 