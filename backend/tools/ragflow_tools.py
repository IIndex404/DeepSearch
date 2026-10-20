"""
    定义RAGFlow工具
    `get_assistant_list`: 获取 RAGFlow 中的所有聊天助手信息，并返回组合后的字符串。如果需要知道有哪些助手可用，请使用此工具。
    `create_ask_delete`: 创建一个新会话，提问一次，然后删除该会话，并返回答案。当需要向特定的 RAGFlow 助手提问时，使用此工具。
"""
import os
from pathlib import Path

from dotenv import load_dotenv, dotenv_values
from ragflow_sdk import RAGFlow

from api.monitor import monitor

load_dotenv(override=True)

# 创建ragflow的客户端
def _get_ragflow_client():
    config = dotenv_values(Path(__file__).resolve().parents[1] / ".env")
    return RAGFlow(
        api_key=config.get("RAGFLOW_API_KEY"),
        base_url=config.get("RAGFLOW_BASE_URL"),
    )

# 获取RAGFlow中所有的助手信息
def get_assistant_list() -> str:
    """
      获取ragflow服务中所有的聊天助手信息! 用于后续具体提问的筛选!
      返回格式: 助手名称:xxx , 描述: xx , 关联的知识库: x,x,x,x \n
              助手名称:xxx , 描述: xx , 关联的知识库: x,x,x,x \n
    """
    # 向前端推送工具使用情况
    monitor.report_tool("获取所有的聊天助手工具")
    try:
        # 获取所有的聊天助手信息
        client = _get_ragflow_client()
        chats = client.list_chats()
        # 判断chats是否为空，若不为空则遍历
        if not chats or len(chats) == 0:
            return "没有任何的聊天助手"
        # 创建拼接最终结果的遍历
        final_result = ""
        dataset_names = {dataset.id: dataset.name for dataset in client.list_datasets()}
        for chat in chats:
            # 获取聊天助手的名称
            name = chat.name
            # 获取聊天助手的描述
            description = getattr(chat, "description", "") or getattr(chat.prompt, "opener", "")
            # 获取聊天助手所关联的知识库
            datasets = getattr(chat, "datasets", None) or getattr(chat, "dataset_ids", [])
            # 获取所有关联的知识库名称
            dataset_name_list = [
                dataset.get("name", dataset_names.get(dataset.get("id"), ""))
                if isinstance(dataset, dict) else dataset_names.get(dataset, str(dataset))
                for dataset in datasets
            ]
            final_result += f"助手名称:{name},描述:{description},关联的知识库:{', '.join(dataset_name_list)} \n"
        return final_result
    except Exception as e:
        return f"获取聊天助手失败：{e}"

# 选择某个聊天助手，对用户的问题进行检索
def create_ask_delete(chat_name:str,question:str) -> str:
    """
      向指定的助手提问,并获取返回结果!
      参数 chat_name就是助手的名称,名称需要get_assistant_list查询和确认
          question是本次提问的问题
      返回结果就是提问的回答
    """
    # 向前端推送工具使用情况
    monitor.report_tool(
        tool_name="向ragflow提问工具",
        args={
            "chat_name":chat_name,
            "question":question,
        }
    )
    chat = None
    session = None
    try:
        # 根据chat_name获取指定的聊天助手
        chats = _get_ragflow_client().list_chats(name=chat_name)
        # 判断chats是否为空，若不为空则获取指定的聊天助手
        if not chats or len(chats) == 0:
            return f"获取{chat_name}助手失败"
        chat = chats[0]
        # 创建会话对象
        session = chat.create_session(name="temp session")
        # 提供会话对象提问聊天助手
        # SDK 流式响应包含增量和空结束帧；使用完整响应，避免最终答案被空帧覆盖。
        chat_result = session.ask(question=question, stream=False)
        # 创建获取最终结果的遍历
        final_result = ""
        # 对chat_result进行遍历
        for chunk in chat_result:
            final_result = chunk.content
        return final_result
    except Exception as e:
        return f"向{chat_name}提问失败：{str(e)}"
    finally:
        if chat is not None and session is not None:
            try:
                chat.delete_sessions(ids=[session.id])
            except Exception:
                pass

if __name__ == "__main__":
    # print(get_assistant_list())
    # print(create_ask_delete("刑法资讯助手", "杀人触犯什么法律"))
    print(create_ask_delete("空调安装助手", "请问空调的绝热工程怎么做"))
