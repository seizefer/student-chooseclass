"""
好友系统API端点

@version: v1.0.0
@date: 2024-12-06
@changelog:
  v1.0.0:
    - 初始版本
    - 实现好友添加和删除功能
    - 添加好友列表查看
    - 实现好友推荐功能
    - 支持好友申请审批流程
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

class FriendRequestCreate(BaseModel):
    friend_id: str = Field(..., max_length=20, description="好友学号")
    message: Optional[str] = Field(None, max_length=200, description="申请留言")

class FriendRequestResponse(BaseModel):
    status: str = Field(..., description="操作结果")

class FriendshipResponse(BaseModel):
    friendship_id: int
    student_id: str
    friend_id: str
    friend_name: Optional[str] = None
    friend_major: Optional[str] = None
    friend_avatar: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class FriendRecommendationResponse(BaseModel):
    student_id: str
    name: str
    major: Optional[str] = None
    grade: Optional[str] = None
    department_name: Optional[str] = None
    common_friends: int
    common_courses: int
    recommendation_score: float


@router.post("/request", response_model=ResponseModel[FriendRequestResponse])
async def send_friend_request(
    request_data: FriendRequestCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[FriendRequestResponse]:
    """
    发送好友申请
    只有学生可以发送好友申请
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学生可以发送好友申请"
            )
        
        student_id = current_user["student_id"]
        friend_id = request_data.friend_id
        
        # 不能添加自己为好友
        if student_id == friend_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能添加自己为好友"
            )
        
        # 检查目标用户是否存在
        success, results, error = mysql_client.select(
            table="students",
            where={"student_id": friend_id, "status": "active"}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="目标用户不存在或已停用"
            )
        
        # 检查是否已经是好友或已有申请记录
        success, results, error = mysql_client.execute_raw_sql(
            """
            SELECT * FROM friendships 
            WHERE (student_id = :student_id AND friend_id = :friend_id) 
               OR (student_id = :friend_id AND friend_id = :student_id)
            """,
            {"student_id": student_id, "friend_id": friend_id}
        )
        
        if success and results:
            existing_status = results[0]["status"]
            if existing_status == "accepted":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="你们已经是好友了"
                )
            elif existing_status == "pending":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="已有待处理的好友申请"
                )
        
        # 检查好友数量限制
        success, results, error = mysql_client.execute_raw_sql(
            """
            SELECT COUNT(*) as friend_count 
            FROM friendships 
            WHERE (student_id = :student_id OR friend_id = :student_id) 
              AND status = 'accepted'
            """,
            {"student_id": student_id}
        )
        
        if success and results:
            friend_count = int(results[0]["friend_count"])
            if friend_count >= settings.MAX_FRIENDS_COUNT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"好友数量已达上限({settings.MAX_FRIENDS_COUNT})"
                )
        
        # 创建好友申请
        friendship_data = {
            "student_id": student_id,
            "friend_id": friend_id,
            "status": "pending",
            "message": request_data.message
        }
        
        success, insert_id, error = mysql_client.insert("friendships", friendship_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"发送好友申请失败: {error}"
            )
        
        return ResponseModel(
            code=200,
            message="好友申请发送成功",
            data=FriendRequestResponse(status="sent")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发送好友申请失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送好友申请失败"
        )


@router.put("/{friendship_id}/accept", response_model=ResponseModel[FriendRequestResponse])
async def accept_friend_request(
    friendship_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[FriendRequestResponse]:
    """
    接受好友申请
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学生可以处理好友申请"
            )
        
        student_id = current_user["student_id"]
        
        # 检查好友申请是否存在且是发给当前用户的
        success, results, error = mysql_client.select(
            table="friendships",
            where={"friendship_id": friendship_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="好友申请不存在"
            )
        
        friendship = results[0]
        
        if friendship["friend_id"] != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您无权处理此好友申请"
            )
        
        if friendship["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该好友申请已处理"
            )
        
        # 更新好友申请状态
        success, affected_rows, error = mysql_client.update(
            table="friendships",
            data={"status": "accepted"},
            where={"friendship_id": friendship_id}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"接受好友申请失败: {error}"
            )
        
        return ResponseModel(
            code=200,
            message="好友申请已接受",
            data=FriendRequestResponse(status="accepted")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"接受好友申请失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="接受好友申请失败"
        )


@router.put("/{friendship_id}/reject", response_model=ResponseModel[FriendRequestResponse])
async def reject_friend_request(
    friendship_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[FriendRequestResponse]:
    """
    拒绝好友申请
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学生可以处理好友申请"
            )
        
        student_id = current_user["student_id"]
        
        # 检查好友申请是否存在且是发给当前用户的
        success, results, error = mysql_client.select(
            table="friendships",
            where={"friendship_id": friendship_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="好友申请不存在"
            )
        
        friendship = results[0]
        
        if friendship["friend_id"] != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您无权处理此好友申请"
            )
        
        if friendship["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该好友申请已处理"
            )
        
        # 更新好友申请状态
        success, affected_rows, error = mysql_client.update(
            table="friendships",
            data={"status": "rejected"},
            where={"friendship_id": friendship_id}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"拒绝好友申请失败: {error}"
            )
        
        return ResponseModel(
            code=200,
            message="好友申请已拒绝",
            data=FriendRequestResponse(status="rejected")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"拒绝好友申请失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="拒绝好友申请失败"
        )


@router.get("/list", response_model=ResponseModel[List[FriendshipResponse]])
async def get_friends_list(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[List[FriendshipResponse]]:
    """
    获取好友列表
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学生可以查看好友列表"
            )
        
        student_id = current_user["student_id"]
        
        # 获取好友列表
        sql = """
        SELECT 
            f.*,
            CASE 
                WHEN f.student_id = :student_id THEN s2.name 
                ELSE s1.name 
            END as friend_name,
            CASE 
                WHEN f.student_id = :student_id THEN s2.major 
                ELSE s1.major 
            END as friend_major
        FROM friendships f
        LEFT JOIN students s1 ON f.student_id = s1.student_id
        LEFT JOIN students s2 ON f.friend_id = s2.student_id
        WHERE (f.student_id = :student_id OR f.friend_id = :student_id)
          AND f.status = 'accepted'
        ORDER BY f.created_at DESC
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"student_id": student_id})
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取好友列表失败: {error}"
            )
        
        # 转换结果
        friends = []
        for friendship in results:
            try:
                # 确定好友ID
                if friendship["student_id"] == student_id:
                    friend_id = friendship["friend_id"]
                else:
                    friend_id = friendship["student_id"]
                
                friendship["friend_id"] = friend_id
                friends.append(FriendshipResponse(**friendship))
            except Exception as e:
                logger.warning(f"转换好友数据失败: {e}")
                continue
        
        return ResponseModel(
            code=200,
            message="获取好友列表成功",
            data=friends
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取好友列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取好友列表失败"
        )


@router.get("/requests", response_model=ResponseModel[List[FriendshipResponse]])
async def get_friend_requests(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[List[FriendshipResponse]]:
    """
    获取好友申请列表（收到的申请）
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学生可以查看好友申请"
            )
        
        student_id = current_user["student_id"]
        
        # 获取收到的好友申请
        sql = """
        SELECT 
            f.*,
            s.name as friend_name,
            s.major as friend_major
        FROM friendships f
        LEFT JOIN students s ON f.student_id = s.student_id
        WHERE f.friend_id = :student_id AND f.status = 'pending'
        ORDER BY f.created_at DESC
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"student_id": student_id})
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取好友申请失败: {error}"
            )
        
        # 转换结果
        requests = []
        for request in results:
            try:
                requests.append(FriendshipResponse(**request))
            except Exception as e:
                logger.warning(f"转换好友申请数据失败: {e}")
                continue
        
        return ResponseModel(
            code=200,
            message="获取好友申请成功",
            data=requests
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取好友申请失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取好友申请失败"
        )


@router.get("/recommendations", response_model=ResponseModel[List[FriendRecommendationResponse]])
async def get_friend_recommendations(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[List[FriendRecommendationResponse]]:
    """
    获取好友推荐列表
    使用存储过程计算推荐算法
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学生可以查看好友推荐"
            )
        
        student_id = current_user["student_id"]
        
        # 调用好友推荐存储过程
        sql = f"CALL GetFriendRecommendations('{student_id}', {settings.FRIEND_RECOMMENDATION_COUNT})"
        
        success, results, error = mysql_client.execute_raw_sql(sql)
        
        if not success:
            # 如果存储过程失败，使用简单的推荐算法
            logger.warning(f"存储过程调用失败，使用备用算法: {error}")
            
            # 简单推荐：同院系、同年级且不是好友的学生
            sql = """
            SELECT 
                s.student_id,
                s.name,
                s.major,
                s.grade,
                d.department_name,
                0 as common_friends,
                0 as common_courses,
                1.0 as recommendation_score
            FROM students s
            LEFT JOIN departments d ON s.department_id = d.department_id
            WHERE s.department_id = (
                SELECT department_id FROM students WHERE student_id = :student_id
            )
            AND s.student_id != :student_id
            AND s.status = 'active'
            AND s.student_id NOT IN (
                SELECT CASE 
                    WHEN student_id = :student_id THEN friend_id 
                    ELSE student_id 
                END as friend_id
                FROM friendships 
                WHERE (student_id = :student_id OR friend_id = :student_id) 
                  AND status IN ('accepted', 'pending')
            )
            LIMIT :limit
            """
            
            success, results, error = mysql_client.execute_raw_sql(
                sql, 
                {
                    "student_id": student_id, 
                    "limit": settings.FRIEND_RECOMMENDATION_COUNT
                }
            )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取好友推荐失败: {error}"
            )
        
        # 转换结果
        recommendations = []
        for recommendation in results:
            try:
                recommendations.append(FriendRecommendationResponse(**recommendation))
            except Exception as e:
                logger.warning(f"转换推荐数据失败: {e}")
                continue
        
        return ResponseModel(
            code=200,
            message="获取好友推荐成功",
            data=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取好友推荐失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取好友推荐失败"
        )


@router.delete("/{friendship_id}", response_model=ResponseModel[None])
async def delete_friendship(
    friendship_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[None]:
    """
    删除好友关系
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学生可以删除好友"
            )
        
        student_id = current_user["student_id"]
        
        # 检查好友关系是否存在
        success, results, error = mysql_client.select(
            table="friendships",
            where={"friendship_id": friendship_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="好友关系不存在"
            )
        
        friendship = results[0]
        
        # 检查权限：只能删除自己相关的好友关系
        if friendship["student_id"] != student_id and friendship["friend_id"] != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您无权删除此好友关系"
            )
        
        # 删除好友关系
        success, deleted_rows, error = mysql_client.delete(
            table="friendships",
            where={"friendship_id": friendship_id}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除好友关系失败: {error}"
            )
        
        return ResponseModel(
            code=200,
            message="好友关系已删除",
            data=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除好友关系失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除好友关系失败"
        ) 