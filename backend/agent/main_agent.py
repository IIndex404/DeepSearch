"""
    创建主智能体
"""
import asyncio
import shutil
from pathlib import Path

from deepagents import create_deep_agent
from langchain_core.messages import AIMessage

from agent.llm import create_llm, model_error_message
from agent.load_prompt import main_agent_config
from agent.sub_agents.db_sub_agent import db_sub_agent
from agent.sub_agents.internet_sub_agent import internet_sub_agent
from agent.sub_agents.rag_sub_agent import rag_sub_agent
from api.context import set_session_context, set_thread_context, reset_session_context
from api.monitor import monitor
from tools.upload_file_read_tool import read_file_content, generate_markdown, convert_md_to_pdf
from utils.logger_utils import logger

def build_main_agent():
    return create_deep_agent(
        model=create_llm(),
        system_prompt=main_agent_config["system_prompt"],
        tools=[read_file_content, generate_markdown, convert_md_to_pdf],
        subagents=[internet_sub_agent, db_sub_agent, rag_sub_agent]
    )

# 获取项目的根路径
project_root = Path(__file__).parents[1].resolve()

def _prepare_session_environment(thread_id: str):
    """
    初始化会话运行环境（会话文件夹,以及相对路径，上传文件的信息！）。
    目标：
    1. 创建独立的物理工作空间。
    2. 处理用户上传的文件。
    3. 生成供 Agent 和前端使用的路径上下文（提示词）。

    执行步骤：
    1. 创建绝对路径：`project_root/output/session_{uuid}`。
    2. 标准化路径：转换为 POSIX 风格 (`/`) 以兼容 LLM 和跨平台。
    3. 文件迁移：将 `upload/session_{uuid}` 中的文件复制到工作目录。
    4. 构造提示词：生成包含已上传文件列表的 Context 文本。

    Returns:
        tuple: (
            session_dir_str (str): 物理工作目录的绝对路径 (当前会话对应文件存储位置)。
            relative_session_dir (str): 相对于项目根目录的路径 (用于提示词)。
            uploaded_info (str): 注入到 Prompt 中的文件列表描述。
        )
    """
    # 设置工作目录
    session_dir = project_root / "output" / f"session_{thread_id}"
    # 创建工作目录
    session_dir.mkdir(parents=True, exist_ok=True)
    # 获取工作目录的字符串路径
    session_dir_str = str(session_dir).replace("\\", "/")
    # 获取工作目录相当于项目根目录的相对路径
    relative_session_dir = str(session_dir.relative_to(project_root)).replace("\\", "/")
    # 获取上传文件的目录
    upload_dir = project_root / "upload" / f"session_{thread_id}"
    # 创建存储上传信息的变量
    uploaded_info = ""
    if upload_dir.exists():
        # 获取upload_dir中所有的文件名
        file_names = [item.name for item in upload_dir.iterdir() if item.is_file()]
        if file_names:
            for file_name in file_names:
                shutil.copy2(upload_dir / file_name, session_dir / file_name)
            uploaded_info = (f"\n    [已上传文件] 已加载到工作目录:\n" +
                             "\n".join([f"    - {f}" for f in file_names]) +
                             "\n    请优先使用工具读取并参考这些文件。")
    return session_dir_str, relative_session_dir, uploaded_info

def _process_stream_chunk(chunk):
    """
    处理 LangGraph 流式输出的增量状态 (Stream Processing)。
    目标：
    1. 解析 Agent 的每一步思考和行动。
    2. 识别关键事件（工具调用、子 Agent 委派、最终回复）。
    3. 通过 Monitor 实时上报状态给前端。
    核心逻辑：
    - 监听 `tool_calls` -> 记录日志，若是 'task' 则上报子 Agent 状态。
    - 监听 `content` -> 若无工具调用，则视为 Agent 的最终回复。
    Args:
        chunk (dict): 增量状态字典，如 {"node_name": {"messages": [AIMessage(...)]}}
    """
    for node_name, state in chunk.items():
        if not state or "messages" not in state: continue
        # 3. [提取] 获取最新一条消息 (Latest Message)
        messages = state["messages"]
        if isinstance(messages, list) and messages:
            last_msg = messages[-1]
            # 4. [分支] 处理 AI 消息 (AIMessage)
            if isinstance(last_msg, AIMessage):
                # Case 1: Agent 决定调用工具 (Tool Call)
                if last_msg.tool_calls:
                    for tool in last_msg.tool_calls:
                        # 特殊处理：如果是 'task' 工具，说明正在委派给子 Agent
                        if tool['name'] == 'task':
                            monitor.report_assistant(
                                tool['args'].get('subagent_type', 'Agent'),
                                {"desc": tool['args'].get('description')}
                            )
                # Case 2: Agent 生成最终回复 (Final Answer)
                elif last_msg.content:
                    monitor.report_task_result(last_msg.content)

async def run_deep_agent(query:str, thread_id:str):
    """
    触发deepagent的调用
    :param query:
    :param thread_id:
    :return:
    """
    # 获取相关数据
    session_dir_str, relative_session_dir, uploaded_info = _prepare_session_environment(thread_id)
    # 存储session_dir和thread_id
    session_token = set_session_context(session_dir_str)
    thread_token = set_thread_context(thread_id)
    # 推送session的路径
    monitor.report_session_dir(session_dir_str)
    path_instruction = f"""
        【工作环境指令】
        工作目录: {relative_session_dir}
        {uploaded_info}

        规则：
        1. 新生成文件必须保存到工作目录：'{relative_session_dir}/filename'
        2. 读取已上传的文件时，请直接将文件名（例如：'开篇.txt'）作为 filename 参数传入（read_file_content）读取工具，不要带上任何目录前缀。
        3. 使用相对路径，禁止使用绝对路径
        4. 若存在上传文件，请先分析内容
    """
    # 调用main_agent
    try:
        main_agent = build_main_agent()
        async for chunk in main_agent.astream(
            {
                "messages":{
                    "role":"user",
                    "content":f"问题:{query}, 额外描述:{path_instruction}"
                }
            }
        ):
            _process_stream_chunk(chunk)
    except Exception as e:
        logger.error("主智能体调用失败: %s (HTTP %s)", type(e).__name__, getattr(e, "status_code", None))
        monitor._emit("error", model_error_message(e))
    finally:
        if 'session_token' in locals():
            reset_session_context(session_token, thread_token)

if __name__ == "__main__":
    task = "请问空调的绝热工程怎么做"
    asyncio.run(run_deep_agent(task, "abc"))
