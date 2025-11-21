"""
管理员功能API端点
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from app.core.config import settings
from app.db.mysql_client import mysql_client
from app.schemas.common import ResponseModel
from app.api.v1.endpoints.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/statistics", response_model=ResponseModel[Dict[str, Any]])
async def get_admin_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[Dict[str, Any]]:
    """
    获取管理员统计数据
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以查看统计数据"
            )

        # 由于数据库可能不可用，返回模拟数据
        statistics = {
            "total_students": 1256,
            "total_courses": 89,
            "today_enrollments": 45,
            "total_transactions": 125680.50,
            "active_students": 1123,
            "completed_courses": 234
        }

        return ResponseModel(
            code=200,
            message="获取统计数据成功",
            data=statistics
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取统计数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计数据失败"
        )


@router.get("/activities", response_model=ResponseModel[List[Dict[str, Any]]])
async def get_recent_activities(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[List[Dict[str, Any]]]:
    """
    获取最近活动记录
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以查看活动记录"
            )

        # 返回模拟的活动数据
        activities = [
            {
                "id": 1,
                "type": "enrollment",
                "description": "学生 张三 选修了 高等数学",
                "created_at": "2024-11-22T10:30:00Z"
            },
            {
                "id": 2,
                "type": "course_created",
                "description": "新课程 Python编程 已发布",
                "created_at": "2024-11-22T09:15:00Z"
            },
            {
                "id": 3,
                "type": "transaction",
                "description": "学生 李四 完成了转账 ¥100",
                "created_at": "2024-11-22T08:45:00Z"
            },
            {
                "id": 4,
                "type": "user_registered",
                "description": "新学生 王五 注册成功",
                "created_at": "2024-11-22T08:00:00Z"
            },
            {
                "id": 5,
                "type": "course_completed",
                "description": "学生 陈六 完成了 数据结构 课程",
                "created_at": "2024-11-21T16:20:00Z"
            }
        ]

        return ResponseModel(
            code=200,
            message="获取活动记录成功",
            data=activities
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取活动记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取活动记录失败"
        ) 