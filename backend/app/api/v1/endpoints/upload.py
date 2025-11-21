"""
文件上传 API 端点
"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

# 上传目录配置
UPLOAD_DIR = Path("uploads")
AVATAR_DIR = UPLOAD_DIR / "avatars"
COURSE_DIR = UPLOAD_DIR / "courses"

# 确保目录存在
AVATAR_DIR.mkdir(parents=True, exist_ok=True)
COURSE_DIR.mkdir(parents=True, exist_ok=True)

# 允许的文件类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_DOC_TYPES = {"application/pdf", "application/msword",
                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    # current_user = Depends(get_current_user)
):
    """
    上传用户头像
    - 支持 JPG, PNG, GIF, WebP 格式
    - 最大 2MB
    """
    # 验证文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="不支持的文件类型，请上传 JPG/PNG/GIF/WebP 格式图片"
        )

    # 验证文件大小
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:  # 2MB
        raise HTTPException(
            status_code=400,
            detail="文件大小不能超过 2MB"
        )

    # 生成唯一文件名
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = AVATAR_DIR / filename

    # 保存文件
    with open(filepath, "wb") as f:
        f.write(contents)

    # 返回文件 URL
    # TODO: 更新用户头像字段
    return {
        "url": f"/api/v1/upload/files/avatars/{filename}",
        "filename": filename
    }


@router.post("/course-material")
async def upload_course_material(
    file: UploadFile = File(...),
    course_id: str = None,
    # current_user = Depends(get_current_user)
):
    """
    上传课程资料
    - 支持 PDF, Word 文档
    - 最大 10MB
    """
    # 验证文件类型
    allowed_types = ALLOWED_IMAGE_TYPES | ALLOWED_DOC_TYPES
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="不支持的文件类型"
        )

    # 验证文件大小
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="文件大小不能超过 10MB"
        )

    # 生成唯一文件名，保留原始扩展名
    ext = file.filename.split(".")[-1] if "." in file.filename else ""
    filename = f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())
    filepath = COURSE_DIR / filename

    # 保存文件
    with open(filepath, "wb") as f:
        f.write(contents)

    # TODO: 保存文件记录到数据库

    return {
        "url": f"/api/v1/upload/files/courses/{filename}",
        "filename": filename,
        "original_name": file.filename,
        "size": len(contents)
    }


@router.get("/files/{category}/{filename}")
async def get_file(category: str, filename: str):
    """
    获取上传的文件
    """
    if category == "avatars":
        filepath = AVATAR_DIR / filename
    elif category == "courses":
        filepath = COURSE_DIR / filename
    else:
        raise HTTPException(status_code=404, detail="文件不存在")

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(filepath)


@router.delete("/files/{category}/{filename}")
async def delete_file(
    category: str,
    filename: str,
    # current_user = Depends(get_current_user)
):
    """
    删除上传的文件
    """
    if category == "avatars":
        filepath = AVATAR_DIR / filename
    elif category == "courses":
        filepath = COURSE_DIR / filename
    else:
        raise HTTPException(status_code=404, detail="文件不存在")

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    os.remove(filepath)
    return {"message": "文件已删除"}
