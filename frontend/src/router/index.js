import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/views/Layout.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台', icon: 'Odometer' }
      },
      {
        path: 'employees',
        name: 'Employees',
        component: () => import('@/views/Employees.vue'),
        meta: { title: '职工管理', icon: 'User' }
      },
      {
        path: 'salary',
        name: 'Salary',
        component: () => import('@/views/Salary.vue'),
        meta: { title: '工资管理', icon: 'Money' }
      },
      {
        path: 'salary-config',
        name: 'SalaryConfig',
        component: () => import('@/views/SalaryConfig.vue'),
        meta: { title: '工资标准配置', icon: 'Setting' }
      },
      {
        path: 'performance',
        name: 'Performance',
        component: () => import('@/views/Performance.vue'),
        meta: { title: '绩效管理', icon: 'TrendCharts' }
      },
      {
        path: 'leave',
        name: 'Leave',
        component: () => import('@/views/Leave.vue'),
        meta: { title: '考勤管理', icon: 'Calendar' }
      },
      {
        path: 'recruitment',
        name: 'Recruitment',
        component: () => import('@/views/Recruitment.vue'),
        meta: { title: '招聘管理', icon: 'Briefcase' }
      },
      {
        path: 'training',
        name: 'Training',
        component: () => import('@/views/Training.vue'),
        meta: { title: '培训管理', icon: 'Reading' }
      },
      {
        path: 'resignation',
        name: 'Resignation',
        component: () => import('@/views/Resignation.vue'),
        meta: { title: '离职管理', icon: 'SwitchButton' }
      },
      {
        path: 'backup',
        name: 'Backup',
        component: () => import('@/views/Backup.vue'),
        meta: { title: '数据备份', icon: 'FolderOpened' }
      },
      {
        path: 'self-service',
        name: 'EmployeeSelfService',
        component: () => import('@/views/EmployeeSelfService.vue'),
        meta: { title: '自助服务', icon: 'UserFilled' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth !== false && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
