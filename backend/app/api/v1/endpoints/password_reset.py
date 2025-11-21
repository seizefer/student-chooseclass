"""
密码重置 API 端点
"""
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr

router = APIRouter()

# 存储重置令牌（生产环境应使用 Redis）
reset_tokens = {}


# ==================== 数据模型 ====================

class ForgotPasswordRequest(BaseModel):
    """忘记密码请求"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """重置密码请求"""
    token: str
    new_password: str


class VerifyTokenRequest(BaseModel):
    """验证令牌请求"""
    token: str


# ==================== API 端点 ====================

@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks
):
    """
    忘记密码 - 发送重置邮件
    """
    # TODO: 检查邮箱是否存在于数据库

    # 生成重置令牌
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=1)

    # 存储令牌（生产环境应使用 Redis 并设置过期时间）
    reset_tokens[token] = {
        "email": request.email,
        "expires_at": expires_at
    }

    # 发送重置邮件（后台任务）
    background_tasks.add_task(
        send_reset_email,
        request.email,
        token
    )

    return {
        "message": "如果该邮箱已注册，您将收到密码重置邮件"
    }


@router.post("/verify-reset-token")
async def verify_reset_token(request: VerifyTokenRequest):
    """
    验证重置令牌是否有效
    """
    token_data = reset_tokens.get(request.token)

    if not token_data:
        raise HTTPException(
            status_code=400,
            detail="无效的重置令牌"
        )

    if datetime.now() > token_data["expires_at"]:
        # 删除过期令牌
        del reset_tokens[request.token]
        raise HTTPException(
            status_code=400,
            detail="重置令牌已过期"
        )

    return {"valid": True}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    重置密码
    """
    # 验证令牌
    token_data = reset_tokens.get(request.token)

    if not token_data:
        raise HTTPException(
            status_code=400,
            detail="无效的重置令牌"
        )

    if datetime.now() > token_data["expires_at"]:
        del reset_tokens[request.token]
        raise HTTPException(
            status_code=400,
            detail="重置令牌已过期"
        )

    # 验证密码强度
    if len(request.new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="密码长度不能少于6位"
        )

    # TODO: 更新数据库中的密码
    # email = token_data["email"]
    # hashed_password = hash_password(request.new_password)
    # update_user_password(email, hashed_password)

    # 删除已使用的令牌
    del reset_tokens[request.token]

    return {"message": "密码重置成功，请使用新密码登录"}


# ==================== 邮箱验证端点 ====================

# 存储验证令牌
verification_tokens = {}


class SendVerificationRequest(BaseModel):
    """发送验证请求"""
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    """验证邮箱请求"""
    token: str


@router.post("/send-verification")
async def send_verification(
    background_tasks: BackgroundTasks,
    # current_user = Depends(get_current_user)
):
    """
    发送邮箱验证邮件
    """
    # TODO: 获取当前用户邮箱
    email = "user@example.com"  # 模拟

    # 生成验证令牌
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=24)

    verification_tokens[token] = {
        "email": email,
        "expires_at": expires_at
    }

    # 发送验证邮件
    background_tasks.add_task(
        send_verification_email,
        email,
        token
    )

    return {"message": "验证邮件已发送，请查收"}


@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest):
    """
    验证邮箱
    """
    token_data = verification_tokens.get(request.token)

    if not token_data:
        raise HTTPException(
            status_code=400,
            detail="无效的验证令牌"
        )

    if datetime.now() > token_data["expires_at"]:
        del verification_tokens[request.token]
        raise HTTPException(
            status_code=400,
            detail="验证令牌已过期"
        )

    # TODO: 更新用户邮箱验证状态
    # email = token_data["email"]
    # update_user_email_verified(email, True)

    del verification_tokens[request.token]

    return {"message": "邮箱验证成功"}


# ==================== 辅助函数 ====================

async def send_reset_email(email: str, token: str):
    """
    发送密码重置邮件
    """
    reset_url = f"http://localhost:5173/reset-password?token={token}"

    # TODO: 使用邮件服务发送
    # 这里只是打印日志
    print(f"发送密码重置邮件到 {email}")
    print(f"重置链接: {reset_url}")

    # 实际实现示例（使用 SMTP）:
    # import smtplib
    # from email.mime.text import MIMEText
    #
    # msg = MIMEText(f"点击链接重置密码: {reset_url}")
    # msg["Subject"] = "密码重置"
    # msg["From"] = "noreply@example.com"
    # msg["To"] = email
    #
    # with smtplib.SMTP("smtp.example.com", 587) as server:
    #     server.starttls()
    #     server.login("username", "password")
    #     server.send_message(msg)


async def send_verification_email(email: str, token: str):
    """
    发送邮箱验证邮件
    """
    verify_url = f"http://localhost:5173/verify-email?token={token}"

    print(f"发送验证邮件到 {email}")
    print(f"验证链接: {verify_url}")
