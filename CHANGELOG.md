# 更新日志 / Changelog

## [v1.3.0] - 2024-11-21

### 新增 Added
- ✅ **项目结构优化**
  - 删除 node_modules (15,777 文件, 193MB)
  - 删除重复的 app/ 目录
  - 创建 .gitignore 文件
  - 整理测试文件到 tests/ 目录
  - 整理文档到 docs/ 目录
  - 项目从 15,882 文件精简到 79 文件

- ✅ **个人资料管理** (profile/index.vue)
  - 用户信息查看与编辑
  - 头像上传功能
  - 密码修改功能
  - 邮箱验证状态

- ✅ **好友系统完整UI** (friends/*.vue)
  - 好友列表管理 (FriendList.vue)
  - 好友请求处理 (FriendRequests.vue)
  - 好友推荐功能 (FriendRecommendations.vue)

- ✅ **交易记录系统** (transactions/History.vue)
  - 交易历史查询
  - 筛选与分页
  - 统计信息展示

- ✅ **通知中心** (notifications/index.vue + notifications.py)
  - 通知列表展示
  - 未读/已读状态管理
  - 按类型筛选
  - 全部已读/清空功能

- ✅ **管理员面板** (admin/*.vue)
  - 管理控制台 (Dashboard.vue) - ECharts 图表
  - 用户管理 (UserManagement.vue) - CRUD 操作
  - 课程管理 (CourseManagement.vue) - 含先修课程

- ✅ **文件上传系统** (upload.py)
  - 头像上传 (JPG/PNG/GIF/WebP, 2MB限制)
  - 课程资料上传 (PDF/Word, 10MB限制)
  - 文件获取与删除

- ✅ **密码重置流程** (password_reset.py)
  - 忘记密码邮件发送
  - 重置令牌验证
  - 新密码设置

- ✅ **邮箱验证** (password_reset.py)
  - 发送验证邮件
  - 令牌验证
  - 验证状态更新

- ✅ **WebSocket 实时通信** (websocket.py)
  - 连接管理器
  - 实时聊天消息
  - 在线状态检测
  - 消息已读回执
  - 系统通知推送

- ✅ **课程验证工具** (course_validation.py)
  - 时间冲突检测
  - 先修课程验证
  - 容量检查
  - 综合选课验证

### 修改 Changed
- 🔄 版本号升级到 v1.3.0
- 🔄 前端路由配置更新 (新增 9 个路由)
- 🔄 后端 API 路由更新 (新增 4 个模块)

### 技术改进 Technical Improvements
- 🎨 **前端组件开发**
  - 9 个新 Vue 组件
  - Element Plus UI 组件库
  - ECharts 图表集成
  - dayjs 日期处理
- 🛡️ **后端功能扩展**
  - 5 个新 API 模块
  - WebSocket 支持
  - 文件上传处理
  - 令牌管理系统
- 📊 **项目清理**
  - 代码量减少 99%
  - 结构更清晰
  - 开发体验提升

### 重要文件版本信息 File Versions
- `frontend/src/views/profile/index.vue` - v1.3.0 (新增)
- `frontend/src/views/friends/FriendList.vue` - v1.3.0 (新增)
- `frontend/src/views/friends/FriendRequests.vue` - v1.3.0 (新增)
- `frontend/src/views/friends/FriendRecommendations.vue` - v1.3.0 (新增)
- `frontend/src/views/transactions/History.vue` - v1.3.0 (新增)
- `frontend/src/views/notifications/index.vue` - v1.3.0 (新增)
- `frontend/src/views/admin/Dashboard.vue` - v1.3.0 (新增)
- `frontend/src/views/admin/UserManagement.vue` - v1.3.0 (新增)
- `frontend/src/views/admin/CourseManagement.vue` - v1.3.0 (新增)
- `backend/app/api/v1/endpoints/notifications.py` - v1.3.0 (新增)
- `backend/app/api/v1/endpoints/upload.py` - v1.3.0 (新增)
- `backend/app/api/v1/endpoints/password_reset.py` - v1.3.0 (新增)
- `backend/app/api/v1/endpoints/websocket.py` - v1.3.0 (新增)
- `backend/app/utils/course_validation.py` - v1.3.0 (新增)

### API端点更新 API Endpoints
```
通知系统 (notifications):
  GET    /api/v1/notifications              获取通知列表
  GET    /api/v1/notifications/unread/count 未读数量
  PUT    /api/v1/notifications/{id}/read    标记已读
  PUT    /api/v1/notifications/read-all     全部已读
  DELETE /api/v1/notifications/{id}         删除通知
  DELETE /api/v1/notifications/clear        清空通知
  POST   /api/v1/notifications              创建通知(管理员)

文件上传 (upload):
  POST   /api/v1/upload/avatar              上传头像
  POST   /api/v1/upload/course-material     上传课程资料
  GET    /api/v1/upload/files/{category}/{filename} 获取文件
  DELETE /api/v1/upload/files/{category}/{filename} 删除文件

密码管理 (password):
  POST   /api/v1/password/forgot-password   忘记密码
  POST   /api/v1/password/verify-reset-token 验证令牌
  POST   /api/v1/password/reset-password    重置密码
  POST   /api/v1/password/send-verification 发送验证邮件
  POST   /api/v1/password/verify-email      验证邮箱

实时通信 (websocket):
  WS     /api/v1/ws                         WebSocket连接
  GET    /api/v1/online-count               在线用户数
  GET    /api/v1/online-users               在线用户列表
  GET    /api/v1/is-online/{user_id}        检查用户在线

总计API端点: 60+ 个 (新增20个)
```

### 功能特性 Features
- 👤 **个人中心** - 完整的用户资料管理
- 🤝 **好友管理** - 好友列表、请求、推荐
- 💰 **交易记录** - 历史查询与统计
- 🔔 **通知中心** - 多类型通知管理
- 🛠️ **管理面板** - 用户/课程管理与统计
- 📁 **文件上传** - 头像与课程资料
- 🔐 **密码重置** - 完整的找回密码流程
- 📧 **邮箱验证** - 账号安全验证
- 💬 **实时通信** - WebSocket 消息推送
- ⚡ **冲突检测** - 课程时间与先修验证

---

## [v1.2.0] - 2024-12-06

### 新增 Added
- ✅ **完整前端页面开发**
  - Vue.js 3 主布局组件 (layout/index.vue)
  - 登录注册页面完整实现
  - 仪表盘首页与数据概览
  - 404错误页面设计
  - 响应式侧边栏导航
- ✅ **学生管理系统** (students.py v1.2.0)
  - 学生个人资料查看与更新
  - 密码修改功能
  - 学生列表管理（管理员）
  - 学生状态管理
  - 学生统计信息
- ✅ **前端状态管理完善**
  - Pinia认证状态管理 (stores/auth.js)
  - 全局样式系统 (style/main.scss)
  - 路由守卫与权限控制
  - API请求封装与拦截器
- ✅ **用户界面优化**
  - 现代化设计风格
  - CSS变量与主题系统
  - 响应式布局设计
  - 动画效果与交互体验

### 修改 Changed
- 🔄 版本号全面升级到v1.2.0
  - 主应用 (main.py v1.2.0)
  - 配置文件 (config.py v1.2.0)
  - API路由 (api.py v1.2.0)
  - 前端项目 (package.json v1.2.0)
- 🔄 项目描述更新
  - 从"在线大学生选课系统"升级为"社交化学习平台"
  - 前端描述增加"完整UI界面"标识

### 技术改进 Technical Improvements
- 🎨 **前端架构完善**
  - 组件化开发模式
  - 状态管理规范化
  - 路由配置标准化
  - 样式管理体系化
- 🛡️ **用户体验增强**
  - 表单验证与反馈
  - 加载状态提示
  - 错误处理优化
  - 响应式适配
- 📱 **移动端支持**
  - 移动端导航菜单
  - 触摸友好的交互
  - 屏幕尺寸适配
- 🔐 **安全性提升**
  - 前端路由守卫
  - 权限状态检查
  - 登录状态持久化

### 重要文件版本信息 File Versions
- `backend/main.py` - v1.2.0
- `backend/app/core/config.py` - v1.2.0
- `backend/app/api/v1/api.py` - v1.2.0
- `backend/app/api/v1/endpoints/students.py` - v1.2.0 (新增)
- `frontend/package.json` - v1.2.0
- `frontend/src/stores/auth.js` - v1.2.0 (新增)
- `frontend/src/style/main.scss` - v1.2.0 (新增)
- `frontend/src/layout/index.vue` - v1.2.0 (新增)
- `frontend/src/views/auth/Login.vue` - v1.2.0 (新增)
- `frontend/src/views/auth/Register.vue` - v1.2.0 (新增)
- `frontend/src/views/dashboard/index.vue` - v1.2.0 (新增)
- `frontend/src/views/error/404.vue` - v1.2.0 (新增)
- `start_backend.ps1` - v1.2.0

### API端点更新 API Endpoints
```
学生管理 (students) - 新增:
  GET    /api/v1/students/profile          获取个人资料
  PUT    /api/v1/students/profile          更新个人资料
  PUT    /api/v1/students/password         修改密码
  GET    /api/v1/students/list             学生列表(管理员)
  PUT    /api/v1/students/{id}/status      更新学生状态(管理员)
  GET    /api/v1/students/statistics       学生统计(管理员)

总计API端点: 40个 (新增6个)
```

### 功能特性 Features
- 🎨 **现代化前端界面** - Vue3 + Element Plus + 响应式设计
- 👤 **个人资料管理** - 完整的学生信息管理系统
- 🔐 **安全认证体系** - 前后端一体化权限控制
- 📱 **移动端友好** - 全面的响应式适配
- 🎯 **用户体验优化** - 现代化交互设计与动画效果

### 开发进度 Development Progress

#### ✅ v1.2.0 已完成
- [x] 完整前端页面开发
- [x] 学生个人资料管理
- [x] 用户界面优化
- [x] 前后端功能集成
- [x] 响应式设计实现

---

## [v1.1.0] - 2024-12-06

### 新增 Added
- ✅ **好友系统完整功能** (friendships.py)
  - 好友申请发送与接收
  - 好友申请审批（接受/拒绝）
  - 好友列表查看与管理
  - 智能好友推荐算法
  - 好友关系删除功能
- ✅ **转账系统核心功能** (transactions.py)
  - 好友间转账功能
  - 账户余额查询
  - 转账记录查看
  - 风险控制与限额管理
  - 转账统计分析
- ✅ **消息系统全面功能** (messages.py)
  - 消息发送与接收
  - 收件箱与发件箱管理
  - 消息状态管理（已读/未读）
  - 消息搜索与分页
  - 未读消息数量统计
- ✅ **前端Vue.js项目初始化**
  - Vue.js 3 + Element Plus项目架构
  - Vite构建配置
  - 前端项目结构搭建

### 修改 Changed
- 🔄 API路由系统重构
  - 新增3个主要功能模块路由
  - 优化路由标签分类
- 🔄 版本号升级到v1.1.0
  - 主应用版本更新
  - 配置文件版本同步
  - 健康检查功能列表更新

### 技术改进 Technical Improvements
- 🛡️ 增强业务安全控制
  - 好友关系验证
  - 转账风险控制
  - 消息权限管理
- 📊 完善数据验证机制
  - 金额限制验证
  - 消息长度限制
  - 好友数量限制
- 🔐 强化权限控制体系
  - 多层权限验证
  - 业务规则检查
- 📝 改进事务管理
  - 转账事务安全
  - 数据一致性保证

### 重要文件版本信息 File Versions
- `backend/main.py` - v1.1.0
- `backend/app/core/config.py` - v1.1.0
- `backend/app/api/v1/api.py` - v1.1.0
- `backend/app/api/v1/endpoints/friendships.py` - v1.0.0
- `backend/app/api/v1/endpoints/transactions.py` - v1.0.0
- `backend/app/api/v1/endpoints/messages.py` - v1.0.0
- `frontend/package.json` - v1.0.0
- `frontend/vite.config.js` - v1.0.0
- `frontend/src/main.js` - v1.0.0
- `frontend/src/App.vue` - v1.0.0

### API端点统计 API Endpoints
```
好友系统 (friendships):
  POST   /api/v1/friendships/request        发送好友申请
  PUT    /api/v1/friendships/{id}/accept    接受好友申请
  PUT    /api/v1/friendships/{id}/reject    拒绝好友申请
  GET    /api/v1/friendships/list           获取好友列表
  GET    /api/v1/friendships/requests       获取好友申请列表
  GET    /api/v1/friendships/recommendations 获取好友推荐
  DELETE /api/v1/friendships/{id}           删除好友关系

转账系统 (transactions):
  POST   /api/v1/transactions/transfer      创建转账
  GET    /api/v1/transactions/balance       查询余额
  GET    /api/v1/transactions/history       转账记录
  GET    /api/v1/transactions/statistics    转账统计

消息系统 (messages):
  POST   /api/v1/messages/send               发送消息
  GET    /api/v1/messages/inbox              收件箱
  GET    /api/v1/messages/sent               发件箱
  GET    /api/v1/messages/{id}               消息详情
  PUT    /api/v1/messages/{id}/status        更新消息状态
  DELETE /api/v1/messages/{id}               删除消息
  GET    /api/v1/messages/unread/count       未读消息数
```

### 功能特性 Features
- 🤝 **社交网络功能** - 好友系统构建学生社交圈
- 💰 **虚拟转账系统** - 安全的好友间资金流转
- 📨 **实时消息通讯** - 高效的消息传递系统
- 🎯 **智能推荐** - 基于算法的好友推荐
- 🔒 **风险控制** - 多层次的安全防护机制

---

## [v1.0.1] - 2024-12-06

### 新增 Added
- ✅ 完善课程管理API端点 (courses.py)
  - 课程增删改查功能
  - 课程搜索和分页
  - 课程状态管理
  - 选课人数统计
- ✅ 添加院系管理功能 (departments.py)
  - 院系增删改查
  - 院系学生和课程统计
  - 权限控制和数据验证
- ✅ 实现选课系统核心功能 (enrollments.py)
  - 学生选课和退课
  - 成绩录入和查询
  - 选课状态管理
  - 选课统计分析
- ✅ 版本管理系统
  - 版本号标注机制
  - 更新日志追踪
  - 文件版本信息

### 修改 Changed
- 🔄 优化数据库连接管理
  - 改进事务处理
  - 增强错误处理
- 🔄 改进API响应格式
  - 统一响应模型
  - 增强错误信息
- 🔄 更新版本号到v1.0.1
  - 主应用版本更新
  - 配置文件版本同步

### 技术改进 Technical Improvements
- 🛡️ 增强SQL注入防护
- 📊 完善数据验证机制
- 🔐 强化权限控制
- 📝 改进事务管理
- 🐛 优化错误处理

### 重要文件版本信息 File Versions
- `backend/main.py` - v1.0.1
- `backend/app/core/config.py` - v1.0.1
- `backend/app/api/v1/endpoints/courses.py` - v1.0.1
- `backend/app/api/v1/endpoints/departments.py` - v1.0.1
- `backend/app/api/v1/endpoints/enrollments.py` - v1.0.1

### API端点统计 API Endpoints
```
课程管理 (courses):
  GET    /api/v1/courses/           - 获取课程列表(分页/搜索)
  GET    /api/v1/courses/{id}       - 获取课程详情
  POST   /api/v1/courses/           - 创建课程(管理员)
  PUT    /api/v1/courses/{id}       - 更新课程(管理员)
  DELETE /api/v1/courses/{id}       - 删除课程(管理员)

院系管理 (departments):
  GET    /api/v1/departments/       - 获取院系列表
  GET    /api/v1/departments/{id}   - 获取院系详情
  POST   /api/v1/departments/       - 创建院系(管理员)
  PUT    /api/v1/departments/{id}   - 更新院系(管理员)
  DELETE /api/v1/departments/{id}   - 删除院系(管理员)
  GET    /api/v1/departments/{id}/students - 获取院系学生列表
  GET    /api/v1/departments/{id}/courses  - 获取院系课程列表

选课管理 (enrollments):
  POST   /api/v1/enrollments/       - 学生选课
  DELETE /api/v1/enrollments/{id}   - 学生退课
  GET    /api/v1/enrollments/my-courses - 查看我的选课
  PUT    /api/v1/enrollments/{id}/grade - 录入成绩(管理员)
  GET    /api/v1/enrollments/course/{id} - 查看课程选课列表(管理员)
  GET    /api/v1/enrollments/statistics  - 选课统计(管理员)
```

---

## [v1.0.0] - 2024-12-06

### 新增 Added
- 项目初始化
- 数据库设计与初始化脚本
- FastAPI基础架构
- MySQL命令行CRUD客户端
- 用户认证系统（JWT）
- 基础安全防护（SQL注入防护）
- API文档自动生成

### 重要文件版本信息 File Versions
- `database/init.sql` - v1.0.0
- `backend/main.py` - v1.0.0
- `backend/app/core/config.py` - v1.0.0
- `backend/app/db/mysql_client.py` - v1.0.0
- `backend/app/api/v1/endpoints/auth.py` - v1.0.0
- `backend/app/utils/security.py` - v1.0.0
- `backend/app/schemas/auth.py` - v1.0.0
- `backend/app/schemas/common.py` - v1.0.0

### 技术栈 Tech Stack
- Backend: FastAPI + Python 3.8+
- Database: MySQL 8.0+ (命令行CRUD)
- Authentication: JWT + bcrypt
- Documentation: OpenAPI/Swagger

### 功能特性 Features
- 🔐 用户认证与授权
- 📊 完整的数据库设计
- 🛡️ SQL注入防护
- 📝 事务管理
- 📖 自动API文档生成

---

### 开发进度 Development Progress

#### ✅ 已完成 (Completed)
- [x] 项目架构搭建
- [x] 数据库设计
- [x] 用户认证系统
- [x] 课程管理功能
- [x] 院系管理功能
- [x] 选课系统功能
- [x] 版本管理系统
- [x] 好友系统开发
- [x] 转账功能开发
- [x] 消息系统开发
- [x] 前端Vue.js架构
- [x] 完整前端页面开发
- [x] 学生管理功能

#### 🔄 进行中 (In Progress)
- [ ] 管理员功能完善
- [ ] 系统集成测试
- [ ] 性能优化

#### ⏳ 计划中 (Planned)
- [ ] 系统部署文档
- [ ] 用户手册编写
- [ ] 性能监控系统 