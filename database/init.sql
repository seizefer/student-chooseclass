-- 在线大学生选课系统数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS student_course_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE student_course_system;

-- 1. 院系信息表
CREATE TABLE departments (
    department_id VARCHAR(10) PRIMARY KEY COMMENT '院系编号',
    department_name VARCHAR(100) NOT NULL COMMENT '院系名称',
    description TEXT COMMENT '院系描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '院系信息表';

-- 2. 学生信息表
CREATE TABLE students (
    student_id VARCHAR(20) PRIMARY KEY COMMENT '学号',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    birth_date DATE COMMENT '出生日期',
    id_number VARCHAR(18) UNIQUE NOT NULL COMMENT '身份证号',
    address VARCHAR(200) COMMENT '地址',
    email VARCHAR(100) UNIQUE COMMENT '邮箱',
    phone VARCHAR(20) COMMENT '电话号码',
    department_id VARCHAR(10) COMMENT '所属院系',
    major VARCHAR(100) COMMENT '专业',
    grade YEAR COMMENT '年级',
    balance DECIMAL(10,2) DEFAULT 0.00 COMMENT '账户余额',
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active' COMMENT '状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL,
    INDEX idx_department (department_id),
    INDEX idx_name (name),
    INDEX idx_id_number (id_number)
) COMMENT '学生信息表';

-- 3. 管理员表
CREATE TABLE administrators (
    admin_id VARCHAR(20) PRIMARY KEY COMMENT '管理员ID',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    role ENUM('super_admin', 'admin', 'teacher') DEFAULT 'admin' COMMENT '角色',
    department_id VARCHAR(10) COMMENT '所属院系',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL
) COMMENT '管理员表';

-- 4. 课程信息表
CREATE TABLE courses (
    course_id VARCHAR(20) PRIMARY KEY COMMENT '课程号',
    course_name VARCHAR(100) NOT NULL COMMENT '课程名称',
    department_id VARCHAR(10) NOT NULL COMMENT '开课院系',
    credits DECIMAL(3,1) NOT NULL COMMENT '学分',
    hours INT NOT NULL COMMENT '学时',
    description TEXT COMMENT '课程描述',
    teacher_name VARCHAR(50) COMMENT '授课教师',
    max_students INT DEFAULT 100 COMMENT '最大选课人数',
    current_students INT DEFAULT 0 COMMENT '当前选课人数',
    semester VARCHAR(20) COMMENT '开课学期',
    schedule VARCHAR(200) COMMENT '上课时间安排',
    status ENUM('active', 'inactive', 'completed') DEFAULT 'active' COMMENT '课程状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    INDEX idx_department (department_id),
    INDEX idx_course_name (course_name),
    INDEX idx_semester (semester)
) COMMENT '课程信息表';

-- 5. 选课记录表
CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '选课记录ID',
    student_id VARCHAR(20) NOT NULL COMMENT '学号',
    course_id VARCHAR(20) NOT NULL COMMENT '课程号',
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '选课时间',
    grade DECIMAL(5,2) COMMENT '成绩',
    grade_date TIMESTAMP NULL COMMENT '成绩录入时间',
    status ENUM('enrolled', 'completed', 'dropped', 'failed') DEFAULT 'enrolled' COMMENT '选课状态',
    remarks TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
    UNIQUE KEY uk_student_course (student_id, course_id),
    INDEX idx_student (student_id),
    INDEX idx_course (course_id),
    INDEX idx_enrollment_date (enrollment_date)
) COMMENT '选课记录表';

-- 6. 好友关系表
CREATE TABLE friendships (
    friendship_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '好友关系ID',
    requester_id VARCHAR(20) NOT NULL COMMENT '发起者学号',
    addressee_id VARCHAR(20) NOT NULL COMMENT '接收者学号',
    status ENUM('pending', 'accepted', 'declined', 'blocked') DEFAULT 'pending' COMMENT '好友状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '申请时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '状态更新时间',
    FOREIGN KEY (requester_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (addressee_id) REFERENCES students(student_id) ON DELETE CASCADE,
    UNIQUE KEY uk_friendship (requester_id, addressee_id),
    INDEX idx_requester (requester_id),
    INDEX idx_addressee (addressee_id),
    INDEX idx_status (status)
) COMMENT '好友关系表';

-- 7. 转账记录表
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '转账记录ID',
    from_student_id VARCHAR(20) NOT NULL COMMENT '转出学号',
    to_student_id VARCHAR(20) NOT NULL COMMENT '转入学号',
    amount DECIMAL(10,2) NOT NULL COMMENT '转账金额',
    transaction_type ENUM('transfer', 'recharge', 'withdraw') DEFAULT 'transfer' COMMENT '交易类型',
    description VARCHAR(200) COMMENT '转账说明',
    status ENUM('pending', 'completed', 'failed', 'cancelled') DEFAULT 'completed' COMMENT '交易状态',
    risk_level ENUM('low', 'medium', 'high') DEFAULT 'low' COMMENT '风险等级',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '转账时间',
    FOREIGN KEY (from_student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (to_student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    INDEX idx_from_student (from_student_id),
    INDEX idx_to_student (to_student_id),
    INDEX idx_transaction_date (created_at),
    INDEX idx_amount (amount),
    INDEX idx_risk_level (risk_level)
) COMMENT '转账记录表';

-- 8. 消息记录表
CREATE TABLE messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
    from_student_id VARCHAR(20) NOT NULL COMMENT '发送者学号',
    to_student_id VARCHAR(20) NOT NULL COMMENT '接收者学号',
    content TEXT NOT NULL COMMENT '消息内容',
    message_type ENUM('text', 'image', 'file', 'system') DEFAULT 'text' COMMENT '消息类型',
    is_read BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    read_at TIMESTAMP NULL COMMENT '阅读时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    FOREIGN KEY (from_student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (to_student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    INDEX idx_from_student (from_student_id),
    INDEX idx_to_student (to_student_id),
    INDEX idx_created_at (created_at),
    INDEX idx_is_read (is_read)
) COMMENT '消息记录表';

-- 9. 登录记录表
CREATE TABLE login_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    user_id VARCHAR(20) NOT NULL COMMENT '用户ID',
    user_type ENUM('student', 'admin') NOT NULL COMMENT '用户类型',
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    logout_time TIMESTAMP NULL COMMENT '登出时间',
    ip_address VARCHAR(45) COMMENT 'IP地址',
    user_agent TEXT COMMENT '用户代理',
    login_status ENUM('success', 'failed') DEFAULT 'success' COMMENT '登录状态',
    device_info VARCHAR(200) COMMENT '设备信息',
    INDEX idx_user_id (user_id),
    INDEX idx_login_time (login_time),
    INDEX idx_user_type (user_type)
) COMMENT '登录记录表';

-- 10. 系统配置表
CREATE TABLE system_config (
    config_id INT AUTO_INCREMENT PRIMARY KEY COMMENT '配置ID',
    config_key VARCHAR(100) UNIQUE NOT NULL COMMENT '配置键',
    config_value TEXT COMMENT '配置值',
    description VARCHAR(200) COMMENT '配置描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '系统配置表';

-- 插入初始数据

-- 院系数据
INSERT INTO departments (department_id, department_name, description) VALUES 
('CS', '计算机科学与技术学院', '计算机科学与技术相关专业'),
('MATH', '数学学院', '数学及应用数学相关专业'),
('ENG', '外国语学院', '外语相关专业'),
('BUS', '商学院', '工商管理相关专业'),
('ART', '艺术学院', '艺术设计相关专业');

-- 管理员数据
INSERT INTO administrators (admin_id, password_hash, name, email, role, department_id) VALUES 
('admin001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeykgyKdM4VbzZK5O', '系统管理员', 'admin@university.edu', 'super_admin', NULL),
('teacher001', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeykgyKdM4VbzZK5O', '张教授', 'zhang@cs.edu', 'teacher', 'CS');

-- 系统配置数据
INSERT INTO system_config (config_key, config_value, description) VALUES 
('max_friends', '100', '每个学生最大好友数量'),
('max_transaction_amount', '1000.00', '单次转账最大金额'),
('daily_transaction_limit', '5000.00', '每日转账限额'),
('friend_recommendation_count', '10', '好友推荐数量'),
('high_risk_amount', '500.00', '高风险转账金额阈值');

-- 创建触发器：选课时更新课程当前人数
DELIMITER //
CREATE TRIGGER tr_enrollment_insert 
AFTER INSERT ON enrollments 
FOR EACH ROW 
BEGIN
    UPDATE courses 
    SET current_students = current_students + 1 
    WHERE course_id = NEW.course_id;
END//

CREATE TRIGGER tr_enrollment_delete 
AFTER DELETE ON enrollments 
FOR EACH ROW 
BEGIN
    UPDATE courses 
    SET current_students = current_students - 1 
    WHERE course_id = OLD.course_id;
END//
DELIMITER ;

-- 创建视图：学生课程成绩视图
CREATE VIEW student_grades AS
SELECT 
    s.student_id,
    s.name as student_name,
    c.course_id,
    c.course_name,
    c.credits,
    e.grade,
    e.status,
    e.enrollment_date,
    e.grade_date
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id;

-- 创建视图：好友关系视图
CREATE VIEW friend_relationships AS
SELECT 
    f.friendship_id,
    s1.student_id as user_id,
    s1.name as user_name,
    s2.student_id as friend_id,
    s2.name as friend_name,
    f.status,
    f.created_at as friendship_date
FROM friendships f
JOIN students s1 ON f.requester_id = s1.student_id
JOIN students s2 ON f.addressee_id = s2.student_id
WHERE f.status = 'accepted'
UNION
SELECT 
    f.friendship_id,
    s2.student_id as user_id,
    s2.name as user_name,
    s1.student_id as friend_id,
    s1.name as friend_name,
    f.status,
    f.created_at as friendship_date
FROM friendships f
JOIN students s1 ON f.requester_id = s1.student_id
JOIN students s2 ON f.addressee_id = s2.student_id
WHERE f.status = 'accepted';

-- 创建存储过程：好友推荐
DELIMITER //
CREATE PROCEDURE RecommendFriends(IN user_id VARCHAR(20))
BEGIN
    -- 基于共同好友和相同专业推荐好友
    SELECT DISTINCT 
        s.student_id,
        s.name,
        s.major,
        s.department_id,
        COUNT(DISTINCT mutual.friend_id) as mutual_friends_count
    FROM students s
    LEFT JOIN (
        -- 获取用户的好友的好友（排除用户本人和已经是好友的）
        SELECT f2.friend_id
        FROM friend_relationships f1
        JOIN friend_relationships f2 ON f1.friend_id = f2.user_id
        WHERE f1.user_id = user_id 
        AND f2.friend_id != user_id
        AND f2.friend_id NOT IN (
            SELECT friend_id FROM friend_relationships WHERE user_id = user_id
        )
    ) mutual ON s.student_id = mutual.friend_id
    WHERE s.student_id != user_id
    AND s.student_id NOT IN (
        SELECT friend_id FROM friend_relationships WHERE user_id = user_id
    )
    AND s.student_id NOT IN (
        SELECT addressee_id FROM friendships WHERE requester_id = user_id AND status IN ('pending', 'accepted')
        UNION
        SELECT requester_id FROM friendships WHERE addressee_id = user_id AND status IN ('pending', 'accepted')
    )
    GROUP BY s.student_id, s.name, s.major, s.department_id
    ORDER BY 
        mutual_friends_count DESC,
        CASE WHEN s.major = (SELECT major FROM students WHERE student_id = user_id) THEN 1 ELSE 0 END DESC,
        CASE WHEN s.department_id = (SELECT department_id FROM students WHERE student_id = user_id) THEN 1 ELSE 0 END DESC
    LIMIT 10;
END//
DELIMITER ; 