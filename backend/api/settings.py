from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, SecretStr

from agent.llm import create_llm, get_model_config, model_error_message, save_model_config


def local_request(request: Request):
    if not request.client or request.client.host not in {"127.0.0.1", "::1"}:
        raise HTTPException(403, "模型设置仅允许在本机访问。")
    origin = request.headers.get("origin")
    if origin and origin != f"{request.url.scheme}://{request.url.netloc}":
        raise HTTPException(403, "请从本机 DeepSearch 页面修改设置。")


router = APIRouter(prefix="/api/settings/model", dependencies=[Depends(local_request)])


class ModelSettings(BaseModel):
    base_url: str = Field(default="https://api.deepseek.com", min_length=1, max_length=500)
    model: str = Field(default="deepseek-v4-pro", min_length=1, max_length=150)
    api_key: SecretStr = SecretStr("")


def validated_config(settings: ModelSettings):
    base_url = settings.base_url.strip().rstrip("/")
    model = settings.model.strip()
    key = settings.api_key.get_secret_value().strip()
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise HTTPException(400, "请输入有效的 HTTP/HTTPS Base URL。")
    if parsed.scheme == "http" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise HTTPException(400, "远程模型接口请使用 HTTPS 地址。")
    if not model or any(c in model + base_url + key for c in "\r\n"):
        raise HTTPException(400, "模型名称、地址和密钥不能包含换行。")
    if len(key) > 1024:
        raise HTTPException(400, "API Key 长度无效。")
    return {"base_url": base_url, "model": model, "api_key": key or get_model_config()["api_key"]}


@router.get("")
def read_settings():
    config = get_model_config()
    return {"base_url": config["base_url"], "model": config["model"], "key_configured": bool(config["api_key"])}


@router.post("")
def save_settings(settings: ModelSettings):
    config = validated_config(settings)
    if not config["api_key"]:
        raise HTTPException(400, "请填写 DeepSeek API Key。")
    save_model_config(**config)
    return {"status": "saved", "message": "已保存，下次提问立即生效。", "key_configured": True}


@router.post("/test")
async def test_settings(settings: ModelSettings):
    config = validated_config(settings)
    if not config["api_key"]:
        raise HTTPException(400, "请先填写 API Key，再测试连接。")
    try:
        await create_llm(config, timeout=20).ainvoke(
            "请只回复 OK。", max_tokens=16, extra_body={"thinking": {"type": "disabled"}},
        )
        return {"ok": True, "message": "连接成功，模型可以正常调用。"}
    except Exception as error:
        return {"ok": False, "message": model_error_message(error)}
