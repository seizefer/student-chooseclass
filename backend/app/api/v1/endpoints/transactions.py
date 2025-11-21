"""
转账系统API端点

@version: v1.0.0
@date: 2024-12-06
@changelog:
  v1.0.0:
    - 初始版本
    - 实现转账功能
    - 添加转账记录查询
    - 实现转账统计
    - 支持风险控制和限额管理
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.config import settings
from app.db.mysql_client import mysql_client
from app.schemas.common import ResponseModel, PaginationResponse
from app.api.v1.endpoints.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# 临时数据模式定义
from pydantic import BaseModel, Field

class TransactionCreate(BaseModel):
    recipient_id: str = Field(..., max_length=20, description="收款人学号")
    amount: float = Field(..., gt=0, le=1000, description="转账金额")
    description: Optional[str] = Field(None, max_length=200, description="转账说明")
    payment_password: str = Field(..., description="支付密码")

class TransactionResponse(BaseModel):
    transaction_id: int
    sender_id: str
    sender_name: Optional[str] = None
    recipient_id: str
    recipient_name: Optional[str] = None
    amount: float
    transaction_fee: float
    status: str
    description: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

class BalanceResponse(BaseModel):
    student_id: str
    balance: float
    daily_spent: float
    daily_limit: float
    monthly_spent: float


@router.post("/transfer", response_model=ResponseModel[TransactionResponse])
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[TransactionResponse]:
    """
    创建转账交易
    只有学生可以进行转账
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学生可以进行转账"
            )
        
        sender_id = current_user["student_id"]
        recipient_id = transaction_data.recipient_id
        amount = Decimal(str(transaction_data.amount))
        
        # 不能给自己转账
        if sender_id == recipient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能给自己转账"
            )
        
        # 检查收款人是否存在
        success, results, error = mysql_client.select(
            table="students",
            where={"student_id": recipient_id, "status": "active"}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="收款人不存在或账户已停用"
            )
        
        recipient = results[0]
        
        # 检查是否为好友关系
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
                detail="只能向好友转账"
            )
        
        # 验证支付密码（这里简化处理，实际应该有独立的支付密码系统）
        # 暂时使用登录密码验证
        from app.utils.security import verify_password
        success, results, error = mysql_client.select(
            table="students",
            where={"student_id": sender_id}
        )
        
        if success and results:
            stored_hash = results[0]["password_hash"]
            if not verify_password(transaction_data.payment_password, stored_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="支付密码错误"
                )
        
        # 检查余额（假设每个学生初始余额为1000元）
        success, results, error = mysql_client.execute_raw_sql(
            """
            SELECT 
                COALESCE(1000 + COALESCE(received.total, 0) - COALESCE(sent.total, 0), 1000) as balance
            FROM students s
            LEFT JOIN (
                SELECT recipient_id, SUM(amount) as total 
                FROM transactions 
                WHERE status = 'completed' AND recipient_id = :student_id
                GROUP BY recipient_id
            ) received ON s.student_id = received.recipient_id
            LEFT JOIN (
                SELECT sender_id, SUM(amount + transaction_fee) as total 
                FROM transactions 
                WHERE status = 'completed' AND sender_id = :student_id
                GROUP BY sender_id
            ) sent ON s.student_id = sent.sender_id
            WHERE s.student_id = :student_id
            """,
            {"student_id": sender_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="查询余额失败"
            )
        
        current_balance = Decimal(str(results[0]["balance"]))
        
        # 计算手续费（1%，最低0.1元）
        transaction_fee = max(amount * Decimal("0.01"), Decimal("0.1"))
        total_amount = amount + transaction_fee
        
        if current_balance < total_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"余额不足，当前余额: {current_balance}元，需要: {total_amount}元"
            )
        
        # 检查单笔限额
        if amount > Decimal(str(settings.MAX_TRANSACTION_AMOUNT)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"单笔转账金额不能超过{settings.MAX_TRANSACTION_AMOUNT}元"
            )
        
        # 检查日限额
        today = datetime.now().date()
        success, results, error = mysql_client.execute_raw_sql(
            """
            SELECT COALESCE(SUM(amount + transaction_fee), 0) as daily_spent
            FROM transactions 
            WHERE sender_id = :sender_id 
              AND DATE(created_at) = :today 
              AND status = 'completed'
            """,
            {"sender_id": sender_id, "today": today}
        )
        
        if success and results:
            daily_spent = Decimal(str(results[0]["daily_spent"]))
            if daily_spent + total_amount > Decimal(str(settings.DAILY_TRANSACTION_LIMIT)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"今日转账额度不足，已用: {daily_spent}元，限额: {settings.DAILY_TRANSACTION_LIMIT}元"
                )
        
        # 风险控制：大额转账需要额外验证
        is_high_risk = amount >= Decimal(str(settings.HIGH_RISK_AMOUNT))
        
        # 使用事务创建转账记录
        with mysql_client.transaction():
            transaction_dict = {
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "amount": float(amount),
                "transaction_fee": float(transaction_fee),
                "status": "pending" if is_high_risk else "completed",
                "description": transaction_data.description,
                "risk_level": "high" if is_high_risk else "normal"
            }
            
            if not is_high_risk:
                transaction_dict["completed_at"] = datetime.now().isoformat()
            
            success, insert_id, error = mysql_client.insert("transactions", transaction_dict)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"创建转账记录失败: {error}"
                )
        
        # 获取完整的转账信息
        sql = """
        SELECT 
            t.*,
            s1.name as sender_name,
            s2.name as recipient_name
        FROM transactions t
        LEFT JOIN students s1 ON t.sender_id = s1.student_id
        LEFT JOIN students s2 ON t.recipient_id = s2.student_id
        WHERE t.transaction_id = :transaction_id
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"transaction_id": insert_id})
        
        if success and results:
            transaction = TransactionResponse(**results[0])
        else:
            transaction_dict["transaction_id"] = insert_id
            transaction = TransactionResponse(**transaction_dict)
        
        message = "转账成功" if not is_high_risk else "大额转账已提交，等待审核"
        
        return ResponseModel(
            code=200,
            message=message,
            data=transaction
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建转账失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建转账失败"
        )


@router.get("/balance", response_model=ResponseModel[BalanceResponse])
async def get_balance(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[BalanceResponse]:
    """
    查询账户余额和限额信息
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学生可以查询余额"
            )
        
        student_id = current_user["student_id"]
        
        # 查询余额信息
        sql = """
        SELECT 
            s.student_id,
            COALESCE(1000 + COALESCE(received.total, 0) - COALESCE(sent.total, 0), 1000) as balance,
            COALESCE(today_spent.daily_spent, 0) as daily_spent,
            COALESCE(month_spent.monthly_spent, 0) as monthly_spent
        FROM students s
        LEFT JOIN (
            SELECT recipient_id, SUM(amount) as total 
            FROM transactions 
            WHERE status = 'completed' AND recipient_id = :student_id
            GROUP BY recipient_id
        ) received ON s.student_id = received.recipient_id
        LEFT JOIN (
            SELECT sender_id, SUM(amount + transaction_fee) as total 
            FROM transactions 
            WHERE status = 'completed' AND sender_id = :student_id
            GROUP BY sender_id
        ) sent ON s.student_id = sent.sender_id
        LEFT JOIN (
            SELECT sender_id, SUM(amount + transaction_fee) as daily_spent
            FROM transactions 
            WHERE sender_id = :student_id 
              AND DATE(created_at) = CURDATE()
              AND status = 'completed'
            GROUP BY sender_id
        ) today_spent ON s.student_id = today_spent.sender_id
        LEFT JOIN (
            SELECT sender_id, SUM(amount + transaction_fee) as monthly_spent
            FROM transactions 
            WHERE sender_id = :student_id 
              AND YEAR(created_at) = YEAR(CURDATE())
              AND MONTH(created_at) = MONTH(CURDATE())
              AND status = 'completed'
            GROUP BY sender_id
        ) month_spent ON s.student_id = month_spent.sender_id
        WHERE s.student_id = :student_id
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"student_id": student_id})
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询余额失败: {error}"
            )
        
        balance_data = results[0]
        balance_data["daily_limit"] = settings.DAILY_TRANSACTION_LIMIT
        
        balance = BalanceResponse(**balance_data)
        
        return ResponseModel(
            code=200,
            message="查询余额成功",
            data=balance
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询余额失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="查询余额失败"
        )


@router.get("/history", response_model=ResponseModel[PaginationResponse[TransactionResponse]])
async def get_transaction_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    transaction_type: Optional[str] = Query(None, description="交易类型: sent/received"),
    status: Optional[str] = Query(None, description="交易状态"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[PaginationResponse[TransactionResponse]]:
    """
    获取转账记录
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学生可以查看转账记录"
            )
        
        student_id = current_user["student_id"]
        
        # 构建WHERE条件
        where_conditions = []
        params = {"student_id": student_id}
        
        if transaction_type == "sent":
            where_conditions.append("t.sender_id = :student_id")
        elif transaction_type == "received":
            where_conditions.append("t.recipient_id = :student_id")
        else:
            where_conditions.append("(t.sender_id = :student_id OR t.recipient_id = :student_id)")
        
        if status:
            where_conditions.append("t.status = :status")
            params["status"] = status
        
        where_clause = " AND ".join(where_conditions)
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取总数
        count_sql = f"""
        SELECT COUNT(*) as total 
        FROM transactions t
        WHERE {where_clause}
        """
        
        success, count_results, error = mysql_client.execute_raw_sql(count_sql, params)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询转账记录总数失败: {error}"
            )
        
        total = int(count_results[0]["total"]) if count_results else 0
        
        # 获取分页数据
        data_sql = f"""
        SELECT 
            t.*,
            s1.name as sender_name,
            s2.name as recipient_name
        FROM transactions t
        LEFT JOIN students s1 ON t.sender_id = s1.student_id
        LEFT JOIN students s2 ON t.recipient_id = s2.student_id
        WHERE {where_clause}
        ORDER BY t.created_at DESC 
        LIMIT {page_size} OFFSET {offset}
        """
        
        success, results, error = mysql_client.execute_raw_sql(data_sql, params)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询转账记录失败: {error}"
            )
        
        # 转换结果
        transactions = []
        for transaction in results:
            try:
                transactions.append(TransactionResponse(**transaction))
            except Exception as e:
                logger.warning(f"转换转账数据失败: {e}")
                continue
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        return ResponseModel(
            code=200,
            message="获取转账记录成功",
            data=PaginationResponse(
                items=transactions,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取转账记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取转账记录失败"
        )


@router.get("/statistics", response_model=ResponseModel[Dict[str, Any]])
async def get_transaction_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[Dict[str, Any]]:
    """
    获取转账统计信息
    管理员可以查看全局统计，学生只能查看个人统计
    """
    try:
        student_id = current_user.get("student_id")
        is_admin = current_user.get("user_type") == "admin"
        
        if is_admin:
            # 管理员查看全局统计
            sql = """
            SELECT 
                COUNT(*) as total_transactions,
                COUNT(DISTINCT sender_id) as active_users,
                SUM(amount) as total_amount,
                SUM(transaction_fee) as total_fees,
                AVG(amount) as avg_amount,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count,
                COUNT(CASE WHEN risk_level = 'high' THEN 1 END) as high_risk_count
            FROM transactions
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            """
            params = {}
        else:
            # 学生查看个人统计
            if not student_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            
            sql = """
            SELECT 
                COUNT(CASE WHEN sender_id = :student_id THEN 1 END) as sent_count,
                COUNT(CASE WHEN recipient_id = :student_id THEN 1 END) as received_count,
                COALESCE(SUM(CASE WHEN sender_id = :student_id THEN amount + transaction_fee END), 0) as total_sent,
                COALESCE(SUM(CASE WHEN recipient_id = :student_id THEN amount END), 0) as total_received,
                COALESCE(AVG(CASE WHEN sender_id = :student_id THEN amount END), 0) as avg_sent_amount,
                COUNT(CASE WHEN (sender_id = :student_id OR recipient_id = :student_id) AND status = 'completed' THEN 1 END) as completed_count,
                COUNT(CASE WHEN (sender_id = :student_id OR recipient_id = :student_id) AND status = 'pending' THEN 1 END) as pending_count
            FROM transactions
            WHERE (sender_id = :student_id OR recipient_id = :student_id)
              AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            """
            params = {"student_id": student_id}
        
        success, results, error = mysql_client.execute_raw_sql(sql, params)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询转账统计失败: {error}"
            )
        
        statistics = results[0] if results else {}
        
        return ResponseModel(
            code=200,
            message="获取转账统计成功",
            data=statistics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取转账统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取转账统计失败"
        ) 