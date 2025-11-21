#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整版后端启动脚本
启动包含所有API功能的完整后端服务

@version: v1.0.0
@date: 2024-12-06
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """检查必要的依赖"""
    print("🔍 检查依赖...")
    
    try:
        import fastapi
        print("✅ FastAPI")
    except ImportError:
        print("❌ FastAPI 未安装")
        return False
        
    try:
        import uvicorn
        print("✅ Uvicorn")
    except ImportError:
        print("❌ Uvicorn 未安装")
        return False
        
    try:
        import mysql.connector
        print("✅ MySQL Connector")
    except ImportError:
        print("❌ MySQL Connector 未安装")
        return False
    
    print("✅ 依赖检查通过")
    return True

def start_backend():
    """启动完整版后端"""
    print("🚀 启动完整版后端服务...")
    
    # 确保在正确的目录
    backend_dir = "backend"
    if os.path.exists(backend_dir):
        os.chdir(backend_dir)
        print(f"📁 切换到目录: {os.getcwd()}")
    
    # 启动服务
    try:
        import uvicorn
        print("📡 启动FastAPI服务器...")
        print("🌐 访问地址:")
        print("   主页: http://localhost:8000")
        print("   API文档: http://localhost:8000/docs")
        print("   健康检查: http://localhost:8000/health")
        print("   API前缀: http://localhost:8000/v1")
        print("=" * 50)
        
        uvicorn.run(
            "main:app",  # 使用完整版main.py
            host="0.0.0.0",
            port=8000,
            reload=True,  # 开发模式热重载
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🎯 在线大学生选课系统 - 完整版后端启动器")
    print("=" * 50)
    
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请安装必要依赖:")
        print("   pip install fastapi uvicorn mysql-connector-python")
        return False
    
    if not start_backend():
        print("❌ 后端启动失败")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 