"""
简化版配置模块 - 临时解决方案
当所有依赖安装完成后，请使用原版config.py

@version: v1.2.0-simple
@date: 2024-12-06
"""
import os

class Settings:
    # 项目基本信息
    PROJECT_NAME: str = "Student Course Selection System"
    VERSION: str = "1.2.0-simple"
    DESCRIPTION: str = "在线大学生选课系统 - 社交化学习平台"
    
    # API配置
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置 - 使用环境变量或默认值
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "student_course_system")
    
    # JWT配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天
    
    # 安全配置
    BCRYPT_ROUNDS: int = 12
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_FOLDER: str = "uploads"
    ALLOWED_EXTENSIONS: set = {'.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif'}
    
    # 业务配置
    MAX_FRIENDS_COUNT: int = 100
    MAX_TRANSACTION_AMOUNT: float = 1000.00
    DAILY_TRANSACTION_LIMIT: float = 5000.00
    HIGH_RISK_AMOUNT: float = 500.00
    FRIEND_RECOMMENDATION_COUNT: int = 10
    
    # 学生管理配置
    DEFAULT_STUDENT_STATUS: str = "active"
    STUDENT_ID_LENGTH: int = 12
    PASSWORD_MIN_LENGTH: int = 6
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # 前端配置
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    STATIC_FILES_PATH: str = "static"
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # 开发模式
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173"
    ]
    
    @property
    def DATABASE_URL(self) -> str:
        """构建数据库连接URL"""
        return f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    @property
    def DATABASE_CONFIG(self) -> dict:
        """数据库连接配置字典"""
        return {
            "host": self.MYSQL_HOST,
            "port": self.MYSQL_PORT,
            "user": self.MYSQL_USER,
            "password": self.MYSQL_PASSWORD,
            "database": self.MYSQL_DATABASE,
            "charset": "utf8mb4",
            "autocommit": False,
            "use_unicode": True
        }

# 创建全局设置实例
settings = Settings() 