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
const CourseDetail = () => import('@/views/courses/CourseDetail.vue')

// 消息相关组件
const Messages = () => import('@/views/messages/index.vue')
const ComposeMessage = () => import('@/views/messages/Compose.vue')

// 交易相关组件
const TransferMoney = () => import('@/views/transactions/Transfer.vue')

// 个人资料
const Profile = () => import('@/views/profile/index.vue')

// 好友相关组件
const FriendList = () => import('@/views/friends/FriendList.vue')
const FriendRequests = () => import('@/views/friends/FriendRequests.vue')
const FriendRecommendations = () => import('@/views/friends/FriendRecommendations.vue')

// 交易历史
const TransactionHistory = () => import('@/views/transactions/History.vue')

// 通知系统
const Notifications = () => import('@/views/notifications/index.vue')

// 管理面板
const AdminDashboard = () => import('@/views/admin/Dashboard.vue')
const UserManagement = () => import('@/views/admin/UserManagement.vue')
const CourseManagement = () => import('@/views/admin/CourseManagement.vue')

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
    meta: { requiresAuth: true, title: '课程管理', icon: 'el-icon-reading' },
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
      },
      {
        path: ':id',
        name: 'CourseDetail',
        component: CourseDetail,
        meta: {
          title: '课程详情',
          icon: 'el-icon-document'
        }
      }
    ]
  },
  {
    path: '/messages',
    component: Layout,
    meta: { requiresAuth: true, title: '消息中心', icon: 'el-icon-message' },
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
    meta: { requiresAuth: true, title: '转账功能', icon: 'el-icon-money' },
    children: [
      {
        path: 'transfer',
        name: 'TransferMoney',
        component: TransferMoney,
        meta: {
          title: '转账汇款',
          icon: 'el-icon-money'
        }
      },
      {
        path: 'history',
        name: 'TransactionHistory',
        component: TransactionHistory,
        meta: {
          title: '交易记录',
          icon: 'el-icon-document'
        }
      }
    ]
  },
  {
    path: '/profile',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Profile',
        component: Profile,
        meta: {
          title: '个人资料',
          icon: 'el-icon-user'
        }
      }
    ]
  },
  {
    path: '/friends',
    component: Layout,
    meta: { requiresAuth: true, title: '好友系统', icon: 'el-icon-user' },
    children: [
      {
        path: '',
        name: 'FriendList',
        component: FriendList,
        meta: {
          title: '好友列表',
          icon: 'el-icon-user'
        }
      },
      {
        path: 'requests',
        name: 'FriendRequests',
        component: FriendRequests,
        meta: {
          title: '好友请求',
          icon: 'el-icon-bell'
        }
      },
      {
        path: 'recommendations',
        name: 'FriendRecommendations',
        component: FriendRecommendations,
        meta: {
          title: '推荐好友',
          icon: 'el-icon-star-on'
        }
      }
    ]
  },
  {
    path: '/notifications',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Notifications',
        component: Notifications,
        meta: {
          title: '通知中心',
          icon: 'el-icon-bell'
        }
      }
    ]
  },
  {
    path: '/admin',
    component: Layout,
    meta: { requiresAuth: true, requiresAdmin: true, title: '管理面板', icon: 'el-icon-setting' },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: AdminDashboard,
        meta: {
          title: '管理控制台',
          icon: 'el-icon-setting'
        }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: UserManagement,
        meta: {
          title: '用户管理',
          icon: 'el-icon-user'
        }
      },
      {
        path: 'courses',
        name: 'CourseManagement',
        component: CourseManagement,
        meta: {
          title: '课程管理',
          icon: 'el-icon-reading'
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