# 医院人事系统 - Vue.js前端

## 📦 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Vite** - 下一代前端构建工具
- **Element Plus** - Vue 3组件库
- **Pinia** - Vue状态管理
- **Vue Router** - Vue路由管理
- **Axios** - HTTP客户端

## 🚀 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问: http://localhost:5173

### 3. 构建生产版本

```bash
npm run build
```

构建输出目录: `frontend/dist`

### 4. 预览生产构建

```bash
npm run preview
```

## 📁 项目结构

```
frontend/
├── src/
│   ├── views/           # 页面组件
│   │   ├── Layout.vue      # 主布局
│   │   ├── Login.vue       # 登录页
│   │   ├── Dashboard.vue   # 工作台
│   │   ├── Employees.vue   # 职工管理
│   │   ├── Salary.vue      # 工资管理
│   │   ├── Performance.vue # 绩效管理
│   │   ├── Leave.vue       # 考勤管理
│   │   ├── Recruitment.vue # 招聘管理
│   │   ├── Training.vue    # 培训管理
│   │   ├── Resignation.vue # 离职管理
│   │   └── Backup.vue      # 数据备份
│   ├── router/          # 路由配置
│   │   └── index.js
│   ├── stores/          # Pinia状态管理
│   │   └── user.js
│   ├── utils/           # 工具函数
│   │   └── request.js   # Axios封装
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── index.html           # HTML模板
├── vite.config.js       # Vite配置
└── package.json         # 依赖配置
```

## 🎨 功能特性

### ✅ 已实现
- 响应式布局(支持PC和移动端)
- 侧边栏菜单导航
- 用户登录/登出
- 路由守卫(权限控制)
- Element Plus UI组件
- Axios请求封装
- 错误处理和消息提示
- 职工管理(CRUD)
- 工资条PDF生成
- 数据备份管理

### ⏳ 开发中
- 招聘管理完整界面
- 培训管理完整界面
- 离职管理完整界面
- 绩效管理完整界面
- 考勤管理完整界面

## 🔧 配置说明

### API代理

在 `vite.config.js` 中配置了API代理:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',  // Flask后端地址
      changeOrigin: true,
    },
  },
}
```

### 响应式设计

所有页面都使用了Element Plus的响应式栅格系统:
- `xs`: < 768px (手机)
- `sm`: ≥ 768px (平板)
- `md`: ≥ 992px (桌面)
- `lg`: ≥ 1200px (大桌面)

## 📱 移动端适配

系统采用移动优先的设计理念:

1. **侧边栏**: 在小屏幕下自动折叠
2. **表格**: 横向滚动显示
3. **表单**: 垂直排列输入项
4. **按钮**: 增大触摸区域
5. **字体**: 自适应大小

## 🎯 开发指南

### 添加新页面

1. 在 `src/views/` 创建Vue组件
2. 在 `src/router/index.js` 添加路由
3. 在Layout菜单中添加导航项

示例:

```javascript
// router/index.js
{
  path: 'new-page',
  name: 'NewPage',
  component: () => import('@/views/NewPage.vue'),
  meta: { title: '新页面', icon: 'Document' }
}
```

### API调用

使用封装的request对象:

```javascript
import request from '@/utils/request'

// GET请求
const data = await request.get('/api/employees')

// POST请求
await request.post('/api/employees', { name: '张三' })

// 文件下载
const response = await request.get('/api/export', {
  responseType: 'blob'
})
```

### 状态管理

使用Pinia store:

```javascript
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 获取用户信息
console.log(userStore.userInfo)

// 登录
await userStore.login('admin', 'admin123')

// 登出
userStore.logout()
```

## 🔐 权限控制

路由守卫会自动检查用户登录状态:

```javascript
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth !== false && !token) {
    next('/login')  // 未登录跳转到登录页
  } else {
    next()
  }
})
```

## 🌐 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge
- 移动端浏览器

## 📝 注意事项

1. **后端服务**: 确保Flask后端在 http://localhost:5000 运行
2. **CORS**: 开发环境通过Vite代理解决跨域问题
3. **生产部署**: 构建后将 `dist` 目录部署到Web服务器
4. **环境变量**: 可在 `.env` 文件中配置API地址

## 🚧 后续优化

- [ ] 添加加载骨架屏
- [ ] 实现主题切换
- [ ] 添加国际化支持
- [ ] 完善单元测试
- [ ] 性能优化(懒加载、代码分割)
- [ ] PWA支持

---

**开发文档版本:** v1.0  
**更新时间:** 2026-06-29
