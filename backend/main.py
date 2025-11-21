"""
在线大学生选课系统 - 主应用入口
FastAPI后端服务器

@version: v1.2.0
@date: 2024-12-06
@changelog:
  v1.2.0:
    - 完善前端页面开发
    - 新增学生管理功能
    - 添加个人资料管理
    - 完善用户界面优化
    - 实现前后端功能集成
  v1.1.0:
    - 新增好友系统功能
    - 新增转账系统功能
    - 新增消息系统功能
    - 完善高级功能模块
  v1.0.1:
    - 优化应用生命周期管理
    - 改进全局异常处理
    - 添加版本信息标注
  v1.0.0:
    - 初始版本
    - 基础FastAPI应用架构
    - CORS中间件配置
    - 健康检查端点
"""
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import uvicorn

from app.core.config import settings
from app.api.v1.api import api_router


# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 学生选课系统启动中...")
    logger.info(f"📦 版本: {settings.VERSION}")
    logger.info(f"📊 数据库: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}")
    logger.info(f"🔧 调试模式: {settings.DEBUG}")
    logger.info(f"🎨 前端地址: {settings.FRONTEND_URL}")
    
    # 可以在这里添加数据库连接测试等启动检查
    try:
        from app.db.mysql_client import mysql_client
        # 简单的数据库连接测试
        success, results, error = mysql_client.execute_raw_sql("SELECT 1 as test;")
        if success:
            logger.info("✅ 数据库连接正常")
        else:
            logger.warning(f"⚠️ 数据库连接测试失败: {error}")
    except Exception as e:
        logger.warning(f"⚠️ 数据库连接测试异常: {str(e)}")
    
    yield
    # 关闭时执行
    logger.info("🛑 学生选课系统已关闭")


# 创建FastAPI应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加受信任主机中间件（生产环境）
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.example.com"]
    )


# 请求处理时间中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加请求处理时间头"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-API-Version"] = settings.VERSION
    
    # 记录慢请求
    if process_time > 1.0:  # 超过1秒的请求
        logger.warning(f"慢请求: {request.method} {request.url} - {process_time:.2f}s")
    
    return response


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(f"未处理的异常: {request.method} {request.url} - {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "detail": str(exc) if settings.DEBUG else "请联系管理员",
            "version": settings.VERSION
        }
    )


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 数据库连接检查
        from app.db.mysql_client import mysql_client
        success, results, error = mysql_client.execute_raw_sql("SELECT 1 as test;")
        
        return {
            "status": "healthy" if success else "degraded",
            "version": settings.VERSION,
            "timestamp": int(time.time()),
            "environment": "development" if settings.DEBUG else "production",
            "database": "connected" if success else f"error: {error}",
            "features": {
                "authentication": "enabled",
                "mysql_cli": "enabled",
                "cors": "enabled",
                "friendships": "enabled",
                "transactions": "enabled",
                "messages": "enabled",
                "student_management": "enabled",
                "frontend_ui": "enabled"
            }
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "version": settings.VERSION,
                "error": str(e)
            }
        )


# 根路径
@app.get("/")
async def root():
    """根路径接口"""
    return {
        "message": "欢迎使用在线大学生选课系统",
        "version": settings.VERSION,
        "docs": "/docs",
        "api": settings.API_V1_STR,
        "health": "/health",
        "frontend": settings.FRONTEND_URL,
        "features": [
            "学生选课管理",
            "好友社交系统",
            "转账功能", 
            "消息通讯",
            "个人资料管理",
            "现代化前端界面"
        ],
        "new_in_v1_2_0": [
            "完整前端页面开发",
            "学生个人资料管理",
            "响应式用户界面",
            "前后端功能集成",
            "现代化设计风格",
            "用户体验优化"
        ],
        "previous_versions": {
            "v1.1.0": [
                "好友申请与管理",
                "好友推荐算法",
                "转账与余额查询",
                "风险控制与限额",
                "消息发送与接收",
                "消息状态管理"
            ],
            "v1.0.1": [
                "课程管理系统",
                "院系管理功能",
                "选课核心功能",
                "成绩管理系统"
            ]
        }
    }


# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    """直接运行时的配置"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    ) 