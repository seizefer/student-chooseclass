# 在线大学生选课系统 (Student Course Selection System)

> **版本**: v1.1.0  
> **更新日期**: 2024-12-06  
> **技术栈**: FastAPI + Python 3.8+ + MySQL 8.0+ (命令行CRUD) + Vue.js 3

## 🎯 项目概述

这是一个基于FastAPI + Vue.js的在线大学生选课系统，支持学生选课、**好友系统**、**转账功能**、**消息系统**等高级功能。**特别采用MySQL命令行CRUD操作**，无ORM依赖，展示了原生SQL操作的完整实现。

## ✨ 功能特性

### 🔐 已实现功能 (v1.1.0)
- ✅ **用户认证与授权** - JWT令牌 + bcrypt加密 + 登录日志
- ✅ **课程管理系统** - 增删改查 + 搜索分页 + 状态管理
- ✅ **院系管理功能** - 完整CRUD + 统计信息 + 权限控制
- ✅ **选课系统** - 选课/退课 + 成绩管理 + 人数限制 + 统计分析
- ✅ **好友系统** 🆕 - 好友申请/管理 + 智能推荐 + 社交网络
- ✅ **转账系统** 🆕 - 安全转账 + 余额查询 + 风险控制 + 限额管理
- ✅ **消息系统** 🆕 - 消息收发 + 状态管理 + 搜索分页
- ✅ **MySQL命令行CRUD** - 防SQL注入 + 事务管理 + 连接池
- ✅ **API文档自动生成** - Swagger/ReDoc + OpenAPI规范
- ✅ **版本管理系统** - 文件版本标注 + 更新日志追踪
- ✅ **前端Vue.js架构** 🆕 - Vue3 + Element Plus + 路由配置

### 🚧 开发中功能
- 🔄 前端页面组件开发
- 🔄 学生信息管理完善
- 🔄 管理员功能扩展

### ⏳ 计划功能
- 📱 完整前端界面开发
- 🔗 前后端功能集成
- 🧪 系统集成测试
- 🚀 部署文档编写

## 🏗️ 技术架构

### 技术栈
- **后端**: FastAPI + Python 3.8+ + uvicorn
- **数据库**: MySQL 8.0+ (纯命令行操作，无ORM)
- **认证**: JWT + bcrypt + OAuth2
- **前端**: Vue.js 3 + Element Plus + Vite
- **文档**: 自动生成OpenAPI/Swagger文档

### 架构亮点
- 🛡️ **安全防护** - SQL注入防护 + 参数化查询 + 权限控制
- 📊 **数据管理** - 事务管理 + 连接池 + 触发器 + 存储过程
- 🏗️ **模块化设计** - 清晰分层 + 统一响应 + 异常处理
- 📖 **开发友好** - 类型提示 + 数据验证 + 热重载 + 版本管理
- 🎨 **现代前端** - Vue3组合式API + Element Plus + 响应式设计

## 📂 项目结构

```
student-chooseclass/
├── 📄 CHANGELOG.md              # 版本更新日志
├── 📄 README.md                 # 项目文档  
├── 📄 test_api.py               # API测试脚本
├── 📄 start_demo.py             # 演示启动脚本
├── 📄 start_backend.ps1         # Windows后端启动脚本 🆕
│
├── 🗄️ database/                 # 数据库相关
│   └── init.sql                # 数据库初始化脚本 (10张表+视图+触发器)
│
├── 🔧 backend/                  # 后端服务
│   ├── main.py                 # 主应用入口 (v1.1.0)
│   ├── requirements.txt        # Python依赖包
│   │
│   └── app/                    # 应用模块
│       ├── core/               # 核心配置
│       │   └── config.py       # 系统配置 (v1.1.0)
│       ├── db/                 # 数据库层
│       │   └── mysql_client.py # MySQL命令行客户端 (v1.0.0)
│       ├── api/v1/             # API版本1
│       │   ├── api.py          # 路由汇总 (v1.1.0)
│       │   └── endpoints/      # API端点
│       │       ├── auth.py         # 认证API (v1.0.0) ✅
│       │       ├── courses.py      # 课程管理API (v1.0.1) ✅
│       │       ├── departments.py  # 院系管理API (v1.0.1) ✅
│       │       ├── enrollments.py  # 选课管理API (v1.0.1) ✅
│       │       ├── friendships.py  # 好友系统API (v1.0.0) ✅ 🆕
│       │       ├── transactions.py # 转账系统API (v1.0.0) ✅ 🆕
│       │       ├── messages.py     # 消息系统API (v1.0.0) ✅ 🆕
│       │       ├── students.py     # 学生管理API 🔄
│       │       └── admin.py        # 管理员API 🔄
│       ├── schemas/            # 数据模式
│       │   ├── common.py       # 通用模式 (v1.0.0) ✅
│       │   └── auth.py         # 认证模式 (v1.0.0) ✅
│       └── utils/              # 工具函数
│           └── security.py     # 安全工具 (v1.0.0) ✅
│
└── 🎨 frontend/                # 前端应用 🆕
    ├── package.json            # 项目依赖 (v1.0.0)
    ├── vite.config.js          # Vite配置 (v1.0.0)
    │
    └── src/                    # 源代码
        ├── main.js             # 应用入口 (v1.0.0)
        ├── App.vue             # 主组件 (v1.0.0)
        ├── router/             # 路由配置
        │   └── index.js        # 路由定义 (v1.0.0)
        ├── api/                # API服务
        │   └── request.js      # 请求封装 (v1.0.0)
        ├── stores/             # 状态管理 🔄
        ├── views/              # 页面组件 🔄
        ├── components/         # 通用组件 🔄
        ├── layout/             # 布局组件 🔄
        ├── utils/              # 工具函数 🔄
        └── style/              # 样式文件 🔄
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- MySQL 8.0+
- Node.js 16+ (前端开发)

### 1. 数据库初始化
```bash
# 登录MySQL并创建数据库
mysql -u root -p < database/init.sql
```

### 2. 后端启动

#### Windows PowerShell方式 (推荐)
```powershell
# 使用Windows启动脚本
.\start_backend.ps1
```

#### 手动方式
```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务 (开发模式)
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 或直接运行
python main.py
```

### 3. 前端启动 🆕
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问服务
- 🏠 **后端API**: http://localhost:8000/
- 🎨 **前端应用**: http://localhost:3000/ 
- 📚 **API文档**: http://localhost:8000/docs  
- 📖 **交互式文档**: http://localhost:8000/redoc
- ❤️ **健康检查**: http://localhost:8000/health

### 5. API测试
```bash
# 运行测试脚本
python test_api.py

# 或运行演示
python start_demo.py
```

## 📊 数据库设计

### 核心数据表 (10张)
1. **departments** - 院系信息表
2. **students** - 学生信息表  
3. **administrators** - 管理员表
4. **courses** - 课程信息表
5. **enrollments** - 选课记录表
6. **friendships** - 好友关系表 🆕
7. **transactions** - 转账记录表 🆕
8. **messages** - 消息记录表 🆕
9. **login_logs** - 登录记录表
10. **system_config** - 系统配置表

### 数据库特性
- 🔗 **外键约束** - 确保数据完整性
- 📇 **索引优化** - 提升查询性能
- 🔄 **触发器** - 自动更新选课人数
- 👁️ **视图** - 简化复杂查询
- 📦 **存储过程** - 好友推荐算法

## 🔗 API端点列表

### 🔐 认证相关 (`/api/v1/auth/`)
| 方法 | 端点 | 功能 | 权限 |
|------|------|------|------|
| POST | `/login` | 用户登录 | 公开 |
| POST | `/register` | 学生注册 | 公开 |
| GET | `/me` | 获取当前用户信息 | 登录用户 |
| POST | `/refresh` | 刷新访问令牌 | 登录用户 |
| POST | `/logout` | 用户登出 | 登录用户 |

### 🏫 院系管理 (`/api/v1/departments/`)
| 方法 | 端点 | 功能 | 权限 |
|------|------|------|------|
| GET | `/` | 获取院系列表 | 公开 |
| GET | `/{id}` | 获取院系详情 | 公开 |
| POST | `/` | 创建院系 | 管理员 |
| PUT | `/{id}` | 更新院系 | 管理员 |
| DELETE | `/{id}` | 删除院系 | 管理员 |
| GET | `/{id}/students` | 院系学生列表 | 管理员 |
| GET | `/{id}/courses` | 院系课程列表 | 公开 |

### 📚 课程管理 (`/api/v1/courses/`)
| 方法 | 端点 | 功能 | 权限 |
|------|------|------|------|
| GET | `/` | 获取课程列表(分页/搜索) | 公开 |
| GET | `/{id}` | 获取课程详情 | 公开 |
| POST | `/` | 创建课程 | 管理员 |
| PUT | `/{id}` | 更新课程 | 管理员 |
| DELETE | `/{id}` | 删除课程 | 管理员 |

### 📝 选课管理 (`/api/v1/enrollments/`)
| 方法 | 端点 | 功能 | 权限 |
|------|------|------|------|
| POST | `/` | 学生选课 | 学生 |
| DELETE | `/{id}` | 学生退课 | 学生/管理员 |
| GET | `/my-courses` | 查看我的选课 | 学生 |
| PUT | `/{id}/grade` | 录入成绩 | 管理员 |
| GET | `/course/{id}` | 课程选课列表 | 管理员 |
| GET | `/statistics` | 选课统计 | 管理员 |

### 🤝 好友系统 (`/api/v1/friendships/`) 🆕
| 方法 | 端点 | 功能 | 权限 |
|------|------|------|------|
| POST | `/request` | 发送好友申请 | 学生 |
| PUT | `/{id}/accept` | 接受好友申请 | 学生 |
| PUT | `/{id}/reject` | 拒绝好友申请 | 学生 |
| GET | `/list` | 获取好友列表 | 学生 |
| GET | `/requests` | 获取好友申请列表 | 学生 |
| GET | `/recommendations` | 获取好友推荐 | 学生 |
| DELETE | `/{id}` | 删除好友关系 | 学生 |

### 💰 转账系统 (`/api/v1/transactions/`) 🆕
| 方法 | 端点 | 功能 | 权限 |
|------|------|------|------|
| POST | `/transfer` | 创建转账 | 学生 |
| GET | `/balance` | 查询余额 | 学生 |
| GET | `/history` | 转账记录 | 学生 |
| GET | `/statistics` | 转账统计 | 学生/管理员 |

### 📨 消息系统 (`/api/v1/messages/`) 🆕
| 方法 | 端点 | 功能 | 权限 |
|------|------|------|------|
| POST | `/send` | 发送消息 | 学生/管理员 |
| GET | `/inbox` | 收件箱 | 学生/管理员 |
| GET | `/sent` | 发件箱 | 学生/管理员 |
| GET | `/{id}` | 消息详情 | 学生/管理员 |
| PUT | `/{id}/status` | 更新消息状态 | 学生/管理员 |
| DELETE | `/{id}` | 删除消息 | 学生/管理员 |
| GET | `/unread/count` | 未读消息数 | 学生/管理员 |

## 🛡️ 安全特性

### SQL注入防护
- ✅ 参数化查询
- ✅ 危险关键字检测  
- ✅ 输入验证和清理
- ✅ 错误信息过滤

### 认证与授权
- ✅ JWT令牌认证
- ✅ bcrypt密码加密
- ✅ 基于角色的权限控制
- ✅ 登录日志记录

### 业务安全 🆕
- ✅ 好友关系验证
- ✅ 转账风险控制
- ✅ 消息权限管理
- ✅ 限额和频次控制

### 数据验证
- ✅ Pydantic数据模型验证
- ✅ 类型提示和检查
- ✅ 输入长度和格式限制
- ✅ 业务规则验证

## 📈 开发进度

### v1.1.0 (当前版本) - 高级功能完善
- [x] 好友系统完整开发
- [x] 转账系统核心功能
- [x] 消息系统全面功能
- [x] 前端Vue.js项目初始化
- [x] API路由系统重构
- [x] 版本管理系统完善

### v1.0.1 - 核心功能实现
- [x] 项目架构搭建
- [x] 数据库设计与初始化
- [x] MySQL命令行CRUD客户端
- [x] 用户认证系统
- [x] 课程管理功能
- [x] 院系管理功能  
- [x] 选课系统核心功能
- [x] API文档生成

### v1.2.0 (计划) - 前端完善
- [ ] 完整前端页面开发
- [ ] 用户界面优化
- [ ] 前后端功能集成
- [ ] 学生管理功能完善
- [ ] 管理员功能扩展

### v2.0.0 (计划) - 系统优化
- [ ] 系统集成测试
- [ ] 性能优化
- [ ] 部署文档
- [ ] 数据可视化

## 🆕 v1.1.0 新功能亮点

### 🤝 好友系统
- **好友申请流程**: 发送申请 → 审批处理 → 建立好友关系
- **智能推荐算法**: 基于院系、年级、共同好友的推荐机制
- **好友管理**: 好友列表、申请记录、关系删除
- **安全控制**: 好友数量限制、权限验证

### 💰 转账系统
- **安全转账**: 好友间资金流转，支付密码验证
- **风险控制**: 单笔限额、日限额、大额审核
- **余额管理**: 实时余额查询、交易记录
- **统计分析**: 个人/全局转账统计

### 📨 消息系统
- **消息收发**: 好友间消息通讯，管理员公告
- **状态管理**: 已读/未读标记、消息时间
- **搜索功能**: 消息内容搜索、分页浏览
- **权限控制**: 基于好友关系的消息权限

### 🎨 前端架构
- **Vue.js 3**: 组合式API、响应式系统
- **Element Plus**: 现代化UI组件库
- **路由管理**: 完整的页面路由配置
- **状态管理**: Pinia状态管理方案

## 🧪 测试

### API测试
```bash
# 运行基础API测试
python test_api.py

# 使用curl测试新功能
# 好友申请
curl -X POST http://localhost:8000/api/v1/friendships/request \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"friend_id": "student001", "message": "你好，我们认识一下吧"}'

# 转账功能
curl -X POST http://localhost:8000/api/v1/transactions/transfer \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient_id": "student001", "amount": 100.0, "description": "还款", "payment_password": "password"}'

# 发送消息
curl -X POST http://localhost:8000/api/v1/messages/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"recipient_id": "student001", "subject": "问候", "content": "你好，最近怎么样？"}'
```

### 前端测试
```bash
# 启动前端开发服务器
cd frontend
npm run dev

# 访问前端应用
open http://localhost:3000
```

## 📝 配置说明

### 环境变量配置
创建 `.env` 文件 (可选):
```env
# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306  
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=student_course_system

# JWT配置
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# 应用配置
DEBUG=True
LOG_LEVEL=INFO
```

### 业务配置 🆕
```python
# 好友系统配置
MAX_FRIENDS_COUNT = 100          # 最大好友数量
FRIEND_RECOMMENDATION_COUNT = 10  # 推荐好友数量

# 转账系统配置
MAX_TRANSACTION_AMOUNT = 1000.0   # 单笔转账限额
DAILY_TRANSACTION_LIMIT = 5000.0  # 日转账限额
HIGH_RISK_AMOUNT = 500.0          # 高风险金额阈值
```

## 🤝 贡献指南

### 开发流程
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 版本管理
- 每次重要更新前更新版本号
- 在文件头部添加版本信息注释
- 更新 `CHANGELOG.md` 记录变更
- 标注重要文件的版本信息

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- 项目地址: [GitHub Repository]
- 问题反馈: [Issues]
- 邮箱: [your-email@example.com]

## 📚 参考文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Vue.js 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [MySQL 8.0 文档](https://dev.mysql.com/doc/refman/8.0/en/)
- [JWT 认证](https://jwt.io/)

---

⭐ 如果这个项目对您有帮助，请给个星标支持！ 