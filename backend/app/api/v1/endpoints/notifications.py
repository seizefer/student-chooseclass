"""
通知系统 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()


# ==================== 数据模型 ====================

class NotificationCreate(BaseModel):
    """创建通知请求"""
    title: str
    content: str
    type: str = "system"  # system, course, message, warning, success
    user_id: Optional[str] = None  # 为空则发送给所有用户


class NotificationResponse(BaseModel):
    """通知响应"""
    id: int
    title: str
    content: str
    type: str
    is_read: bool
    created_at: datetime
    link: Optional[str] = None


# ==================== API 端点 ====================

@router.get("")
async def get_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
    is_read: Optional[bool] = None,
    # current_user = Depends(get_current_user)
):
    """
    获取用户通知列表
    - 支持按类型筛选
    - 支持按已读状态筛选
    """
    # TODO: 从数据库获取通知
    # 这里返回模拟数据
    notifications = [
        {
            "id": 1,
            "title": "选课成功",
            "content": "您已成功选修课程《高等数学》",
            "type": "course",
            "is_read": False,
            "created_at": datetime.now(),
            "link": "/courses/my"
        },
        {
            "id": 2,
            "title": "系统维护通知",
            "content": "选课系统将于本周五22:00-次日6:00进行维护",
            "type": "system",
            "is_read": True,
            "created_at": datetime.now(),
            "link": None
        }
    ]

    # 筛选
    if type:
        notifications = [n for n in notifications if n["type"] == type]
    if is_read is not None:
        notifications = [n for n in notifications if n["is_read"] == is_read]

    return {
        "items": notifications,
        "total": len(notifications),
        "unread_count": len([n for n in notifications if not n["is_read"]])
    }


@router.get("/unread/count")
async def get_unread_count(
    # current_user = Depends(get_current_user)
):
    """获取未读通知数量"""
    # TODO: 从数据库获取
    return {"count": 3}


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    # current_user = Depends(get_current_user)
):
    """标记单条通知为已读"""
    # TODO: 更新数据库
    return {"message": "已标记为已读"}


@router.put("/read-all")
async def mark_all_as_read(
    # current_user = Depends(get_current_user)
):
    """标记所有通知为已读"""
    # TODO: 更新数据库
    return {"message": "已全部标记为已读"}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    # current_user = Depends(get_current_user)
):
    """删除单条通知"""
    # TODO: 从数据库删除
    return {"message": "删除成功"}


@router.delete("/clear")
async def clear_notifications(
    # current_user = Depends(get_current_user)
):
    """清空所有通知"""
    # TODO: 从数据库删除
    return {"message": "已清空所有通知"}


@router.post("")
async def create_notification(
    notification: NotificationCreate,
    # current_user = Depends(get_current_admin)
):
    """
    创建通知（管理员）
    - 可以发送给单个用户或所有用户
    """
    # TODO: 保存到数据库
    return {
        "message": "通知已发送",
        "id": 1
    }


# ==================== 辅助函数 ====================

async def send_notification(user_id: str, title: str, content: str, type: str = "system", link: str = None):
    """
    发送通知到指定用户
    可在其他模块中调用此函数发送通知
    """
    # TODO: 保存通知到数据库
    # TODO: 如果用户在线，通过 WebSocket 推送
    pass
