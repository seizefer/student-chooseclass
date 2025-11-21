#!/usr/bin/env python
"""
系统状态检查脚本
快速检查各个组件的运行状态

@version: v1.2.0
@date: 2024-12-06
"""
import requests
import time
import sys

def check_api_health():
    """检查API服务健康状态"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API服务正常运行")
            print(f"   版本: {data.get('version', 'unknown')}")
            print(f"   状态: {data.get('status', 'unknown')}")
            print(f"   数据库: {data.get('database', 'unknown')}")
            return True
        else:
            print(f"⚠️ API服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API服务未启动或无法连接")
        return False
    except Exception as e:
        print(f"❌ API检查失败: {str(e)}")
        return False

def check_api_docs():
    """检查API文档可访问性"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API文档可访问")
            return True
        else:
            print(f"⚠️ API文档访问异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API文档检查失败: {str(e)}")
        return False

def check_database():
    """检查数据库连接"""
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='student_course_system'
        )
        conn.close()
        print("✅ 数据库连接正常")
        return True
    except mysql.connector.Error as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 数据库检查异常: {str(e)}")
        return False

def check_dependencies():
    """检查关键依赖"""
    dependencies = [
        ('fastapi', 'FastAPI框架'),
        ('uvicorn', 'ASGI服务器'),
        ('mysql.connector', 'MySQL连接器'),
        ('pydantic', '数据验证')
    ]
    
    missing = []
    for module, description in dependencies:
        try:
            if module == 'mysql.connector':
                import mysql.connector
            else:
                __import__(module)
            print(f"✅ {description}")
        except ImportError:
            print(f"❌ {description} - 未安装")
            missing.append(module)
    
    return len(missing) == 0

def main():
    """主检查函数"""
    print("🔍 系统状态检查")
    print("=" * 50)
    
    # 检查依赖
    print("\n📦 依赖检查:")
    deps_ok = check_dependencies()
    
    # 检查数据库
    print("\n🗄️ 数据库检查:")
    db_ok = check_database()
    
    # 检查API服务
    print("\n🖥️ API服务检查:")
    api_ok = check_api_health()
    
    # 检查API文档
    print("\n📚 API文档检查:")
    docs_ok = check_api_docs()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 检查结果:")
    
    total_checks = 4
    passed_checks = sum([deps_ok, db_ok, api_ok, docs_ok])
    
    if passed_checks == total_checks:
        print("🎉 所有检查通过！系统运行正常")
    else:
        print(f"⚠️ {passed_checks}/{total_checks} 项检查通过")
        
        if not api_ok:
            print("\n💡 建议:")
            print("   1. 启动API服务: python main_simple.py")
            print("   2. 检查端口8000是否被占用")
            print("   3. 查看错误日志")
    
    print(f"\n🔗 快速链接:")
    print(f"   主页: http://localhost:8000")
    print(f"   健康检查: http://localhost:8000/health")
    print(f"   API文档: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 