# 数据库与知识库配置

主程序通过 `backend/.env` 连接业务 MySQL 与 RAGFlow。你可以使用已有服务，也可以使用仓库中的本地 RAGFlow 部署配置。

## 启动本地 RAGFlow

需要 Docker Desktop。先复制 `services/ragflow/.env.example` 为同目录下的 `.env`，填写 `MYSQL_PASSWORD`、`MINIO_PASSWORD`、`ELASTIC_PASSWORD`、`REDIS_PASSWORD` 和 `RAGFLOW_SECRET_KEY`。请使用自行生成的长随机值；首次初始化后修改配置文件不会自动重置已有服务的密码。

在仓库根目录运行 `Start-DataServices.cmd`，或执行：

```powershell
cd services/ragflow
docker compose up -d
docker compose ps
docker compose logs --tail 100 ragflow
```

配置包含 RAGFlow 0.24.0、MySQL、Elasticsearch、Valkey、MinIO 和 CPU TEI。TEI 首次启动会下载 `BAAI/bge-small-zh-v1.5`。服务数据与模型缓存在 `services/ragflow/data/`，不进入 Git。首次运行需要等待镜像下载、模型下载和服务初始化。

RAGFlow 页面为 `http://127.0.0.1:8080`，API 为 `http://127.0.0.1:9380`。在页面中完成账号、模型与知识库配置，创建关联知识库的聊天助手并生成 API Key，将它填写到 `backend/.env` 的 `RAGFLOW_API_KEY`。聊天模型需要单独配置；DeepSearch 页面中的模型设置只控制主程序。

本地端口默认还包括 MySQL `3306`、Elasticsearch `1200`、TEI `6380`、MinIO `9000/9001`。已有同端口服务时应先调整映射。此配置使用独立 MinIO，不依赖原电脑已有容器。

停止服务并保留数据：

```powershell
docker compose stop
```

## 业务 MySQL

SQL 助手使用 `backend/.env` 中的 `MYSQL_*` 配置。请连接你有权使用的业务数据库，并使用只读账号。RAGFlow 的 `rag_flow` 数据库保存知识库平台内部元数据，不是业务示例数据库。

仓库不包含业务数据库备份、业务报表或预置知识库内容。需要自行准备表、导入授权资料，并按业务修改 `backend/prompt/prompts.yaml`。

## 复用已有服务

将 `RAGFLOW_BASE_URL` 指向已有 RAGFlow API，并填写相应 API Key。Python 依赖中固定使用 `ragflow-sdk==0.24.0`。第三方平台的安装与使用说明见 [RAGFlow](https://github.com/infiniflow/ragflow)。

本次开源整理只验证配置解析，没有重新启动这组数据服务。
