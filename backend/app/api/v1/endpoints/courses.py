"""
课程管理API端点

@version: v1.0.1
@date: 2024-12-06
@changelog:
  v1.0.1:
    - 实现课程增删改查功能
    - 添加课程搜索和分页
    - 实现课程状态管理
    - 添加选课人数统计
  v1.0.0:
    - 初始骨架
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
import logging

from app.core.config import settings
from app.db.mysql_client import mysql_client
from app.schemas.common import ResponseModel, PaginationResponse
from app.api.v1.endpoints.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


# 临时数据模式定义（后续应移动到schemas/courses.py）
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CourseCreate(BaseModel):
    course_id: str = Field(..., max_length=20, description="课程号")
    course_name: str = Field(..., max_length=100, description="课程名称")
    department_id: str = Field(..., max_length=10, description="开课院系")
    credits: float = Field(..., ge=0, le=10, description="学分")
    hours: int = Field(..., ge=1, description="学时")
    description: Optional[str] = Field(None, description="课程描述")
    teacher_name: Optional[str] = Field(None, max_length=50, description="授课教师")
    max_students: int = Field(100, ge=1, description="最大选课人数")
    semester: Optional[str] = Field(None, max_length=20, description="开课学期")
    schedule: Optional[str] = Field(None, max_length=200, description="上课时间安排")

class CourseUpdate(BaseModel):
    course_name: Optional[str] = Field(None, max_length=100, description="课程名称")
    department_id: Optional[str] = Field(None, max_length=10, description="开课院系")
    credits: Optional[float] = Field(None, ge=0, le=10, description="学分")
    hours: Optional[int] = Field(None, ge=1, description="学时")
    description: Optional[str] = Field(None, description="课程描述")
    teacher_name: Optional[str] = Field(None, max_length=50, description="授课教师")
    max_students: Optional[int] = Field(None, ge=1, description="最大选课人数")
    semester: Optional[str] = Field(None, max_length=20, description="开课学期")
    schedule: Optional[str] = Field(None, max_length=200, description="上课时间安排")
    status: Optional[str] = Field(None, description="课程状态")

class CourseResponse(BaseModel):
    course_id: str
    course_name: str
    department_id: str
    department_name: Optional[str] = None
    credits: float
    hours: int
    description: Optional[str] = None
    teacher_name: Optional[str] = None
    max_students: int
    current_students: int
    semester: Optional[str] = None
    schedule: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@router.get("/", response_model=ResponseModel[PaginationResponse[CourseResponse]])
async def get_courses(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    department_id: Optional[str] = Query(None, description="院系ID"),
    semester: Optional[str] = Query(None, description="学期"),
    status: Optional[str] = Query(None, description="课程状态"),
    search: Optional[str] = Query(None, description="搜索关键词")
) -> ResponseModel[PaginationResponse[CourseResponse]]:
    """
    获取课程列表（分页）
    支持按院系、学期、状态筛选，以及关键词搜索
    """
    try:
        # 构建WHERE条件
        where_conditions = []
        params = {}
        
        if department_id:
            where_conditions.append("courses.department_id = :department_id")
            params["department_id"] = department_id
        if semester:
            where_conditions.append("courses.semester = :semester")
            params["semester"] = semester
        if status:
            where_conditions.append("courses.status = :status")
            params["status"] = status
        if search:
            where_conditions.append("(courses.course_name LIKE :search OR courses.teacher_name LIKE :search)")
            params["search"] = f"%{search}%"
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 获取总数
        count_sql = f"""
        SELECT COUNT(*) as total 
        FROM courses 
        WHERE {where_clause}
        """
        
        success, count_results, error = mysql_client.execute_raw_sql(count_sql, params)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询课程总数失败: {error}"
            )
        
        total = int(count_results[0]["total"]) if count_results else 0
        
        # 获取分页数据
        data_sql = f"""
        SELECT 
            courses.*,
            d.department_name
        FROM courses 
        LEFT JOIN departments d ON courses.department_id = d.department_id
        WHERE {where_clause}
        ORDER BY courses.created_at DESC 
        LIMIT {page_size} OFFSET {offset}
        """
        
        success, results, error = mysql_client.execute_raw_sql(data_sql, params)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询课程列表失败: {error}"
            )
        
        # 转换结果
        courses = []
        for course in results:
            try:
                courses.append(CourseResponse(**course))
            except Exception as e:
                logger.warning(f"转换课程数据失败: {e}")
                continue
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        return ResponseModel(
            code=200,
            message="获取课程列表成功",
            data=PaginationResponse(
                items=courses,
                total=total,
                page=page,
                page_size=page_size,
                total_pages=total_pages
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取课程列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取课程列表失败"
        )


@router.get("/{course_id}", response_model=ResponseModel[CourseResponse])
async def get_course(course_id: str) -> ResponseModel[CourseResponse]:
    """
    获取单个课程详情
    """
    try:
        sql = """
        SELECT courses.*, d.department_name
        FROM courses 
        LEFT JOIN departments d ON courses.department_id = d.department_id
        WHERE courses.course_id = :course_id
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"course_id": course_id})
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询课程失败: {error}"
            )
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="课程不存在"
            )
        
        course = CourseResponse(**results[0])
        
        return ResponseModel(
            code=200,
            message="获取课程详情成功",
            data=course
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取课程详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取课程详情失败"
        )


@router.post("/", response_model=ResponseModel[CourseResponse])
async def create_course(
    course_data: CourseCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[CourseResponse]:
    """
    创建新课程
    需要管理员权限
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以创建课程"
            )
        
        # 检查课程号是否已存在
        success, results, error = mysql_client.select(
            table="courses",
            where={"course_id": course_data.course_id}
        )
        
        if success and results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="课程号已存在"
            )
        
        # 检查院系是否存在
        success, results, error = mysql_client.select(
            table="departments",
            where={"department_id": course_data.department_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="院系不存在"
            )
        
        # 创建课程数据
        course_dict = course_data.dict()
        course_dict["current_students"] = 0
        course_dict["status"] = "active"
        
        success, insert_id, error = mysql_client.insert("courses", course_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建课程失败: {error}"
            )
        
        # 获取创建的课程信息
        sql = """
        SELECT courses.*, d.department_name
        FROM courses 
        LEFT JOIN departments d ON courses.department_id = d.department_id
        WHERE courses.course_id = :course_id
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"course_id": course_data.course_id})
        
        if success and results:
            course = CourseResponse(**results[0])
        else:
            course = CourseResponse(**course_dict)
        
        return ResponseModel(
            code=200,
            message="创建课程成功",
            data=course
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建课程失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建课程失败"
        )


@router.put("/{course_id}", response_model=ResponseModel[CourseResponse])
async def update_course(
    course_id: str,
    course_data: CourseUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[CourseResponse]:
    """
    更新课程信息
    需要管理员权限
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以更新课程"
            )
        
        # 检查课程是否存在
        success, results, error = mysql_client.select(
            table="courses",
            where={"course_id": course_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="课程不存在"
            )
        
        # 准备更新数据
        update_data = {k: v for k, v in course_data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有需要更新的数据"
            )
        
        # 更新课程
        success, affected_rows, error = mysql_client.update(
            table="courses",
            data=update_data,
            where={"course_id": course_id}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新课程失败: {error}"
            )
        
        # 获取更新后的课程信息
        sql = """
        SELECT courses.*, d.department_name
        FROM courses 
        LEFT JOIN departments d ON courses.department_id = d.department_id
        WHERE courses.course_id = :course_id
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"course_id": course_id})
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取更新后的课程信息失败"
            )
        
        course = CourseResponse(**results[0])
        
        return ResponseModel(
            code=200,
            message="更新课程成功",
            data=course
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新课程失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新课程失败"
        )


@router.delete("/{course_id}", response_model=ResponseModel[None])
async def delete_course(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[None]:
    """
    删除课程
    需要管理员权限，只能删除没有学生选课的课程
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以删除课程"
            )
        
        # 检查课程是否存在
        success, results, error = mysql_client.select(
            table="courses",
            where={"course_id": course_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="课程不存在"
            )
        
        # 检查是否有学生选课
        success, results, error = mysql_client.select(
            table="enrollments",
            where={"course_id": course_id}
        )
        
        if success and results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该课程已有学生选课，无法删除"
            )
        
        # 删除课程
        success, deleted_rows, error = mysql_client.delete(
            table="courses",
            where={"course_id": course_id}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除课程失败: {error}"
            )
        
        return ResponseModel(
            code=200,
            message="删除课程成功",
            data=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除课程失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除课程失败"
        )


@router.get("/{course_id}/enrollments", response_model=ResponseModel[List[Dict[str, Any]]])
async def get_course_enrollments(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[List[Dict[str, Any]]]:
    """
    获取课程的选课学生列表
    需要管理员权限
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以查看选课学生列表"
            )
        
        # 检查课程是否存在
        success, results, error = mysql_client.select(
            table="courses",
            where={"course_id": course_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="课程不存在"
            )
        
        # 获取选课学生信息
        sql = f"""
        SELECT 
            e.*,
            s.name as student_name,
            s.email as student_email,
            s.phone as student_phone,
            s.major as student_major
        FROM enrollments e
        LEFT JOIN students s ON e.student_id = s.student_id
        WHERE e.course_id = '{course_id}'
        ORDER BY e.enrollment_date DESC
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取选课学生列表失败: {error}"
            )
        
        return ResponseModel(
            code=200,
            message="获取选课学生列表成功",
            data=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取选课学生列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取选课学生列表失败"
        ) 