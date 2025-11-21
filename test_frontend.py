#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端连接测试脚本
测试前端服务是否正常响应
"""

import requests
import time
import sys

def test_frontend():
    """测试前端服务状态"""
    print("🔍 正在测试前端服务连接...")
    
    frontend_urls = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    working_urls = []
    
    for url in frontend_urls:
        try:
            print(f"测试 {url}...")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {url} - 响应成功 (状态码: {response.status_code})")
                working_urls.append(url)
                
                # 检查是否包含预期内容
                if "在线大学生选课系统" in response.text or "app" in response.text:
                    print(f"   📄 页面内容正常")
                else:
                    print(f"   ⚠️ 页面内容可能异常")
                    
            else:
                print(f"❌ {url} - 状态码: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {url} - 连接被拒绝")
        except requests.exceptions.Timeout:
            print(f"❌ {url} - 连接超时")
        except Exception as e:
            print(f"❌ {url} - 错误: {e}")
    
    print("\n" + "="*50)
    
    if working_urls:
        print(f"🎉 发现 {len(working_urls)} 个可用的前端地址:")
        for url in working_urls:
            print(f"   🌐 {url}")
        print("\n💡 请在浏览器中打开上述任一地址！")
        return True
    else:
        print("❌ 未找到可用的前端服务")
        print("请检查:")
        print("1. 前端服务是否已启动: cd frontend && npm run dev")
        print("2. 端口是否被占用: netstat -ano | findstr :3000")
        print("3. 防火墙设置是否阻止了访问")
        return False

def test_backend():
    """测试后端服务状态"""
    print("\n🔧 正在测试后端服务连接...")
    
    backend_urls = [
        "http://localhost:8000",
        "http://localhost:8000/health",
        "http://127.0.0.1:8000"
    ]
    
    backend_working = False
    
    for url in backend_urls:
        try:
            print(f"测试 {url}...")
            response = requests.get(url, timeout=3)
            
            if response.status_code == 200:
                print(f"✅ {url} - 后端服务正常")
                backend_working = True
                break
            else:
                print(f"❌ {url} - 状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {url} - 错误: {e}")
    
    if not backend_working:
        print("⚠️ 后端服务未运行，请启动: python main_simple.py")
    
    return backend_working

if __name__ == "__main__":
    print("🚀 在线大学生选课系统 - 服务连接测试")
    print("="*50)
    
    # 测试前端
    frontend_ok = test_frontend()
    
    # 测试后端  
    backend_ok = test_backend()
    
    print("\n" + "="*50)
    print("📊 测试结果摘要:")
    print(f"前端服务: {'✅ 正常' if frontend_ok else '❌ 异常'}")
    print(f"后端服务: {'✅ 正常' if backend_ok else '❌ 异常'}")
    
    if frontend_ok and backend_ok:
        print("\n🎉 系统已完全就绪，可以开始使用！")
    elif frontend_ok:
        print("\n⚠️ 前端正常，但请启动后端服务")
    elif backend_ok:
        print("\n⚠️ 后端正常，但前端连接有问题")
    else:
        print("\n❌ 前后端服务都需要检查") 