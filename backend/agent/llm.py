"""Read the local DeepSeek settings when each task starts."""
from pathlib import Path
from threading import RLock

from dotenv import dotenv_values, set_key
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import AIMessage

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
_lock = RLock()


class DeepSeekV4Chat(ChatDeepSeek):
    """Preserve reasoning_content on follow-up tool calls in thinking mode."""

    def _get_request_payload(self, input_, *, stop=None, **kwargs):
        messages = self._convert_input(input_).to_messages()
        payload = super()._get_request_payload(messages, stop=stop, **kwargs)
        for original, serialized in zip(messages, payload["messages"]):
            if isinstance(original, AIMessage):
                reasoning = original.additional_kwargs.get("reasoning_content")
                if reasoning is not None:
                    serialized["reasoning_content"] = reasoning
        return payload


def get_model_config():
    with _lock:
        values = dotenv_values(ENV_PATH)
        return {
            "base_url": values.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com",
            "model": values.get("DEEPSEEK_MODEL") or "deepseek-v4-pro",
            "api_key": values.get("DEEPSEEK_API_KEY") or "",
        }


def save_model_config(base_url: str, model: str, api_key: str):
    with _lock:
        set_key(str(ENV_PATH), "DEEPSEEK_BASE_URL", base_url)
        set_key(str(ENV_PATH), "DEEPSEEK_MODEL", model)
        if api_key:
            set_key(str(ENV_PATH), "DEEPSEEK_API_KEY", api_key)


def create_llm(config=None, timeout=120):
    config = config or get_model_config()
    if not config["api_key"]:
        raise ValueError("请先在右上角模型设置中填写 DeepSeek API Key。")
    return DeepSeekV4Chat(
        model=config["model"], api_key=config["api_key"],
        base_url=config["base_url"], timeout=timeout, max_retries=0,
    )


def model_error_message(error):
    status = getattr(error, "status_code", None)
    if status == 401:
        return "API Key 无效，请在模型设置中重新填写。"
    if status == 402:
        return "模型账户余额不足，请充值后重试。"
    if status == 429:
        return "模型服务请求受限，请稍后重试。"
    if status:
        return f"模型接口返回 HTTP {status}，请检查 Base URL、模型名称和账户权限。"
    if isinstance(error, ValueError):
        return "请先在模型设置中填写有效的 API Key。"
    return "模型调用失败，请检查接口地址和网络后重试。"
