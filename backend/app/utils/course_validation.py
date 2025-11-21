"""
课程验证工具
- 时间冲突检测
- 先修课程验证
"""
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime


# ==================== 时间冲突检测 ====================

def parse_schedule(schedule: str) -> List[Tuple[int, int, int]]:
    """
    解析课程时间表
    输入格式: "周一 8:00-9:40" 或 "周一三五 10:00-11:40"
    返回: [(weekday, start_minutes, end_minutes), ...]
    """
    if not schedule:
        return []

    # 星期映射
    weekday_map = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '日': 7,
        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7
    }

    results = []

    # 匹配时间段
    time_pattern = r'(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})'
    time_match = re.search(time_pattern, schedule)

    if not time_match:
        return []

    start_hour, start_min = int(time_match.group(1)), int(time_match.group(2))
    end_hour, end_min = int(time_match.group(3)), int(time_match.group(4))
    start_minutes = start_hour * 60 + start_min
    end_minutes = end_hour * 60 + end_min

    # 提取星期
    for char in schedule:
        if char in weekday_map:
            results.append((weekday_map[char], start_minutes, end_minutes))

    return results


def check_time_conflict(schedule1: str, schedule2: str) -> bool:
    """
    检查两个课程时间是否冲突
    返回 True 表示有冲突
    """
    times1 = parse_schedule(schedule1)
    times2 = parse_schedule(schedule2)

    for weekday1, start1, end1 in times1:
        for weekday2, start2, end2 in times2:
            # 同一天
            if weekday1 == weekday2:
                # 时间重叠
                if not (end1 <= start2 or end2 <= start1):
                    return True

    return False


def check_enrollment_conflicts(
    new_course_schedule: str,
    enrolled_courses: List[Dict]
) -> List[Dict]:
    """
    检查新选课程与已选课程的时间冲突
    返回冲突的课程列表
    """
    conflicts = []

    for course in enrolled_courses:
        if check_time_conflict(new_course_schedule, course.get('schedule', '')):
            conflicts.append({
                'course_id': course['course_id'],
                'name': course['name'],
                'schedule': course['schedule']
            })

    return conflicts


# ==================== 先修课程验证 ====================

def check_prerequisites(
    course_prerequisites: List[str],
    completed_courses: List[str]
) -> Tuple[bool, List[str]]:
    """
    检查是否满足先修课程要求
    返回: (是否满足, 缺少的先修课程列表)
    """
    if not course_prerequisites:
        return True, []

    missing = []
    for prereq in course_prerequisites:
        if prereq not in completed_courses:
            missing.append(prereq)

    return len(missing) == 0, missing


def get_prerequisite_tree(
    course_id: str,
    all_courses: Dict[str, Dict]
) -> Dict:
    """
    获取课程的先修课程树
    用于可视化展示先修关系
    """
    if course_id not in all_courses:
        return {}

    course = all_courses[course_id]
    prerequisites = course.get('prerequisites', [])

    tree = {
        'course_id': course_id,
        'name': course.get('name', ''),
        'prerequisites': []
    }

    for prereq_id in prerequisites:
        subtree = get_prerequisite_tree(prereq_id, all_courses)
        if subtree:
            tree['prerequisites'].append(subtree)

    return tree


# ==================== 选课容量验证 ====================

def check_capacity(current_enrollment: int, capacity: int) -> bool:
    """
    检查课程是否还有剩余容量
    返回 True 表示可以选课
    """
    return current_enrollment < capacity


def get_available_seats(current_enrollment: int, capacity: int) -> int:
    """
    获取剩余座位数
    """
    return max(0, capacity - current_enrollment)


# ==================== 综合验证 ====================

def validate_enrollment(
    student_id: str,
    course: Dict,
    enrolled_courses: List[Dict],
    completed_courses: List[str]
) -> Tuple[bool, str]:
    """
    综合验证是否可以选课
    返回: (是否可以选课, 原因)
    """
    # 1. 检查容量
    if not check_capacity(course.get('current_enrollment', 0), course.get('capacity', 0)):
        return False, "课程容量已满"

    # 2. 检查时间冲突
    conflicts = check_enrollment_conflicts(course.get('schedule', ''), enrolled_courses)
    if conflicts:
        conflict_names = ', '.join([c['name'] for c in conflicts])
        return False, f"与已选课程时间冲突: {conflict_names}"

    # 3. 检查先修课程
    satisfied, missing = check_prerequisites(
        course.get('prerequisites', []),
        completed_courses
    )
    if not satisfied:
        missing_names = ', '.join(missing)
        return False, f"缺少先修课程: {missing_names}"

    # 4. 检查是否重复选课
    for enrolled in enrolled_courses:
        if enrolled['course_id'] == course['course_id']:
            return False, "已经选修该课程"

    return True, "可以选课"


# ==================== 示例用法 ====================

if __name__ == "__main__":
    # 测试时间解析
    schedule = "周一三五 8:00-9:40"
    print(f"解析 '{schedule}': {parse_schedule(schedule)}")

    # 测试冲突检测
    s1 = "周一 8:00-9:40"
    s2 = "周一 9:00-10:40"
    s3 = "周二 8:00-9:40"

    print(f"\n'{s1}' 与 '{s2}' 冲突: {check_time_conflict(s1, s2)}")
    print(f"'{s1}' 与 '{s3}' 冲突: {check_time_conflict(s1, s3)}")
