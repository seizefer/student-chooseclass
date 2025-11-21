"""
用户认证API端点
包含登录、注册、Token验证等功能
"""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

from app.core.config import settings
from app.db.mysql_client import mysql_client
from app.schemas.auth import Token, UserLogin, UserRegister, UserResponse
from app.schemas.common import ResponseModel
from app.utils.security import create_access_token, verify_password, get_password_hash

logger = logging.getLogger(__name__)

router = APIRouter()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_user_by_id(user_id: str, user_type: str = "student") -> Optional[Dict[str, Any]]:
    """根据用户ID获取用户信息"""
    try:
        if user_type == "student":
            table = "students"
            id_field = "student_id"
        else:
            table = "administrators"
            id_field = "admin_id"
        
        success, results, error = mysql_client.select(
            table=table,
            where={id_field: user_id}
        )
        
        if success and results:
            return results[0]
        return None
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        return None


async def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """用户认证"""
    try:
        # 先在学生表中查找
        user = await get_user_by_id(username, "student")
        user_type = "student"
        
        # 如果在学生表中没找到，在管理员表中查找
        if not user:
            user = await get_user_by_id(username, "admin")
            user_type = "admin"
        
        if not user:
            return None
        
        # 验证密码
        if not verify_password(password, user.get("password_hash", "")):
            return None
        
        # 添加用户类型到返回的用户信息中
        user["user_type"] = user_type
        
        # 记录登录日志
        await record_login_log(username, user_type, "success")
        
        return user
        
    except Exception as e:
        logger.error(f"用户认证失败: {str(e)}")
        return None


async def record_login_log(user_id: str, user_type: str, status: str, 
                          ip_address: str = None, user_agent: str = None):
    """记录登录日志"""
    try:
        log_data = {
            "user_id": user_id,
            "user_type": user_type,
            "login_status": status,
            "ip_address": ip_address or "unknown",
            "user_agent": user_agent or "unknown"
        }
        
        success, insert_id, error = mysql_client.insert("login_logs", log_data)
        if not success:
            logger.error(f"记录登录日志失败: {error}")
            
    except Exception as e:
        logger.error(f"记录登录日志异常: {str(e)}")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        user_type: str = payload.get("user_type", "student")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_id(user_id, user_type)
    if user is None:
        raise credentials_exception
    
    user["user_type"] = user_type
    return user


@router.post("/login", response_model=ResponseModel[Token])
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> ResponseModel[Token]:
    """
    用户登录
    """
    try:
        # 获取客户端信息
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # 认证用户
        user = await authenticate_user(form_data.username, form_data.password)
        if not user:
            # 记录失败的登录尝试
            await record_login_log(form_data.username, "unknown", "failed", client_ip, user_agent)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["student_id"] if user["user_type"] == "student" else user["admin_id"], 
                  "user_type": user["user_type"]},
            expires_delta=access_token_expires
        )
        
        # 更新登录日志中的用户代理和IP
        await record_login_log(
            user["student_id"] if user["user_type"] == "student" else user["admin_id"],
            user["user_type"], 
            "success", 
            client_ip, 
            user_agent
        )
        
        return ResponseModel(
            code=200,
            message="登录成功",
            data=Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user_type=user["user_type"]
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录服务异常"
        )


@router.post("/register", response_model=ResponseModel[UserResponse])
async def register(user_data: UserRegister) -> ResponseModel[UserResponse]:
    """
    学生注册
    """
    try:
        # 检查学号是否已存在
        success, results, error = mysql_client.select(
            table="students",
            where={"student_id": user_data.student_id}
        )
        
        if success and results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="学号已存在"
            )
        
        # 检查身份证号是否已存在
        success, results, error = mysql_client.select(
            table="students",
            where={"id_number": user_data.id_number}
        )
        
        if success and results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="身份证号已存在"
            )
        
        # 检查邮箱是否已存在
        if user_data.email:
            success, results, error = mysql_client.select(
                table="students",
                where={"email": user_data.email}
            )
            
            if success and results:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已存在"
                )
        
        # 验证院系是否存在
        if user_data.department_id:
            success, results, error = mysql_client.select(
                table="departments",
                where={"department_id": user_data.department_id}
            )
            
            if not success or not results:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="院系不存在"
                )
        
        # 创建新学生记录
        student_data = {
            "student_id": user_data.student_id,
            "password_hash": get_password_hash(user_data.password),
            "name": user_data.name,
            "birth_date": user_data.birth_date.isoformat() if user_data.birth_date else None,
            "id_number": user_data.id_number,
            "address": user_data.address,
            "email": user_data.email,
            "phone": user_data.phone,
            "department_id": user_data.department_id,
            "major": user_data.major,
            "grade": user_data.grade,
            "balance": 0.00,
            "status": "active"
        }
        
        success, insert_id, error = mysql_client.insert("students", student_data)
        
        if not success:
            logger.error(f"注册失败: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"注册失败: {error}"
            )
        
        # 返回用户信息（不包含密码）
        del student_data["password_hash"]
        
        return ResponseModel(
            code=200,
            message="注册成功",
            data=UserResponse(**student_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"注册异常: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册服务异常"
        )


@router.get("/me", response_model=ResponseModel[UserResponse])
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[UserResponse]:
    """
    获取当前用户信息
    """
    try:
        # 移除敏感信息
        safe_user = current_user.copy()
        if "password_hash" in safe_user:
            del safe_user["password_hash"]
        
        return ResponseModel(
            code=200,
            message="获取用户信息成功",
            data=UserResponse(**safe_user)
        )
        
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户信息失败"
        )


@router.post("/refresh", response_model=ResponseModel[Token])
async def refresh_token(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[Token]:
    """
    刷新访问令牌
    """
    try:
        # 创建新的访问令牌
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user["student_id"] if current_user["user_type"] == "student" else current_user["admin_id"], 
                  "user_type": current_user["user_type"]},
            expires_delta=access_token_expires
        )
        
        return ResponseModel(
            code=200,
            message="令牌刷新成功",
            data=Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user_type=current_user["user_type"]
            )
        )
        
    except Exception as e:
        logger.error(f"刷新令牌失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刷新令牌失败"
        )


@router.post("/logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[None]:
    """
    用户登出
    """
    try:
        # 在实际应用中，可以将令牌加入黑名单
        # 这里暂时只记录登出日志
        user_id = current_user["student_id"] if current_user["user_type"] == "student" else current_user["admin_id"]
        
        # 更新登录日志的登出时间
        success, affected_rows, error = mysql_client.update(
            table="login_logs",
            data={"logout_time": datetime.now().isoformat()},
            where={
                "user_id": user_id,
                "user_type": current_user["user_type"],
                "logout_time": None
            }
        )
        
        return ResponseModel(
            code=200,
            message="登出成功",
            data=None
        )
        
    except Exception as e:
        logger.error(f"登出失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登出失败"
        ) 