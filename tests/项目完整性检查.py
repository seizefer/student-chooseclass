#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目完整性检查脚本
检查前后端项目的完整性和文件结构
"""

import os
import json
import subprocess
from pathlib import Path

def check_backend_files():
    """检查后端文件完整性"""
    print("🔧 检查后端文件...")
    
    backend_files = [
        "backend/main.py",
        "backend/app/__init__.py",
        "backend/app/main.py", 
        "backend/app/db/mysql_client.py",
        "backend/app/core/config.py",
        "backend/app/utils/security.py",
        "backend/app/routers/auth.py",
        "backend/app/routers/courses.py",
        "backend/app/routers/departments.py",
        "backend/app/routers/enrollments.py"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in backend_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")
    
    print(f"\n后端文件统计: {len(existing_files)}/{len(backend_files)} 个文件存在")
    
    if missing_files:
        print("⚠️ 缺失的后端文件:")
        for file in missing_files:
            print(f"   - {file}")
    
    return len(missing_files) == 0

def check_frontend_files():
    """检查前端文件完整性"""
    print("\n🎨 检查前端文件...")
    
    frontend_files = [
        "frontend/index.html",
        "frontend/package.json",
        "frontend/vite.config.js",
        "frontend/src/main.js",
        "frontend/src/App.vue",
        "frontend/src/views/Welcome.vue",
        "frontend/src/views/auth/Login.vue",
        "frontend/src/views/auth/Register.vue",
        "frontend/src/views/dashboard/index.vue",
        "frontend/src/views/courses/List.vue",
        "frontend/src/views/error/404.vue",
        "frontend/src/layout/index.vue",
        "frontend/src/router/index.js",
        "frontend/src/stores/auth.js"
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in frontend_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")
    
    print(f"\n前端文件统计: {len(existing_files)}/{len(frontend_files)} 个文件存在")
    
    if missing_files:
        print("⚠️ 缺失的前端文件:")
        for file in missing_files:
            print(f"   - {file}")
    
    return len(missing_files) == 0

def check_database_files():
    """检查数据库文件"""
    print("\n🗄️ 检查数据库文件...")
    
    db_files = [
        "database/init.sql",
        "database/sample_data.sql"
    ]
    
    existing_files = []
    
    for file_path in db_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
    
    return len(existing_files) > 0

def check_dependencies():
    """检查依赖是否安装"""
    print("\n📦 检查依赖安装...")
    
    # 检查前端依赖
    frontend_package_json = "frontend/package.json"
    if os.path.exists(frontend_package_json):
        node_modules = "frontend/node_modules"
        if os.path.exists(node_modules):
            print("✅ 前端依赖已安装")
        else:
            print("❌ 前端依赖未安装，请运行: cd frontend && npm install")
    
    # 检查Python依赖
    try:
        import fastapi
        import uvicorn
        print("✅ Python基础依赖已安装")
    except ImportError:
        print("❌ Python依赖缺失，请安装FastAPI和Uvicorn")

def check_services():
    """检查服务运行状态"""
    print("\n🚀 检查服务状态...")
    
    # 检查端口占用
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, shell=True)
        if ':8000' in result.stdout:
            print("✅ 后端服务 (端口8000) 正在运行")
        else:
            print("⚠️ 后端服务未运行")
            
        if ':3000' in result.stdout:
            print("✅ 前端服务 (端口3000) 正在运行")
        else:
            print("⚠️ 前端服务未运行")
    except:
        print("⚠️ 无法检查服务状态")

def check_project_structure():
    """检查项目目录结构"""
    print("\n📁 检查项目结构...")
    
    required_dirs = [
        "backend",
        "frontend", 
        "database",
        "docs"
    ]
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/")

def generate_report():
    """生成完整性报告"""
    print("\n" + "="*60)
    print("📊 项目完整性检查报告")
    print("="*60)
    
    backend_ok = check_backend_files()
    frontend_ok = check_frontend_files() 
    database_ok = check_database_files()
    
    check_project_structure()
    check_dependencies()
    check_services()
    
    print("\n" + "="*60)
    print("🎯 总结:")
    print(f"后端文件: {'✅ 完整' if backend_ok else '❌ 不完整'}")
    print(f"前端文件: {'✅ 完整' if frontend_ok else '❌ 不完整'}")
    print(f"数据库文件: {'✅ 存在' if database_ok else '❌ 缺失'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 项目核心文件完整，可以正常运行！")
        print("\n🔗 快速启动:")
        print("   后端: python backend/main.py")
        print("   前端: cd frontend && npm run dev")
        print("   测试: python test_frontend.py")
    else:
        print("\n⚠️ 项目存在缺失文件，可能影响正常运行")
    
    print("\n📚 访问地址:")
    print("   前端: http://localhost:3000")
    print("   后端: http://localhost:8000")
    print("   API文档: http://localhost:8000/docs")

if __name__ == "__main__":
    print("🔍 在线大学生选课系统 - 项目完整性检查")
    generate_report()