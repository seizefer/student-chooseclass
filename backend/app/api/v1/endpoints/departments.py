"""
院系管理API端点

@version: v1.0.1
@date: 2024-12-06
@changelog:
  v1.0.1:
    - 实现院系增删改查功能
    - 添加院系课程统计
    - 实现院系学生统计
    - 添加数据验证和权限控制
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

# 临时数据模式定义
from pydantic import BaseModel, Field

class DepartmentCreate(BaseModel):
    department_id: str = Field(..., max_length=10, description="院系编号")
    department_name: str = Field(..., max_length=100, description="院系名称")
    description: Optional[str] = Field(None, description="院系描述")

class DepartmentUpdate(BaseModel):
    department_name: Optional[str] = Field(None, max_length=100, description="院系名称")
    description: Optional[str] = Field(None, description="院系描述")

class DepartmentResponse(BaseModel):
    department_id: str
    department_name: str
    description: Optional[str] = None
    student_count: Optional[int] = 0
    course_count: Optional[int] = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@router.get("/", response_model=ResponseModel[List[DepartmentResponse]])
async def get_departments(
    include_stats: bool = Query(False, description="是否包含统计信息")
) -> ResponseModel[List[DepartmentResponse]]:
    """
    获取所有院系列表
    可选择是否包含学生和课程统计信息
    """
    try:
        if include_stats:
            # 包含统计信息的查询
            sql = """
            SELECT 
                d.*,
                COALESCE(s.student_count, 0) as student_count,
                COALESCE(c.course_count, 0) as course_count
            FROM departments d
            LEFT JOIN (
                SELECT department_id, COUNT(*) as student_count 
                FROM students 
                WHERE status = 'active'
                GROUP BY department_id
            ) s ON d.department_id = s.department_id
            LEFT JOIN (
                SELECT department_id, COUNT(*) as course_count 
                FROM courses 
                WHERE status = 'active'
                GROUP BY department_id
            ) c ON d.department_id = c.department_id
            ORDER BY d.department_id
            """
        else:
            # 基础查询
            sql = "SELECT * FROM departments ORDER BY department_id"
        
        success, results, error = mysql_client.execute_raw_sql(sql)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询院系列表失败: {error}"
            )
        
        # 转换结果
        departments = []
        for dept in results:
            try:
                departments.append(DepartmentResponse(**dept))
            except Exception as e:
                logger.warning(f"转换院系数据失败: {e}")
                continue
        
        return ResponseModel(
            code=200,
            message="获取院系列表成功",
            data=departments
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取院系列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取院系列表失败"
        )


@router.get("/{department_id}", response_model=ResponseModel[DepartmentResponse])
async def get_department(
    department_id: str,
    include_stats: bool = Query(True, description="是否包含统计信息")
) -> ResponseModel[DepartmentResponse]:
    """
    获取单个院系详情
    """
    try:
        if include_stats:
            sql = """
            SELECT 
                d.*,
                COALESCE(s.student_count, 0) as student_count,
                COALESCE(c.course_count, 0) as course_count
            FROM departments d
            LEFT JOIN (
                SELECT department_id, COUNT(*) as student_count 
                FROM students 
                WHERE status = 'active' AND department_id = :department_id
                GROUP BY department_id
            ) s ON d.department_id = s.department_id
            LEFT JOIN (
                SELECT department_id, COUNT(*) as course_count 
                FROM courses 
                WHERE status = 'active' AND department_id = :department_id
                GROUP BY department_id
            ) c ON d.department_id = c.department_id
            WHERE d.department_id = :department_id
            """
        else:
            sql = "SELECT * FROM departments WHERE department_id = :department_id"
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"department_id": department_id})
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询院系失败: {error}"
            )
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="院系不存在"
            )
        
        department = DepartmentResponse(**results[0])
        
        return ResponseModel(
            code=200,
            message="获取院系详情成功",
            data=department
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取院系详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取院系详情失败"
        )


@router.post("/", response_model=ResponseModel[DepartmentResponse])
async def create_department(
    department_data: DepartmentCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[DepartmentResponse]:
    """
    创建新院系
    需要管理员权限
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以创建院系"
            )
        
        # 检查院系ID是否已存在
        success, results, error = mysql_client.select(
            table="departments",
            where={"department_id": department_data.department_id}
        )
        
        if success and results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="院系编号已存在"
            )
        
        # 检查院系名称是否已存在
        success, results, error = mysql_client.select(
            table="departments",
            where={"department_name": department_data.department_name}
        )
        
        if success and results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="院系名称已存在"
            )
        
        # 创建院系
        department_dict = department_data.dict()
        success, insert_id, error = mysql_client.insert("departments", department_dict)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建院系失败: {error}"
            )
        
        # 返回创建的院系信息
        department_dict["student_count"] = 0
        department_dict["course_count"] = 0
        department = DepartmentResponse(**department_dict)
        
        return ResponseModel(
            code=200,
            message="创建院系成功",
            data=department
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建院系失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建院系失败"
        )


@router.put("/{department_id}", response_model=ResponseModel[DepartmentResponse])
async def update_department(
    department_id: str,
    department_data: DepartmentUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[DepartmentResponse]:
    """
    更新院系信息
    需要管理员权限
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以更新院系"
            )
        
        # 检查院系是否存在
        success, results, error = mysql_client.select(
            table="departments",
            where={"department_id": department_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="院系不存在"
            )
        
        # 如果更新院系名称，检查名称是否已存在
        if department_data.department_name:
            success, results, error = mysql_client.select(
                table="departments",
                where={"department_name": department_data.department_name}
            )
            
            if success and results and results[0]["department_id"] != department_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="院系名称已存在"
                )
        
        # 准备更新数据
        update_data = {k: v for k, v in department_data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="没有需要更新的数据"
            )
        
        # 更新院系
        success, affected_rows, error = mysql_client.update(
            table="departments",
            data=update_data,
            where={"department_id": department_id}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新院系失败: {error}"
            )
        
        # 获取更新后的院系信息（包含统计）
        sql = """
        SELECT 
            d.*,
            COALESCE(s.student_count, 0) as student_count,
            COALESCE(c.course_count, 0) as course_count
        FROM departments d
        LEFT JOIN (
            SELECT department_id, COUNT(*) as student_count 
            FROM students 
            WHERE status = 'active' AND department_id = :department_id
            GROUP BY department_id
        ) s ON d.department_id = s.department_id
        LEFT JOIN (
            SELECT department_id, COUNT(*) as course_count 
            FROM courses 
            WHERE status = 'active' AND department_id = :department_id
            GROUP BY department_id
        ) c ON d.department_id = c.department_id
        WHERE d.department_id = :department_id
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"department_id": department_id})
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取更新后的院系信息失败"
            )
        
        department = DepartmentResponse(**results[0])
        
        return ResponseModel(
            code=200,
            message="更新院系成功",
            data=department
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新院系失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新院系失败"
        )


@router.delete("/{department_id}", response_model=ResponseModel[None])
async def delete_department(
    department_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[None]:
    """
    删除院系
    需要管理员权限，只能删除没有学生和课程的院系
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以删除院系"
            )
        
        # 检查院系是否存在
        success, results, error = mysql_client.select(
            table="departments",
            where={"department_id": department_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="院系不存在"
            )
        
        # 检查是否有学生
        success, results, error = mysql_client.select(
            table="students",
            where={"department_id": department_id}
        )
        
        if success and results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该院系下还有{len(results)}名学生，无法删除"
            )
        
        # 检查是否有课程
        success, results, error = mysql_client.select(
            table="courses",
            where={"department_id": department_id}
        )
        
        if success and results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该院系下还有{len(results)}门课程，无法删除"
            )
        
        # 删除院系
        success, deleted_rows, error = mysql_client.delete(
            table="departments",
            where={"department_id": department_id}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除院系失败: {error}"
            )
        
        return ResponseModel(
            code=200,
            message="删除院系成功",
            data=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除院系失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除院系失败"
        )


@router.get("/{department_id}/students", response_model=ResponseModel[List[Dict[str, Any]]])
async def get_department_students(
    department_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[List[Dict[str, Any]]]:
    """
    获取院系下的学生列表
    需要管理员权限
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以查看院系学生列表"
            )
        
        # 检查院系是否存在
        success, results, error = mysql_client.select(
            table="departments",
            where={"department_id": department_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="院系不存在"
            )
        
        # 获取学生列表
        sql = """
        SELECT 
            student_id,
            name,
            email,
            phone,
            major,
            grade,
            status,
            created_at
        FROM students
        WHERE department_id = :department_id
        ORDER BY grade DESC, name
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"department_id": department_id})
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取学生列表失败: {error}"
            )
        
        return ResponseModel(
            code=200,
            message="获取院系学生列表成功",
            data=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取院系学生列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取院系学生列表失败"
        )


@router.get("/{department_id}/courses", response_model=ResponseModel[List[Dict[str, Any]]])
async def get_department_courses(
    department_id: str
) -> ResponseModel[List[Dict[str, Any]]]:
    """
    获取院系下的课程列表
    """
    try:
        # 检查院系是否存在
        success, results, error = mysql_client.select(
            table="departments",
            where={"department_id": department_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="院系不存在"
            )
        
        # 获取课程列表
        sql = """
        SELECT 
            course_id,
            course_name,
            credits,
            hours,
            teacher_name,
            max_students,
            current_students,
            semester,
            status,
            created_at
        FROM courses
        WHERE department_id = :department_id
        ORDER BY semester DESC, course_name
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"department_id": department_id})
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取课程列表失败: {error}"
            )
        
        return ResponseModel(
            code=200,
            message="获取院系课程列表成功",
            data=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取院系课程列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取院系课程列表失败"
        ) 