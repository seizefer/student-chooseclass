#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生选课系统状态检查 - 完整版
检查前后端服务状态和功能
"""

import requests
import socket
from datetime import datetime

def check_port(host, port):
    """检查端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_backend():
    """检查后端服务状态"""
    print("🔧 检查后端服务...")
    
    # 检查端口
    if not check_port('localhost', 8000):
        print("❌ 后端端口8000未开放")
        return False
    
    try:
        # 检查健康状态
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ 后端健康检查通过")
        else:
            print(f"⚠️ 后端健康检查异常: {response.status_code}")
            
        # 检查API文档
        response = requests.get('http://localhost:8000/docs', timeout=5)
        if response.status_code == 200:
            print("✅ API文档可访问")
        else:
            print(f"⚠️ API文档访问异常: {response.status_code}")
            
        # 测试登录API
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                print("✅ 登录API正常")
                return True
            else:
                print(f"❌ 登录API业务逻辑错误: {data.get('message')}")
                return False
        else:
            print(f"❌ 登录API HTTP错误: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接后端服务")
        return False
    except Exception as e:
        print(f"❌ 后端检查错误: {e}")
        return False

def check_frontend():
    """检查前端服务状态"""
    print("\n🎨 检查前端服务...")
    
    # 检查端口
    if not check_port('localhost', 3000):
        print("❌ 前端端口3000未开放")
        return False
    
    try:
        # 检查前端页面
        response = requests.get('http://localhost:3000', timeout=10)
        if response.status_code == 200:
            print("✅ 前端页面可访问")
            
            # 检查关键内容
            content = response.text
            if '学生选课系统' in content:
                print("✅ 前端内容正确")
            else:
                print("⚠️ 前端内容可能有问题")
                
            return True
        else:
            print(f"❌ 前端页面访问错误: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接前端服务")
        return False
    except Exception as e:
        print(f"❌ 前端检查错误: {e}")
        return False

def test_complete_workflow():
    """测试完整的登录流程"""
    print("\n🔄 测试完整登录流程...")
    
    try:
        # 1. 测试注册
        register_data = {
            "username": f"test_user_{datetime.now().strftime('%H%M%S')}",
            "password": "123456",
            "studentId": f"2024{datetime.now().strftime('%M%S')}"
        }
        
        response = requests.post('http://localhost:8000/api/v1/auth/register', json=register_data, timeout=5)
        if response.status_code == 200 and response.json().get('code') == 200:
            print("✅ 用户注册功能正常")
            
            # 2. 使用新用户登录
            login_data = {
                "username": register_data["username"],
                "password": register_data["password"]
            }
            
            response = requests.post('http://localhost:8000/api/v1/auth/login', json=login_data, timeout=5)
            if response.status_code == 200 and response.json().get('code') == 200:
                print("✅ 新用户登录功能正常")
                
                # 获取token
                token = response.json().get('data', {}).get('access_token', '')
                if token:
                    print("✅ Token获取正常")
                    
                    # 3. 测试用户信息获取
                    headers = {"Authorization": f"Bearer {token}"}
                    response = requests.get('http://localhost:8000/api/v1/auth/me', headers=headers, timeout=5)
                    if response.status_code == 200 and response.json().get('code') == 200:
                        print("✅ 用户信息获取正常")
                        return True
                    else:
                        print("❌ 用户信息获取失败")
                else:
                    print("❌ Token获取失败")
            else:
                print("❌ 新用户登录失败")
        else:
            print("❌ 用户注册失败")
            
    except Exception as e:
        print(f"❌ 完整流程测试错误: {e}")
        
    return False

def check_system_files():
    """检查关键系统文件"""
    print("\n📁 检查关键文件...")
    
    import os
    
    critical_files = [
        "backend/main.py",
        "frontend/index.html", 
        "frontend/src/main.js",
        "frontend/src/stores/auth.js",
        "frontend/src/views/auth/Login.vue",
        "frontend/src/views/auth/Register.vue"
    ]
    
    all_exist = True
    for file_path in critical_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({size} bytes)")
        else:
            print(f"❌ {file_path} 缺失")
            all_exist = False
            
    return all_exist

def main():
    """主检查函数"""
    print("🚀 学生选课系统完整状态检查")
    print("=" * 60)
    
    # 检查文件
    files_ok = check_system_files()
    
    # 检查后端
    backend_ok = check_backend()
    
    # 检查前端
    frontend_ok = check_frontend()
    
    # 测试完整流程
    workflow_ok = test_complete_workflow()
    
    print("\n" + "=" * 60)
    print("📊 系统状态总结:")
    print(f"关键文件: {'✅ 完整' if files_ok else '❌ 缺失'}")
    print(f"后端服务: {'✅ 正常' if backend_ok else '❌ 异常'}")
    print(f"前端服务: {'✅ 正常' if frontend_ok else '❌ 异常'}")
    print(f"登录流程: {'✅ 正常' if workflow_ok else '❌ 异常'}")
    
    if all([files_ok, backend_ok, frontend_ok, workflow_ok]):
        print("\n🎉 系统完全正常！")
        print("📍 前端地址: http://localhost:3000")
        print("📍 后端地址: http://localhost:8000")
        print("📍 API文档: http://localhost:8000/docs")
        print("🔑 测试账户: admin/admin123")
        print("💡 现在可以正常使用系统了！")
    else:
        print("\n⚠️ 系统还有问题需要解决")
        
        if not backend_ok:
            print("💡 请检查后端服务是否正在运行: python backend/main.py")
        if not frontend_ok:
            print("💡 请检查前端服务是否正在运行: cd frontend && npm run dev")

if __name__ == "__main__":
    main() 