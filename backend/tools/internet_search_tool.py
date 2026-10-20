"""
    定义网络搜索的工具
"""
import os
from typing import Literal

from dotenv import load_dotenv
from tavily import TavilyClient

from api.monitor import monitor
from utils.logger_utils import logger

load_dotenv(override=True)

# 创建tavily客户端
_tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"),)

# 创建网络搜索工具所对应的函数
def internet_search(
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news", "finance"] = "general",
        include_raw_content: bool = False,
):
    """
    根据问题进行网络查询，当需要获取外部互联网的公开信息、最新新闻或特定主题数据时使用此工具。
    :param query: 查询的问题
    :param max_results: 查询的最大结果数量
    :param topic: 查询的主题类型
    :param include_raw_content: 是否精简返回
    :return: 网络搜索的结果
    """

    # 记录日志信息
    logger.info(f"调用工具internet_search，参数为query: {query}，max_results: {max_results}")

    # 向前端推送工具使用情况
    monitor.report_tool(
        tool_name="网络搜索工具",
        args={
            "query": query,
            "max_results": max_results,
            "topic": topic,
            "include_raw_content": include_raw_content,
        }
    )

    # 调用tavily进行网络搜索
    return _tavily_client.search(
        query=query,
        max_results=max_results,
        topic=topic,
        include_raw_content=include_raw_content,
    )
