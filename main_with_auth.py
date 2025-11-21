#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
带认证功能的简化版后端
包含登录注册功能，方便前端测试

@version: v1.0.0
@date: 2024-12-06
"""

import logging
import time
import hashlib
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict
import uvicorn

# 简化配置
class SimpleSettings:
    PROJECT_NAME = "Student Course Selection System"
    VERSION = "1.2.0-auth"
    DESCRIPTION = "在线大学生选课系统 [带认证功能]"
    API_V1_STR = "/api/v1"
    SECRET_KEY = "simple-auth-key-for-testing"
    DEBUG = True
    BACKEND_CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]

settings = SimpleSettings()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 简单的内存用户存储（仅用于测试）
users_db: Dict[str, dict] = {
    "admin": {
        "username": "admin", 
        "password": "admin123",  # 实际应用中应该加密
        "name": "系统管理员",
        "user_type": "admin"
    },
    "student1": {
        "username": "student1",
        "password": "123456",
        "name": "张三",
        "user_type": "student",
        "student_id": "202301001"
    }
}

# 简单的token存储
tokens_db: Dict[str, dict] = {}

# 请求/响应模型
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    studentId: Optional[str] = None

class LoginResponse(BaseModel):
    code: int = 200
    message: str = "登录成功"
    data: dict

# 安全组件
security = HTTPBearer()

def create_token(username: str) -> str:
    """创建简单token"""
    token = hashlib.md5(f"{username}_{time.time()}_{settings.SECRET_KEY}".encode()).hexdigest()
    tokens_db[token] = {
        "username": username,
        "created_at": time.time()
    }
    return token

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """验证token"""
    token = credentials.credentials
    if token not in tokens_db:
        raise HTTPException(status_code=401, detail="无效的token")
    
    token_data = tokens_db[token]
    username = token_data["username"]
    
    if username not in users_db:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    return users_db[username]

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": int(time.time()),
        "auth": "enabled",
        "features": {
            "authentication": "✅ 可用",
            "registration": "✅ 可用", 
            "basic_api": "✅ 可用",
            "cors": "✅ 已启用"
        }
    }

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用在线大学生选课系统 [认证版]",
        "version": settings.VERSION,
        "docs": "/docs",
        "api": settings.API_V1_STR,
        "health": "/health",
        "auth_endpoints": {
            "login": f"{settings.API_V1_STR}/auth/login",
            "register": f"{settings.API_V1_STR}/auth/register",
            "me": f"{settings.API_V1_STR}/auth/me"
        },
        "test_users": {
            "admin": "admin123",
            "student1": "123456"
        }
    }

# 认证路由
@app.post(f"{settings.API_V1_STR}/auth/login")
async def login(request: LoginRequest):
    """用户登录"""
    try:
        username = request.username.strip()
        password = request.password
        
        # 验证用户
        if username not in users_db:
            raise HTTPException(
                status_code=401, 
                detail="用户名或密码错误"
            )
        
        user = users_db[username]
        if user["password"] != password:  # 简化验证，实际应用需要加密比较
            raise HTTPException(
                status_code=401,
                detail="用户名或密码错误"
            )
        
        # 创建token
        token = create_token(username)
        
        # 返回成功响应
        response_data = {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "username": user["username"],
                "name": user["name"],
                "user_type": user["user_type"]
            }
        }
        
        if "student_id" in user:
            response_data["user"]["student_id"] = user["student_id"]
        
        logger.info(f"用户 {username} 登录成功")
        
        return LoginResponse(
            code=200,
            message="登录成功",
            data=response_data
        )
        
    except HTTPException as e:
        logger.warning(f"登录失败: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"登录错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="服务器内部错误"
        )

@app.post(f"{settings.API_V1_STR}/auth/register")
async def register(request: RegisterRequest):
    """用户注册"""
    try:
        username = request.username.strip()
        
        # 检查用户是否已存在
        if username in users_db:
            raise HTTPException(
                status_code=400,
                detail="用户名已存在"
            )
        
        # 创建新用户
        new_user = {
            "username": username,
            "password": request.password,  # 实际应用需要加密
            "name": username,  # 简化，使用用户名作为姓名
            "user_type": "student"
        }
        
        if request.studentId:
            new_user["student_id"] = request.studentId
        
        users_db[username] = new_user
        
        logger.info(f"新用户 {username} 注册成功")
        
        return {
            "code": 200,
            "message": "注册成功",
            "data": {
                "username": username,
                "message": "注册成功，请登录"
            }
        }
        
    except HTTPException as e:
        logger.warning(f"注册失败: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"注册错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="服务器内部错误"
        )

@app.get(f"{settings.API_V1_STR}/auth/me")
async def get_current_user(current_user: dict = Depends(verify_token)):
    """获取当前用户信息"""
    return {
        "code": 200,
        "message": "获取用户信息成功",
        "data": {
            "username": current_user["username"],
            "name": current_user["name"],
            "user_type": current_user["user_type"]
        }
    }

@app.post(f"{settings.API_V1_STR}/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """用户登出"""
    token = credentials.credentials
    if token in tokens_db:
        del tokens_db[token]
    
    return {
        "code": 200,
        "message": "登出成功"
    }

# 测试端点
@app.get("/test")
async def test_endpoint():
    """测试端点"""
    return {
        "message": "API测试成功",
        "timestamp": time.time(),
        "server": "带认证功能的简化版FastAPI服务器",
        "registered_users": len(users_db),
        "active_tokens": len(tokens_db)
    }

if __name__ == "__main__":
    print("🚀 启动带认证功能的选课系统...")
    print(f"📦 版本: {settings.VERSION}")
    print(f"📍 地址: http://localhost:8000")
    print(f"📚 文档: http://localhost:8000/docs") 
    print(f"🔐 认证: http://localhost:8000/api/v1/auth/login")
    print(f"👤 测试用户: admin/admin123, student1/123456")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 