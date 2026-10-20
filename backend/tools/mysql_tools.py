"""
    定义数据库子智能体的工具
    `list_sql_tables`: 列出配置的 MySQL 数据库中所有可用的表，这是了解数据库结构的第一步。
    `get_table_data`: 读取指定 MySQL 表的前 100 行数据，用于快速预览数据内容。
    `execute_sql_query`: 执行自定义 SQL 查询，当需要复杂的筛选、联接或聚合时使用此工具。
"""
import os
from pathlib import Path
from unittest import result

from dotenv import load_dotenv, dotenv_values
from mysql.connector import connect
from pandas.core.interchange import column

from api.monitor import monitor

load_dotenv(override=True)

# 读取.env文件中关于MySQL的配置信息
def get_db_config():
    config_values = dotenv_values(Path(__file__).resolve().parents[1] / ".env")
    config = {
        "host": config_values.get("MYSQL_HOST", "localhost"),
        "port": int(config_values.get("MYSQL_PORT", "3306")),
        "user": config_values.get("MYSQL_USER"),
        "password": config_values.get("MYSQL_PASSWORD"),
        "database": config_values.get("MYSQL_DATABASE"),
        "charset": config_values.get("MYSQL_CHARSET", "utf8mb4"),
        "autocommit": True,
        "connection_timeout": 5,
    }
    # 排除config中值为None的键值对
    config = {k: v for k, v in config.items() if v is not None}
    # 设置连接数据库必须使用的键
    required_keys = ["user", "password", "database"]
    # 获取config中缺失的关键的键
    missing_keys = [k for k in required_keys if k not in config]
    # 判断missing_keys是否为空
    if missing_keys:
        raise ValueError(f"连接数据库配置缺失：{', '.join(missing_keys)}")
    return config

# 获取数据库中所有可用的表
def list_sql_tables():
    """
    获取数据库中所有可用的表
    """
    # 向前端推送工具使用情况
    monitor.report_tool("表名搜索工具")
    try:
        with connect(**get_db_config()) as conn:
            with conn.cursor() as cursor:
                sql = "show tables"
                # 执行sql
                cursor.execute(sql)
                # 获取查询的结果
                result = cursor.fetchall()
                # 判断是否查询到数据
                if not result or len(result) == 0:
                    return "没有查询到可用的表"
                # 将表名存储到列表中
                table_list = [item[0] for item in result]
                return ", ".join(table_list)
    except Exception as e:
        return f"创建连接失败，{e}"

# 查询指定表中的前100条数据
def get_table_data(table_name: str):
    """
    查询指定表名的数据,参数就是表名! 为了让助手理解表的结构!
    我们返回的格式参照表格格式 如下:
    id,name,age
    1,二狗子,18
    2,驴蛋蛋,19
    """
    # 向前端推送工具使用情况
    monitor.report_tool(
        tool_name="搜索指定表名的数据工具",
        args={
            "table_name": table_name,
        }
    )
    try:
        with connect(**get_db_config()) as conn:
            with conn.cursor() as cursor:
                sql = f"select * from {table_name} limit 100"
                # 执行sql
                cursor.execute(sql)
                # 获取查询的表的字段结果
                description = cursor.description
                # 将字段名存储到列表中
                column_name_list = [item[0] for item in description]
                # 将所有的字段拼接为字符串
                column_name_str = ", ".join(column_name_list)
                # 获取查询的结果
                result = cursor.fetchall()
                # 将查询的每条数据的字段拼接为字符串
                data_list = [", ".join(map(str, item)) for item in result]
                # 将查询的每条数据中间使用换行进行拼接
                data_list_str = "\n".join(data_list)
                return column_name_str + "\n" + data_list_str
    except Exception as e:
        return f"数据库连接失败，{e}"

# 执行自定义的SQL语句
def execute_sql_query(sql: str):
    """
    执行自定义SQL查询
    """
    # 向前端推送工具使用情况
    monitor.report_tool(
        tool_name="执行自定义SQL查询工具",
        args={
            "sql": sql,
        }
    )
    try:
        with connect(**get_db_config()) as conn:
            with conn.cursor() as cursor:
                # 执行sql
                cursor.execute(sql)
                # 获取查询的表的字段结果
                description = cursor.description
                # 将字段名存储到列表中
                column_name_list = [item[0] for item in description]
                # 将所有的字段拼接为字符串
                column_name_str = ", ".join(column_name_list)
                # 获取查询的结果
                result = cursor.fetchall()
                # 将查询的每条数据的字段拼接为字符串
                data_list = [", ".join(map(str, item)) for item in result]
                # 将查询的每条数据中间使用换行进行拼接
                data_list_str = "\n".join(data_list)
                return column_name_str + "\n" + data_list_str
    except Exception as e:
        return f"数据库连接失败，{e}"


if __name__ == "__main__":
    # print(list_sql_tables())
    # print(get_table_data("drugs"))
    print(execute_sql_query("select * from inventory"))
