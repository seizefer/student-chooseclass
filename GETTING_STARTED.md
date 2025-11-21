# 本地运行指南

## 环境要求

### 必需软件
- **Node.js** >= 16.0.0 (推荐 18.x)
- **Python** >= 3.8 (推荐 3.9+)
- **MySQL** >= 8.0
- **npm** 或 **yarn**

### 检查版本
```bash
node -v      # v18.x.x
python --version  # Python 3.9.x
mysql --version   # mysql  Ver 8.0.x
```

---

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd student-chooseclass
```

### 2. 数据库设置

#### 2.1 创建数据库
```bash
mysql -u root -p
```

```sql
CREATE DATABASE student_course_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE student_course_system;
source database/init.sql;
```

#### 2.2 配置数据库连接
创建 `backend/.env` 文件：
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=student_course_system

# JWT配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
DEBUG=True
```

### 3. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境 (推荐)
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
python main.py
# 或使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端服务运行在: http://localhost:8000
API文档: http://localhost:8000/docs

### 4. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
# 或
yarn install

# 启动开发服务器
npm run dev
# 或
yarn dev
```

前端服务运行在: http://localhost:5173

---

## 项目结构

```
student-chooseclass/
├── backend/                 # 后端代码
│   ├── main.py             # 入口文件
│   ├── requirements.txt    # Python依赖
│   └── app/
│       ├── api/v1/         # API路由
│       ├── core/           # 配置
│       ├── db/             # 数据库
│       ├── schemas/        # 数据模型
│       └── utils/          # 工具函数
├── frontend/               # 前端代码
│   ├── package.json        # Node依赖
│   ├── vite.config.js      # Vite配置
│   └── src/
│       ├── views/          # 页面组件
│       ├── router/         # 路由配置
│       ├── stores/         # 状态管理
│       └── api/            # API封装
├── database/               # 数据库脚本
│   └── init.sql           # 初始化SQL
├── docs/                   # 项目文档
├── tests/                  # 测试文件
└── uploads/                # 上传文件目录 (自动创建)
```

---

## 功能模块

### 已完成功能

#### 用户系统
- ✅ 用户注册/登录 (JWT认证)
- ✅ 个人资料管理
- ✅ 头像上传
- ✅ 密码修改
- ✅ 邮箱验证
- ✅ 密码重置

#### 课程系统
- ✅ 课程列表/详情
- ✅ 课程搜索筛选
- ✅ 学生选课/退课
- ✅ 成绩查看
- ✅ 时间冲突检测
- ✅ 先修课程验证

#### 社交系统
- ✅ 好友请求/管理
- ✅ 好友推荐
- ✅ 私信消息
- ✅ WebSocket实时通信

#### 财务系统
- ✅ 账户余额
- ✅ 好友转账
- ✅ 交易记录

#### 管理系统
- ✅ 管理员面板
- ✅ 用户管理
- ✅ 课程管理
- ✅ 统计图表

#### 通知系统
- ✅ 通知中心
- ✅ 未读提醒
- ✅ 实时推送

---

## API 端点

### 认证 `/api/v1/auth`
- POST `/login` - 登录
- POST `/register` - 注册
- POST `/refresh` - 刷新令牌
- GET `/me` - 当前用户

### 课程 `/api/v1/courses`
- GET `/` - 课程列表
- GET `/{id}` - 课程详情
- POST `/` - 创建课程
- PUT `/{id}` - 更新课程
- DELETE `/{id}` - 删除课程

### 选课 `/api/v1/enrollments`
- POST `/` - 选课
- DELETE `/{id}` - 退课
- GET `/my-courses` - 我的课程

### 好友 `/api/v1/friendships`
- POST `/request` - 发送请求
- GET `/list` - 好友列表
- GET `/recommendations` - 推荐

### 消息 `/api/v1/messages`
- POST `/send` - 发送
- GET `/inbox` - 收件箱
- GET `/sent` - 发件箱

### 转账 `/api/v1/transactions`
- POST `/transfer` - 转账
- GET `/balance` - 余额
- GET `/history` - 记录

### 通知 `/api/v1/notifications`
- GET `/` - 通知列表
- PUT `/{id}/read` - 标记已读
- DELETE `/clear` - 清空

### WebSocket `/api/v1/ws`
- WS连接: `ws://localhost:8000/api/v1/ws?token=<jwt>`

完整API文档: http://localhost:8000/docs

---

## 默认账号

初始化数据库后，可使用以下测试账号：

| 角色 | 学号/用户名 | 密码 |
|------|------------|------|
| 学生 | 2021001 | 123456 |
| 管理员 | admin | admin123 |

> 注意：正式环境请修改默认密码

---

## 常见问题

### 1. 数据库连接失败
- 检查 MySQL 服务是否启动
- 检查 `.env` 配置是否正确
- 检查数据库用户权限

### 2. 前端无法连接后端
- 确认后端服务在 8000 端口运行
- 检查 `vite.config.js` 中的代理配置
- 检查 CORS 设置

### 3. npm install 失败
- 尝试清除缓存: `npm cache clean --force`
- 删除 `node_modules` 重新安装
- 检查 Node.js 版本

### 4. Python 依赖安装失败
- 确保使用虚拟环境
- 升级 pip: `pip install --upgrade pip`
- 检查 Python 版本

---

## 开发命令

### 前端
```bash
npm run dev      # 开发服务器
npm run build    # 生产构建
npm run preview  # 预览构建
npm run lint     # 代码检查
```

### 后端
```bash
python main.py                    # 启动服务
pytest tests/                     # 运行测试
uvicorn main:app --reload        # 热重载开发
```

---

## 生产部署

### 前端构建
```bash
cd frontend
npm run build
# 产出在 dist/ 目录
```

### 后端部署
```bash
# 使用 gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Docker 部署 (计划中)
```bash
docker-compose up -d
```

---

## 技术栈

### 前端
- Vue.js 3
- Vue Router 4
- Pinia
- Element Plus
- Axios
- ECharts
- Vite
- Sass

### 后端
- FastAPI
- Python 3.8+
- MySQL 8.0
- JWT认证
- WebSocket
- Pydantic

---

## 联系方式

如有问题，请提交 Issue 或联系开发者。
