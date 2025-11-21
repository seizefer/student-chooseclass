"""
简化版主应用 - 临时测试版本
用于测试系统是否可以正常启动

@version: v1.2.0-simple
@date: 2024-12-06
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

# 使用简化配置
try:
    from app.core.config_simple import settings
    print("✅ 使用简化配置模块")
except ImportError as e:
    print(f"❌ 配置导入失败: {e}")
    exit(1)

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION + " [简化版]",
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

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 测试数据库连接
        try:
            from app.db.mysql_client import mysql_client
            success, results, error = mysql_client.execute_raw_sql("SELECT 1 as test;")
            db_status = "connected" if success else f"error: {error}"
        except Exception as e:
            db_status = f"module_error: {str(e)}"
        
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "timestamp": int(time.time()),
            "environment": "development" if settings.DEBUG else "production",
            "database": db_status,
            "dependencies": {
                "fastapi": "✅ 已安装",
                "uvicorn": "✅ 已安装", 
                "mysql-connector": "✅ 已安装",
                "pydantic": "✅ 已安装",
                "note": "简化版本，部分依赖可能缺失"
            },
            "features": {
                "basic_api": "enabled",
                "mysql_cli": "enabled" if db_status.startswith("connected") else "disabled",
                "cors": "enabled",
                "note": "完整功能需要安装所有依赖"
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
        "message": "欢迎使用在线大学生选课系统 [简化版]",
        "version": settings.VERSION,
        "docs": "/docs",
        "api": settings.API_V1_STR,
        "health": "/health",
        "status": "简化版本运行中",
        "note": "这是临时简化版本，用于测试系统启动",
        "next_steps": [
            "1. 访问 /health 检查系统状态",
            "2. 访问 /docs 查看API文档",
            "3. 安装完整依赖后使用main.py"
        ]
    }

# 基础API测试端点
@app.get("/test")
async def test_endpoint():
    """测试端点"""
    return {
        "message": "API测试成功",
        "timestamp": time.time(),
        "server": "简化版FastAPI服务器"
    }

if __name__ == "__main__":
    print("🚀 启动简化版选课系统...")
    print(f"📦 版本: {settings.VERSION}")
    print(f"📍 地址: http://localhost:8000")
    print(f"📚 文档: http://localhost:8000/docs")
    print(f"❤️ 健康: http://localhost:8000/health")
    print("=" * 50)
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 