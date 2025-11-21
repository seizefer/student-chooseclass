"""
消息系统API端点

@version: v1.0.0
@date: 2024-12-06
@changelog:
  v1.0.0:
    - 初始版本
    - 实现消息发送和接收功能
    - 添加消息列表查看
    - 实现消息状态管理
    - 支持消息搜索和分页
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
import logging
from datetime import datetime

from app.core.config import settings
from app.db.mysql_client import mysql_client
from app.schemas.common import ResponseModel, PaginationResponse
from app.api.v1.endpoints.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# 临时数据模式定义
from pydantic import BaseModel, Field

class MessageCreate(BaseModel):
    recipient_id: str = Field(..., max_length=20, description="收件人学号")
    subject: str = Field(..., max_length=100, description="消息主题")
    content: str = Field(..., max_length=1000, description="消息内容")
    message_type: Optional[str] = Field("personal", description="消息类型")

class MessageResponse(BaseModel):
    message_id: int
    sender_id: str
    sender_name: Optional[str] = None
    recipient_id: str
    recipient_name: Optional[str] = None
    subject: str
    content: str
    message_type: str
    status: str
    is_read: bool
    created_at: Optional[str] = None
    read_at: Optional[str] = None

class MessageStatusUpdate(BaseModel):
    is_read: bool = Field(..., description="是否已读")


@router.post("/send", response_model=ResponseModel[MessageResponse])
async def send_message(
    message_data: MessageCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[MessageResponse]:
    """
    发送消息
    学生只能给好友发送消息，管理员可以给任何人发送
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") not in ["student", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        sender_id = current_user.get("student_id") or current_user.get("admin_id")
        sender_type = current_user.get("user_type")
        recipient_id = message_data.recipient_id
        
        # 不能给自己发消息
        if sender_id == recipient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能给自己发消息"
            )
        
        # 检查收件人是否存在
        success, results, error = mysql_client.select(
            table="students",
            where={"student_id": recipient_id, "status": "active"}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="收件人不存在或账户已停用"
            )
        
        # 如果是学生发送，检查好友关系
        if sender_type == "student":
            success, results, error = mysql_client.execute_raw_sql(
                """
                SELECT * FROM friendships 
                WHERE ((student_id = :sender_id AND friend_id = :recipient_id) 
                      OR (student_id = :recipient_id AND friend_id = :sender_id))
                  AND status = 'accepted'
                """,
                {"sender_id": sender_id, "recipient_id": recipient_id}
            )
            
            if not success or not results:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="只能向好友发送消息"
                )
        
        # 创建消息
        message_dict = {
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "subject": message_data.subject,
            "content": message_data.content,
            "message_type": message_data.message_type,
            "status": "sent",
            "is_read": False
        }
        
        success, insert_id, error = mysql_client.insert("messages", message_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"发送消息失败: {error}"
            )
        
        # 获取完整的消息信息
        sql = """
        SELECT 
            m.*,
            s1.name as sender_name,
            s2.name as recipient_name
        FROM messages m
        LEFT JOIN students s1 ON m.sender_id = s1.student_id
        LEFT JOIN students s2 ON m.recipient_id = s2.student_id
        WHERE m.message_id = :message_id
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"message_id": insert_id})
        
        if success and results:
            message = MessageResponse(**results[0])
        else:
            message_dict["message_id"] = insert_id
            message = MessageResponse(**message_dict)
        
        return ResponseModel(
            code=200,
            message="消息发送成功",
            data=message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送消息失败"
        )


@router.get("/inbox", response_model=ResponseModel[PaginationResponse[MessageResponse]])
async def get_inbox_messages(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    is_read: Optional[bool] = Query(None, description="是否已读"),
    message_type: Optional[str] = Query(None, description="消息类型"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[PaginationResponse[MessageResponse]]:
    """
    获取收件箱消息列表
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") not in ["student", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        recipient_id = current_user.get("student_id") or current_user.get("admin_id")
        
        # 构建WHERE条件
        where_conditions = ["m.recipient_id = :recipient_id"]
        params = {"recipient_id": recipient_id}
        
        if is_read is not None:
            where_conditions.append("m.is_read = :is_read")
            params["is_read"] = is_read
        
        if message_type:
            where_conditions.append("m.message_type = :message_type")
            params["message_type"] = message_type
        
        if search:
            where_conditions.append("(m.subject LIKE :search OR m.content LIKE :search)")
            params["search"] = f"%{search}%"
        
        where_clause = " AND ".join(where_conditions)
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取总数
        count_sql = f"""
        SELECT COUNT(*) as total 
        FROM messages m
        WHERE {where_clause}
        """
        
        success, count_results, error = mysql_client.execute_raw_sql(count_sql, params)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询消息总数失败: {error}"
            )
        
        total = int(count_results[0]["total"]) if count_results else 0
        
        # 获取分页数据
        data_sql = f"""
        SELECT 
            m.*,
            s1.name as sender_name,
            s2.name as recipient_name
        FROM messages m
        LEFT JOIN students s1 ON m.sender_id = s1.student_id
        LEFT JOIN students s2 ON m.recipient_id = s2.student_id
        WHERE {where_clause}
        ORDER BY m.created_at DESC 
        LIMIT {page_size} OFFSET {offset}
        """
        
        success, results, error = mysql_client.execute_raw_sql(data_sql, params)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询收件箱消息失败: {error}"
            )
        
        # 转换结果
        messages = []
        for message in results:
            try:
                messages.append(MessageResponse(**message))
            except Exception as e:
                logger.warning(f"转换消息数据失败: {e}")
                continue
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        return ResponseModel(
            code=200,
            message="获取收件箱消息成功",
            data=PaginationResponse(
                items=messages,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取收件箱消息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取收件箱消息失败"
        )


@router.get("/sent", response_model=ResponseModel[PaginationResponse[MessageResponse]])
async def get_sent_messages(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    message_type: Optional[str] = Query(None, description="消息类型"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[PaginationResponse[MessageResponse]]:
    """
    获取发件箱消息列表
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") not in ["student", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        sender_id = current_user.get("student_id") or current_user.get("admin_id")
        
        # 构建WHERE条件
        where_conditions = ["m.sender_id = :sender_id"]
        params = {"sender_id": sender_id}
        
        if message_type:
            where_conditions.append("m.message_type = :message_type")
            params["message_type"] = message_type
        
        if search:
            where_conditions.append("(m.subject LIKE :search OR m.content LIKE :search)")
            params["search"] = f"%{search}%"
        
        where_clause = " AND ".join(where_conditions)
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取总数
        count_sql = f"""
        SELECT COUNT(*) as total 
        FROM messages m
        WHERE {where_clause}
        """
        
        success, count_results, error = mysql_client.execute_raw_sql(count_sql, params)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询消息总数失败: {error}"
            )
        
        total = int(count_results[0]["total"]) if count_results else 0
        
        # 获取分页数据
        data_sql = f"""
        SELECT 
            m.*,
            s1.name as sender_name,
            s2.name as recipient_name
        FROM messages m
        LEFT JOIN students s1 ON m.sender_id = s1.student_id
        LEFT JOIN students s2 ON m.recipient_id = s2.student_id
        WHERE {where_clause}
        ORDER BY m.created_at DESC 
        LIMIT {page_size} OFFSET {offset}
        """
        
        success, results, error = mysql_client.execute_raw_sql(data_sql, params)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询发件箱消息失败: {error}"
            )
        
        # 转换结果
        messages = []
        for message in results:
            try:
                messages.append(MessageResponse(**message))
            except Exception as e:
                logger.warning(f"转换消息数据失败: {e}")
                continue
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        return ResponseModel(
            code=200,
            message="获取发件箱消息成功",
            data=PaginationResponse(
                items=messages,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取发件箱消息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取发件箱消息失败"
        )


@router.get("/{message_id}", response_model=ResponseModel[MessageResponse])
async def get_message(
    message_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[MessageResponse]:
    """
    获取单个消息详情
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") not in ["student", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        user_id = current_user.get("student_id") or current_user.get("admin_id")
        
        # 获取消息详情
        sql = """
        SELECT 
            m.*,
            s1.name as sender_name,
            s2.name as recipient_name
        FROM messages m
        LEFT JOIN students s1 ON m.sender_id = s1.student_id
        LEFT JOIN students s2 ON m.recipient_id = s2.student_id
        WHERE m.message_id = :message_id
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"message_id": message_id})
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询消息失败: {error}"
            )
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="消息不存在"
            )
        
        message = results[0]
        
        # 检查权限：只能查看自己发送或接收的消息
        if message["sender_id"] != user_id and message["recipient_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您无权查看此消息"
            )
        
        # 如果是接收的消息且未读，标记为已读
        if message["recipient_id"] == user_id and not message["is_read"]:
            success, affected_rows, error = mysql_client.update(
                table="messages",
                data={"is_read": True, "read_at": datetime.now().isoformat()},
                where={"message_id": message_id}
            )
            
            if success:
                message["is_read"] = True
                message["read_at"] = datetime.now().isoformat()
        
        message_response = MessageResponse(**message)
        
        return ResponseModel(
            code=200,
            message="获取消息详情成功",
            data=message_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取消息详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取消息详情失败"
        )


@router.put("/{message_id}/status", response_model=ResponseModel[MessageResponse])
async def update_message_status(
    message_id: int,
    status_data: MessageStatusUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[MessageResponse]:
    """
    更新消息状态（标记为已读/未读）
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") not in ["student", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        user_id = current_user.get("student_id") or current_user.get("admin_id")
        
        # 检查消息是否存在
        success, results, error = mysql_client.select(
            table="messages",
            where={"message_id": message_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="消息不存在"
            )
        
        message = results[0]
        
        # 只有收件人可以更新消息状态
        if message["recipient_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有收件人可以更新消息状态"
            )
        
        # 更新消息状态
        update_data = {"is_read": status_data.is_read}
        if status_data.is_read:
            update_data["read_at"] = datetime.now().isoformat()
        else:
            update_data["read_at"] = None
        
        success, affected_rows, error = mysql_client.update(
            table="messages",
            data=update_data,
            where={"message_id": message_id}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新消息状态失败: {error}"
            )
        
        # 获取更新后的消息信息
        sql = """
        SELECT 
            m.*,
            s1.name as sender_name,
            s2.name as recipient_name
        FROM messages m
        LEFT JOIN students s1 ON m.sender_id = s1.student_id
        LEFT JOIN students s2 ON m.recipient_id = s2.student_id
        WHERE m.message_id = :message_id
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"message_id": message_id})
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取更新后的消息信息失败"
            )
        
        message_response = MessageResponse(**results[0])
        
        return ResponseModel(
            code=200,
            message="消息状态更新成功",
            data=message_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新消息状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新消息状态失败"
        )


@router.delete("/{message_id}", response_model=ResponseModel[None])
async def delete_message(
    message_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[None]:
    """
    删除消息
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") not in ["student", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        user_id = current_user.get("student_id") or current_user.get("admin_id")
        
        # 检查消息是否存在
        success, results, error = mysql_client.select(
            table="messages",
            where={"message_id": message_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="消息不存在"
            )
        
        message = results[0]
        
        # 检查权限：只能删除自己发送或接收的消息
        if message["sender_id"] != user_id and message["recipient_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您无权删除此消息"
            )
        
        # 删除消息
        success, deleted_rows, error = mysql_client.delete(
            table="messages",
            where={"message_id": message_id}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除消息失败: {error}"
            )
        
        return ResponseModel(
            code=200,
            message="消息删除成功",
            data=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除消息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除消息失败"
        )


@router.get("/unread/count", response_model=ResponseModel[Dict[str, int]])
async def get_unread_count(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[Dict[str, int]]:
    """
    获取未读消息数量
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") not in ["student", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        user_id = current_user.get("student_id") or current_user.get("admin_id")
        
        # 查询未读消息数量
        sql = """
        SELECT COUNT(*) as unread_count
        FROM messages 
        WHERE recipient_id = :user_id AND is_read = FALSE
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"user_id": user_id})
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询未读消息数量失败: {error}"
            )
        
        unread_count = int(results[0]["unread_count"]) if results else 0
        
        return ResponseModel(
            code=200,
            message="获取未读消息数量成功",
            data={"unread_count": unread_count}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取未读消息数量失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取未读消息数量失败"
        ) 