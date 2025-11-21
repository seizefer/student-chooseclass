#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端登录请求 - 模拟前端的确切请求
"""

import requests
import json

def test_frontend_login_request():
    """模拟前端发送的登录请求"""
    print("🔐 测试前端登录请求...")
    
    # 模拟前端发送的确切请求
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    # 前端使用的确切URL
    url = "http://localhost:8000/api/v1/auth/login"
    
    try:
        print(f"📡 发送请求到: {url}")
        print(f"📦 请求数据: {login_data}")
        
        response = requests.post(
            url,
            json=login_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        
        print(f"🔗 状态码: {response.status_code}")
        print(f"📄 响应头: {dict(response.headers)}")
        print(f"💬 响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                print("✅ 前端登录请求成功!")
                token = data.get("data", {}).get("access_token", "")
                print(f"🔑 获得Token: {token[:20]}..." if token else "❌ 未获得Token")
                return True
            else:
                print(f"❌ 业务逻辑失败: {data.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 请确认后端服务正在运行")
        return False
    except Exception as e:
        print(f"❌ 请求错误: {e}")
        return False

def test_register_request():
    """测试注册请求"""
    print("\n📝 测试前端注册请求...")
    
    register_data = {
        "username": "frontend_test_user",
        "password": "123456",
        "studentId": "202401002"
    }
    
    url = "http://localhost:8000/api/v1/auth/register"
    
    try:
        print(f"📡 发送请求到: {url}")
        
        response = requests.post(
            url,
            json=register_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        
        print(f"🔗 状态码: {response.status_code}")
        print(f"💬 响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                print("✅ 前端注册请求成功!")
                return True
        
        print("❌ 注册请求失败")
        return False
        
    except Exception as e:
        print(f"❌ 注册请求错误: {e}")
        return False

def test_api_endpoints():
    """测试所有认证相关的API端点"""
    print("\n🔍 测试API端点可用性...")
    
    endpoints = [
        ("POST", "/api/v1/auth/login", {"username": "admin", "password": "admin123"}),
        ("GET", "/health", None),
        ("GET", "/", None),
        ("GET", "/docs", None)
    ]
    
    base_url = "http://localhost:8000"
    
    for method, endpoint, data in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            if method == "POST":
                response = requests.post(url, json=data, timeout=5)
            else:
                response = requests.get(url, timeout=5)
            
            status = "✅" if response.status_code < 400 else "❌"
            print(f"{status} {method} {endpoint} - {response.status_code}")
            
        except Exception as e:
            print(f"❌ {method} {endpoint} - 错误: {str(e)[:50]}")

if __name__ == "__main__":
    print("🧪 前端登录功能测试")
    print("=" * 50)
    
    # 测试API端点
    test_api_endpoints()
    
    # 测试登录
    login_success = test_frontend_login_request()
    
    # 测试注册
    register_success = test_register_request()
    
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"前端登录: {'✅ 成功' if login_success else '❌ 失败'}")
    print(f"前端注册: {'✅ 成功' if register_success else '❌ 失败'}")
    
    if login_success and register_success:
        print("\n🎉 前端认证功能完全正常!")
        print("💡 现在可以在浏览器中正常登录了")
    else:
        print("\n⚠️ 还有问题需要解决") 