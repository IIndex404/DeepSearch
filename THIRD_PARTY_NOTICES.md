# 第三方依赖说明

DeepSearch 使用 Vue、FastAPI、DeepAgents、LangChain、Tavily SDK、RAGFlow SDK 等依赖，各依赖保留自身的许可证与版权。具体依赖版本见 `backend/uv.lock` 与 `frontend/package-lock.json`。

`services/ragflow/entrypoint.sh`、`service_conf.yaml.template` 及 Nginx 配置沿用本地部署所使用的 RAGFlow 部署文件，并进行了公开配置整理。RAGFlow 是独立第三方服务，其代码和部署文件按 Apache License 2.0 提供；对应许可保存在 `services/ragflow/LICENSE`。

RAGFlow 项目：https://github.com/infiniflow/ragflow

这份说明记录所使用的第三方依赖与部署文件，不将 DeepSearch 的应用代码归属于这些第三方。
