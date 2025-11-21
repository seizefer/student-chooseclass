"""
API路由汇总
包含所有API版本1的端点路由

@version: v1.2.0
@date: 2024-12-06
@changelog:
  v1.2.0:
    - 添加学生管理API路由
    - 完善前端支持路由
    - 增强API功能集成
  v1.1.0:
    - 添加好友系统API路由
    - 添加转账系统API路由
    - 添加消息系统API路由
    - 完善高级功能模块
  v1.0.1:
    - 添加课程管理、院系管理、选课管理路由
  v1.0.0:
    - 初始版本，包含认证路由
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, courses, departments, enrollments
from app.api.v1.endpoints import friendships, transactions, messages, students

api_router = APIRouter()

# 认证相关路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证管理"])

# 院系管理路由
api_router.include_router(departments.router, prefix="/departments", tags=["院系管理"])

# 课程管理路由
api_router.include_router(courses.router, prefix="/courses", tags=["课程管理"])

# 选课管理路由
api_router.include_router(enrollments.router, prefix="/enrollments", tags=["选课管理"])

# 学生管理路由
api_router.include_router(students.router, prefix="/students", tags=["学生管理"])

# 好友系统路由
api_router.include_router(friendships.router, prefix="/friendships", tags=["好友系统"])

# 转账系统路由
api_router.include_router(transactions.router, prefix="/transactions", tags=["转账系统"])

# 消息系统路由
api_router.include_router(messages.router, prefix="/messages", tags=["消息系统"]) 