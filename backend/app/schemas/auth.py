"""
认证相关数据模式
"""
from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_type: str
    user: dict  # 添加用户信息字段

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 691200,
                "user_type": "student",
                "user": {
                    "student_id": "20231001",
                    "name": "张三",
                    "user_type": "student"
                }
            }
        }


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名（学号或管理员ID）")
    password: str = Field(..., description="密码")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "20231001",
                "password": "123456"
            }
        }


class UserRegister(BaseModel):
    """用户注册模型"""
    student_id: str = Field(..., max_length=20, description="学号")
    name: str = Field(..., max_length=50, description="姓名")
    password: str = Field(..., min_length=6, description="密码")
    id_number: str = Field(..., max_length=18, description="身份证号")
    birth_date: Optional[date] = Field(None, description="出生日期")
    address: Optional[str] = Field(None, max_length=200, description="地址")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="电话号码")
    department_id: Optional[str] = Field(None, max_length=10, description="所属院系")
    major: Optional[str] = Field(None, max_length=100, description="专业")
    grade: Optional[int] = Field(None, description="年级")
    
    class Config:
        schema_extra = {
            "example": {
                "student_id": "20231001",
                "name": "张三",
                "password": "123456",
                "id_number": "123456789012345678",
                "birth_date": "2000-01-01",
                "address": "北京市海淀区",
                "email": "zhangsan@example.com",
                "phone": "13800138000",
                "department_id": "CS",
                "major": "计算机科学与技术",
                "grade": 2023
            }
        }


class UserResponse(BaseModel):
    """用户响应模型"""
    student_id: Optional[str] = None
    admin_id: Optional[str] = None
    name: str
    birth_date: Optional[date] = None
    id_number: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[int] = None
    balance: Optional[float] = None
    status: Optional[str] = None
    role: Optional[str] = None
    user_type: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "student_id": "20231001",
                "name": "张三",
                "birth_date": "2000-01-01",
                "id_number": "123456789012345678",
                "address": "北京市海淀区",
                "email": "zhangsan@example.com",
                "phone": "13800138000",
                "department_id": "CS",
                "major": "计算机科学与技术",
                "grade": 2023,
                "balance": 0.00,
                "status": "active",
                "user_type": "student"
            }
        } 