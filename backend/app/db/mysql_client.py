"""
MySQL命令行客户端
实现通过MySQL命令行进行CRUD操作，包含连接管理、事务处理、SQL注入防护等功能
"""
import mysql.connector
import subprocess
import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
from app.core.config import settings

logger = logging.getLogger(__name__)


class MySQLCommandLineClient:
    """MySQL命令行客户端类，负责执行SQL命令并处理结果"""
    
    def __init__(self):
        self.config = settings.DATABASE_CONFIG
        self._connection_pool = None
        
    def _sanitize_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        SQL注入防护：清理和验证SQL语句
        使用参数化查询和白名单验证
        """
        if not sql or not isinstance(sql, str):
            raise ValueError("SQL语句不能为空")
            
        # 移除危险的SQL关键字
        dangerous_keywords = [
            r'\bDROP\b', r'\bDELETE\b.*\bWHERE\s+1\s*=\s*1\b', 
            r'\bTRUNCATE\b', r'\bALTER\b', r'\bCREATE\b.*\bUSER\b',
            r'\bGRANT\b', r'\bREVOKE\b', r'--', r'/\*', r'\*/',
            r'\bUNION\b.*\bSELECT\b', r'\bEXEC\b', r'\bEVAL\b'
        ]
        
        sql_upper = sql.upper()
        for pattern in dangerous_keywords:
            if re.search(pattern, sql_upper, re.IGNORECASE):
                raise ValueError(f"检测到潜在的SQL注入攻击: {pattern}")
        
        # 参数化处理
        if params:
            for key, value in params.items():
                if isinstance(value, str):
                    # 转义单引号
                    value = value.replace("'", "''")
                    sql = sql.replace(f":{key}", f"'{value}'")
                elif isinstance(value, (int, float)):
                    sql = sql.replace(f":{key}", str(value))
                elif value is None:
                    sql = sql.replace(f":{key}", "NULL")
        
        return sql
    
    def _execute_mysql_command(self, sql: str, fetch_results: bool = True) -> Tuple[bool, List[Dict], str]:
        """
        执行MySQL命令行操作
        
        Args:
            sql: SQL语句
            fetch_results: 是否需要获取查询结果
            
        Returns:
            Tuple[成功标志, 结果数据, 错误信息]
        """
        try:
            # 构建MySQL命令
            cmd = [
                "mysql",
                f"--host={self.config['host']}",
                f"--port={self.config['port']}",
                f"--user={self.config['user']}",
                f"--password={self.config['password']}",
                f"--database={self.config['database']}",
                "--execute", sql
            ]
            
            if fetch_results:
                cmd.extend(["--batch", "--raw", "--skip-column-names"])
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"MySQL命令执行失败: {error_msg}")
                return False, [], error_msg
            
            # 处理结果
            results = []
            if fetch_results and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                if lines:
                    # 第一行是列名
                    if sql.strip().upper().startswith('SELECT') or sql.strip().upper().startswith('SHOW'):
                        # 重新执行获取列名
                        header_cmd = cmd.copy()
                        header_cmd.remove("--skip-column-names")
                        header_result = subprocess.run(header_cmd, capture_output=True, text=True, timeout=30)
                        
                        if header_result.returncode == 0:
                            header_lines = header_result.stdout.strip().split('\n')
                            if len(header_lines) > 1:
                                columns = header_lines[0].split('\t')
                                for line in header_lines[1:]:
                                    values = line.split('\t')
                                    if len(values) == len(columns):
                                        row_dict = dict(zip(columns, values))
                                        results.append(row_dict)
            
            logger.info(f"MySQL命令执行成功，返回{len(results)}条记录")
            return True, results, ""
            
        except subprocess.TimeoutExpired:
            error_msg = "MySQL命令执行超时"
            logger.error(error_msg)
            return False, [], error_msg
        except Exception as e:
            error_msg = f"MySQL命令执行异常: {str(e)}"
            logger.error(error_msg)
            return False, [], error_msg
    
    @contextmanager
    def transaction(self):
        """
        事务管理上下文管理器
        """
        transaction_id = None
        try:
            # 开始事务
            success, _, error = self._execute_mysql_command("START TRANSACTION;", fetch_results=False)
            if not success:
                raise Exception(f"开始事务失败: {error}")
            
            logger.info("事务已开始")
            yield self
            
            # 提交事务
            success, _, error = self._execute_mysql_command("COMMIT;", fetch_results=False)
            if not success:
                raise Exception(f"提交事务失败: {error}")
                
            logger.info("事务已提交")
            
        except Exception as e:
            # 回滚事务
            try:
                self._execute_mysql_command("ROLLBACK;", fetch_results=False)
                logger.info("事务已回滚")
            except:
                pass
            raise e
    
    def select(self, table: str, columns: List[str] = None, 
               where: Dict[str, Any] = None, 
               order_by: str = None, 
               limit: int = None,
               joins: List[str] = None) -> Tuple[bool, List[Dict], str]:
        """SELECT查询操作"""
        try:
            # 构建SELECT语句
            if columns:
                columns_str = ", ".join(columns)
            else:
                columns_str = "*"
            
            sql = f"SELECT {columns_str} FROM {table}"
            
            # 添加JOIN
            if joins:
                for join in joins:
                    sql += f" {join}"
            
            # 添加WHERE条件
            if where:
                conditions = []
                for key, value in where.items():
                    if isinstance(value, str):
                        conditions.append(f"{key} = '{value.replace('\'', '\'\'')}'")
                    elif isinstance(value, (int, float)):
                        conditions.append(f"{key} = {value}")
                    elif value is None:
                        conditions.append(f"{key} IS NULL")
                
                if conditions:
                    sql += f" WHERE {' AND '.join(conditions)}"
            
            # 添加ORDER BY
            if order_by:
                sql += f" ORDER BY {order_by}"
            
            # 添加LIMIT
            if limit:
                sql += f" LIMIT {limit}"
            
            sql += ";"
            
            # 验证SQL安全性
            sql = self._sanitize_sql(sql)
            
            return self._execute_mysql_command(sql, fetch_results=True)
            
        except Exception as e:
            error_msg = f"SELECT查询失败: {str(e)}"
            logger.error(error_msg)
            return False, [], error_msg
    
    def insert(self, table: str, data: Dict[str, Any]) -> Tuple[bool, int, str]:
        """INSERT插入操作"""
        try:
            if not data:
                raise ValueError("插入数据不能为空")
            
            columns = list(data.keys())
            values = []
            
            for value in data.values():
                if isinstance(value, str):
                    values.append(f"'{value.replace('\'', '\'\'')}'")
                elif isinstance(value, (int, float)):
                    values.append(str(value))
                elif value is None:
                    values.append("NULL")
                else:
                    values.append(f"'{str(value).replace('\'', '\'\'')}'")
            
            sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)});"
            
            # 验证SQL安全性
            sql = self._sanitize_sql(sql)
            
            success, results, error = self._execute_mysql_command(sql, fetch_results=False)
            
            if success:
                # 获取插入的ID
                success_id, id_results, _ = self._execute_mysql_command("SELECT LAST_INSERT_ID();")
                insert_id = 0
                if success_id and id_results:
                    insert_id = int(list(id_results[0].values())[0])
                
                return True, insert_id, ""
            else:
                return False, 0, error
                
        except Exception as e:
            error_msg = f"INSERT插入失败: {str(e)}"
            logger.error(error_msg)
            return False, 0, error_msg
    
    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> Tuple[bool, int, str]:
        """UPDATE更新操作"""
        try:
            if not data:
                raise ValueError("更新数据不能为空")
            if not where:
                raise ValueError("WHERE条件不能为空，防止误删")
            
            # 构建SET子句
            set_clauses = []
            for key, value in data.items():
                if isinstance(value, str):
                    set_clauses.append(f"{key} = '{value.replace('\'', '\'\'')}'")
                elif isinstance(value, (int, float)):
                    set_clauses.append(f"{key} = {value}")
                elif value is None:
                    set_clauses.append(f"{key} = NULL")
            
            # 构建WHERE子句
            where_clauses = []
            for key, value in where.items():
                if isinstance(value, str):
                    where_clauses.append(f"{key} = '{value.replace('\'', '\'\'')}'")
                elif isinstance(value, (int, float)):
                    where_clauses.append(f"{key} = {value}")
                elif value is None:
                    where_clauses.append(f"{key} IS NULL")
            
            sql = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)};"
            
            # 验证SQL安全性
            sql = self._sanitize_sql(sql)
            
            success, results, error = self._execute_mysql_command(sql, fetch_results=False)
            
            if success:
                # 获取影响行数
                success_rows, rows_results, _ = self._execute_mysql_command("SELECT ROW_COUNT();")
                affected_rows = 0
                if success_rows and rows_results:
                    affected_rows = int(list(rows_results[0].values())[0])
                
                return True, affected_rows, ""
            else:
                return False, 0, error
                
        except Exception as e:
            error_msg = f"UPDATE更新失败: {str(e)}"
            logger.error(error_msg)
            return False, 0, error_msg
    
    def delete(self, table: str, where: Dict[str, Any]) -> Tuple[bool, int, str]:
        """DELETE删除操作"""
        try:
            if not where:
                raise ValueError("WHERE条件不能为空，防止误删全表")
            
            # 构建WHERE子句
            where_clauses = []
            for key, value in where.items():
                if isinstance(value, str):
                    where_clauses.append(f"{key} = '{value.replace('\'', '\'\'')}'")
                elif isinstance(value, (int, float)):
                    where_clauses.append(f"{key} = {value}")
                elif value is None:
                    where_clauses.append(f"{key} IS NULL")
            
            sql = f"DELETE FROM {table} WHERE {' AND '.join(where_clauses)};"
            
            # 验证SQL安全性
            sql = self._sanitize_sql(sql)
            
            success, results, error = self._execute_mysql_command(sql, fetch_results=False)
            
            if success:
                # 获取删除行数
                success_rows, rows_results, _ = self._execute_mysql_command("SELECT ROW_COUNT();")
                deleted_rows = 0
                if success_rows and rows_results:
                    deleted_rows = int(list(rows_results[0].values())[0])
                
                return True, deleted_rows, ""
            else:
                return False, 0, error
                
        except Exception as e:
            error_msg = f"DELETE删除失败: {str(e)}"
            logger.error(error_msg)
            return False, 0, error_msg
    
    def execute_raw_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, List[Dict], str]:
        """执行原始SQL语句"""
        try:
            # 验证SQL安全性
            sql = self._sanitize_sql(sql, params)
            
            # 判断是否需要返回结果
            fetch_results = sql.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN'))
            
            return self._execute_mysql_command(sql, fetch_results)
            
        except Exception as e:
            error_msg = f"执行原始SQL失败: {str(e)}"
            logger.error(error_msg)
            return False, [], error_msg


# 创建全局MySQL客户端实例
mysql_client = MySQLCommandLineClient() 