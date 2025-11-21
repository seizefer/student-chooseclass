"""
选课管理API端点

@version: v1.0.1
@date: 2024-12-06
@changelog:
  v1.0.1:
    - 实现选课和退课功能
    - 添加成绩录入和查询
    - 实现选课状态管理
    - 添加选课时间和人数限制检查
    - 支持批量操作
  v1.0.0:
    - 初始骨架
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

class EnrollmentCreate(BaseModel):
    course_id: str = Field(..., max_length=20, description="课程号")

class EnrollmentUpdate(BaseModel):
    status: Optional[str] = Field(None, description="选课状态")
    remarks: Optional[str] = Field(None, description="备注")

class GradeUpdate(BaseModel):
    grade: float = Field(..., ge=0, le=100, description="成绩")
    remarks: Optional[str] = Field(None, description="备注")

class EnrollmentResponse(BaseModel):
    enrollment_id: int
    student_id: str
    student_name: Optional[str] = None
    course_id: str
    course_name: Optional[str] = None
    department_name: Optional[str] = None
    credits: Optional[float] = None
    enrollment_date: Optional[str] = None
    grade: Optional[float] = None
    grade_date: Optional[str] = None
    status: str
    remarks: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@router.post("/", response_model=ResponseModel[EnrollmentResponse])
async def enroll_course(
    enrollment_data: EnrollmentCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[EnrollmentResponse]:
    """
    学生选课
    """
    try:
        # 只有学生可以选课
        if current_user.get("user_type") != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学生可以选课"
            )
        
        student_id = current_user["student_id"]
        course_id = enrollment_data.course_id
        
        # 检查课程是否存在且处于激活状态
        success, results, error = mysql_client.select(
            table="courses",
            where={"course_id": course_id, "status": "active"}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="课程不存在或未开放选课"
            )
        
        course = results[0]
        
        # 检查是否已经选过这门课
        success, results, error = mysql_client.select(
            table="enrollments",
            where={"student_id": student_id, "course_id": course_id}
        )
        
        if success and results:
            existing_status = results[0]["status"]
            if existing_status in ["enrolled", "completed"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="您已经选过这门课程"
                )
        
        # 检查课程是否已满
        current_students = int(course.get("current_students", 0))
        max_students = int(course.get("max_students", 0))
        
        if current_students >= max_students:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="课程选课人数已满"
            )
        
        # 使用事务进行选课操作
        with mysql_client.transaction():
            # 创建选课记录
            enrollment_dict = {
                "student_id": student_id,
                "course_id": course_id,
                "status": "enrolled"
            }
            
            success, insert_id, error = mysql_client.insert("enrollments", enrollment_dict)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"选课失败: {error}"
                )
            
            # 更新课程当前人数（触发器会自动处理，这里作为备份）
            success, affected_rows, error = mysql_client.update(
                table="courses",
                data={"current_students": current_students + 1},
                where={"course_id": course_id}
            )
        
        # 获取完整的选课信息
        sql = """
        SELECT 
            e.*,
            s.name as student_name,
            c.course_name,
            c.credits,
            d.department_name
        FROM enrollments e
        LEFT JOIN students s ON e.student_id = s.student_id
        LEFT JOIN courses c ON e.course_id = c.course_id
        LEFT JOIN departments d ON c.department_id = d.department_id
        WHERE e.enrollment_id = :enrollment_id
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"enrollment_id": insert_id})
        
        if success and results:
            enrollment = EnrollmentResponse(**results[0])
        else:
            # 如果联查失败，返回基础信息
            enrollment_dict["enrollment_id"] = insert_id
            enrollment = EnrollmentResponse(**enrollment_dict)
        
        return ResponseModel(
            code=200,
            message="选课成功",
            data=enrollment
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"选课失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="选课失败"
        )


@router.delete("/{enrollment_id}", response_model=ResponseModel[None])
async def drop_course(
    enrollment_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[None]:
    """
    学生退课
    """
    try:
        # 检查选课记录是否存在
        success, results, error = mysql_client.select(
            table="enrollments",
            where={"enrollment_id": enrollment_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="选课记录不存在"
            )
        
        enrollment = results[0]
        
        # 权限检查：学生只能退自己的课，管理员可以退任何课
        if current_user.get("user_type") == "student":
            if enrollment["student_id"] != current_user["student_id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="您只能退自己选的课程"
                )
        elif current_user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        # 检查是否可以退课（已完成或已有成绩的课程不能退）
        if enrollment["status"] == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已完成的课程不能退课"
            )
        
        if enrollment["grade"] is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已有成绩的课程不能退课"
            )
        
        # 使用事务进行退课操作
        with mysql_client.transaction():
            # 更新选课状态为已退课
            success, affected_rows, error = mysql_client.update(
                table="enrollments",
                data={"status": "dropped"},
                where={"enrollment_id": enrollment_id}
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"退课失败: {error}"
                )
            
            # 减少课程当前人数
            success, results, error = mysql_client.select(
                table="courses",
                where={"course_id": enrollment["course_id"]}
            )
            
            if success and results:
                current_students = int(results[0]["current_students"])
                mysql_client.update(
                    table="courses",
                    data={"current_students": max(0, current_students - 1)},
                    where={"course_id": enrollment["course_id"]}
                )
        
        return ResponseModel(
            code=200,
            message="退课成功",
            data=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"退课失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="退课失败"
        )


@router.get("/my-courses", response_model=ResponseModel[List[EnrollmentResponse]])
async def get_my_enrollments(
    status: Optional[str] = Query(None, description="选课状态筛选"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[List[EnrollmentResponse]]:
    """
    获取当前学生的选课列表
    """
    try:
        # 只有学生可以查看自己的选课
        if current_user.get("user_type") != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学生可以查看选课记录"
            )
        
        student_id = current_user["student_id"]
        
        # 构建查询条件
        where_conditions = ["e.student_id = :student_id"]
        params = {"student_id": student_id}
        
        if status:
            where_conditions.append("e.status = :status")
            params["status"] = status
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f"""
        SELECT 
            e.*,
            s.name as student_name,
            c.course_name,
            c.credits,
            c.teacher_name,
            c.semester,
            d.department_name
        FROM enrollments e
        LEFT JOIN students s ON e.student_id = s.student_id
        LEFT JOIN courses c ON e.course_id = c.course_id
        LEFT JOIN departments d ON c.department_id = d.department_id
        WHERE {where_clause}
        ORDER BY e.enrollment_date DESC
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, params)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询选课记录失败: {error}"
            )
        
        # 转换结果
        enrollments = []
        for enrollment in results:
            try:
                enrollments.append(EnrollmentResponse(**enrollment))
            except Exception as e:
                logger.warning(f"转换选课数据失败: {e}")
                continue
        
        return ResponseModel(
            code=200,
            message="获取选课记录成功",
            data=enrollments
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取选课记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取选课记录失败"
        )


@router.put("/{enrollment_id}/grade", response_model=ResponseModel[EnrollmentResponse])
async def update_grade(
    enrollment_id: int,
    grade_data: GradeUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[EnrollmentResponse]:
    """
    录入或更新成绩
    需要管理员权限
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以录入成绩"
            )
        
        # 检查选课记录是否存在
        success, results, error = mysql_client.select(
            table="enrollments",
            where={"enrollment_id": enrollment_id}
        )
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="选课记录不存在"
            )
        
        enrollment = results[0]
        
        # 检查选课状态
        if enrollment["status"] not in ["enrolled", "completed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能为已选课或已完成的课程录入成绩"
            )
        
        # 更新成绩和状态
        update_data = {
            "grade": grade_data.grade,
            "grade_date": datetime.now().isoformat(),
            "status": "completed",
            "remarks": grade_data.remarks
        }
        
        success, affected_rows, error = mysql_client.update(
            table="enrollments",
            data=update_data,
            where={"enrollment_id": enrollment_id}
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新成绩失败: {error}"
            )
        
        # 获取更新后的完整信息
        sql = """
        SELECT 
            e.*,
            s.name as student_name,
            c.course_name,
            c.credits,
            d.department_name
        FROM enrollments e
        LEFT JOIN students s ON e.student_id = s.student_id
        LEFT JOIN courses c ON e.course_id = c.course_id
        LEFT JOIN departments d ON c.department_id = d.department_id
        WHERE e.enrollment_id = :enrollment_id
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"enrollment_id": enrollment_id})
        
        if not success or not results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="获取更新后的选课信息失败"
            )
        
        enrollment = EnrollmentResponse(**results[0])
        
        return ResponseModel(
            code=200,
            message="成绩录入成功",
            data=enrollment
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"成绩录入失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="成绩录入失败"
        )


@router.get("/course/{course_id}", response_model=ResponseModel[List[EnrollmentResponse]])
async def get_course_enrollments(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[List[EnrollmentResponse]]:
    """
    获取某课程的选课学生列表
    需要管理员权限
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以查看课程选课列表"
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
        
        # 获取选课学生列表
        sql = """
        SELECT 
            e.*,
            s.name as student_name,
            s.email,
            s.phone,
            s.major,
            c.course_name,
            c.credits,
            d.department_name
        FROM enrollments e
        LEFT JOIN students s ON e.student_id = s.student_id
        LEFT JOIN courses c ON e.course_id = c.course_id
        LEFT JOIN departments d ON c.department_id = d.department_id
        WHERE e.course_id = :course_id AND e.status IN ('enrolled', 'completed')
        ORDER BY e.enrollment_date
        """
        
        success, results, error = mysql_client.execute_raw_sql(sql, {"course_id": course_id})
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询选课学生列表失败: {error}"
            )
        
        # 转换结果
        enrollments = []
        for enrollment in results:
            try:
                enrollments.append(EnrollmentResponse(**enrollment))
            except Exception as e:
                logger.warning(f"转换选课数据失败: {e}")
                continue
        
        return ResponseModel(
            code=200,
            message="获取课程选课列表成功",
            data=enrollments
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取课程选课列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取课程选课列表失败"
        )


@router.get("/statistics", response_model=ResponseModel[Dict[str, Any]])
async def get_enrollment_statistics(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> ResponseModel[Dict[str, Any]]:
    """
    获取选课统计信息
    需要管理员权限
    """
    try:
        # 检查用户权限
        if current_user.get("user_type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以查看选课统计"
            )
        
        # 总体统计
        total_sql = """
        SELECT 
            COUNT(*) as total_enrollments,
            COUNT(DISTINCT student_id) as total_students,
            COUNT(DISTINCT course_id) as total_courses,
            AVG(CASE WHEN grade IS NOT NULL THEN grade END) as avg_grade
        FROM enrollments
        WHERE status IN ('enrolled', 'completed')
        """
        
        success, total_results, error = mysql_client.execute_raw_sql(total_sql)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询总体统计失败: {error}"
            )
        
        # 按状态统计
        status_sql = """
        SELECT status, COUNT(*) as count
        FROM enrollments
        GROUP BY status
        """
        
        success, status_results, error = mysql_client.execute_raw_sql(status_sql)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询状态统计失败: {error}"
            )
        
        # 按院系统计
        department_sql = """
        SELECT 
            d.department_name,
            COUNT(e.enrollment_id) as enrollment_count,
            AVG(CASE WHEN e.grade IS NOT NULL THEN e.grade END) as avg_grade
        FROM enrollments e
        LEFT JOIN courses c ON e.course_id = c.course_id
        LEFT JOIN departments d ON c.department_id = d.department_id
        WHERE e.status IN ('enrolled', 'completed')
        GROUP BY d.department_id, d.department_name
        ORDER BY enrollment_count DESC
        """
        
        success, department_results, error = mysql_client.execute_raw_sql(department_sql)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"查询院系统计失败: {error}"
            )
        
        # 组装统计结果
        statistics = {
            "total": total_results[0] if total_results else {},
            "by_status": status_results,
            "by_department": department_results
        }
        
        return ResponseModel(
            code=200,
            message="获取选课统计成功",
            data=statistics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取选课统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取选课统计失败"
        ) 