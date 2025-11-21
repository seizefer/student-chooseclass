#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试登录功能
"""

import requests
import json

def test_login():
    """测试登录API"""
    print("🔐 测试登录功能...")
    
    # 测试数据
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # 发送登录请求 (使用表单数据格式)
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 登录成功!")
            print(f"Token: {data.get('data', {}).get('access_token', 'N/A')[:20]}...")
            print(f"用户: {data.get('data', {}).get('user', {})}")
            return True
        else:
            print("❌ 登录失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求错误: {e}")
        return False

def test_register():
    """测试注册API"""
    print("\n📝 测试注册功能...")
    
    register_data = {
        "username": "testuser",
        "password": "123456",
        "studentId": "202401001"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 注册成功!")
            return True
        else:
            print("❌ 注册失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求错误: {e}")
        return False

def test_health():
    """测试健康检查"""
    print("\n❤️ 测试健康检查...")
    
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 健康检查通过!")
            return True
        else:
            print("❌ 健康检查失败")
            return False
            
    except Exception as e:
        print(f"❌ 请求错误: {e}")
        return False

if __name__ == "__main__":
    print("🧪 认证API测试")
    print("=" * 40)
    
    # 测试健康检查
    health_ok = test_health()
    
    # 测试登录
    login_ok = test_login()
    
    # 测试注册
    register_ok = test_register()
    
    # 再次测试登录新用户
    if register_ok:
        print("\n🔐 测试新用户登录...")
        login_data = {"username": "testuser", "password": "123456"}
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/auth/login",
                json=login_data
            )
            if response.status_code == 200:
                print("✅ 新用户登录成功!")
            else:
                print("❌ 新用户登录失败")
        except Exception as e:
            print(f"❌ 新用户登录错误: {e}")
    
    print("\n" + "=" * 40)
    print("📊 测试结果:")
    print(f"健康检查: {'✅' if health_ok else '❌'}")
    print(f"用户登录: {'✅' if login_ok else '❌'}")
    print(f"用户注册: {'✅' if register_ok else '❌'}") 