# 连接数据库和知识库

如果你想让 DeepSearch 查询自己的业务数据或文档，按下面对应的部分设置。

## 查自己的数据库

双击项目根目录的“配置.cmd”，找到这几行：

```dotenv
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=deepsearch_readonly
MYSQL_PASSWORD=
MYSQL_DATABASE=your_business_database
```

分别填数据库地址、端口、用户名、密码和库名。数据库在自己电脑上，地址一般用 `127.0.0.1`；在另一台机器上，就填那台机器的地址。用户名、密码和库名都要改成自己的。

请使用只能查询数据的账号。这个功能会让模型生成 SQL，再交给数据库执行。

保存后，停止再启动 DeepSearch。仓库没有附带业务数据库，需要连接你自己准备好的库。

## 查自己的文档

DeepSearch 通过 RAGFlow 管理长期使用的资料。流程是：**启动 RAGFlow → 导入文档 → 创建聊天助手 → 把 API Key 填回 DeepSearch**。

如果只是让它分析当前这次任务的文件，可以直接在 DeepSearch 页面上传。要把资料长期保存、反复检索，再接知识库。

### 已经有 RAGFlow

双击“配置.cmd”，填写：

```dotenv
RAGFLOW_BASE_URL=http://127.0.0.1:9380
RAGFLOW_API_KEY=这里填RAGFlow提供的密钥
```

地址填 RAGFlow 的接口地址，密钥在 RAGFlow 中生成。还需要在 RAGFlow 里创建关联了知识库的聊天助手。填好后重启 DeepSearch。

### 还没有 RAGFlow

1. 先安装并打开 Docker Desktop。
2. 打开项目的 `services/ragflow` 文件夹，把 `.env.example` 复制一份，改名为 `.env`。
3. 用记事本打开 `.env`，填写 `MYSQL_PASSWORD`、`MINIO_PASSWORD`、`ELASTIC_PASSWORD`、`REDIS_PASSWORD` 和 `RAGFLOW_SECRET_KEY`。这些值由你自己设置，用长随机字符串，并保存在自己的密码管理工具中。
4. 回到项目根目录，双击 `Start-DataServices.cmd`。第一次会下载镜像和向量模型，需要等待。
5. 打开 **[http://127.0.0.1:8080](http://127.0.0.1:8080)**，按 RAGFlow 页面完成账号和模型配置。
6. 创建知识库、上传文档，等解析完成。再创建聊天助手，把这个知识库关联进去。
7. 在 RAGFlow 中生成 API Key，按上一节填回 DeepSearch，重启主程序。

RAGFlow 里的聊天模型也需要单独配置。DeepSearch 右上角的“模型设置”只修改 DeepSearch 自己使用的模型。

## 资料保存在哪

| 内容 | 本地位置 |
| --- | --- |
| DeepSearch 密钥与连接信息 | `backend/.env` |
| 当前会话上传的文件 | `backend/upload` |
| 生成的报告 | `backend/output` |
| RAGFlow 数据、文档与模型缓存 | `services/ragflow/data` |

这些目录和配置文件已被 Git 忽略，不会随代码上传。

## 启动失败怎么查

在 `services/ragflow` 文件夹打开终端，运行：

```powershell
docker compose ps
docker compose logs --tail 100 ragflow
```

第一条看服务状态，第二条看最近的报错。常见原因是 Docker 没启动、镜像还没下载完、内存不足或端口被占用。

默认使用 `3306`、`8080`、`9380`、`1200`、`6380`、`9000` 和 `9001` 这些本机端口。如果已有服务占用，需要修改 `compose.yaml` 的端口，并同步调整主程序的连接配置。

这套部署包含 RAGFlow 0.24.0、MySQL、Elasticsearch、Valkey、MinIO 和 CPU 向量服务。RAGFlow 使用的 `rag_flow` 库保存它自己的运行数据，业务查询应连接另行准备的业务库。

用完后，在同一个终端运行 `docker compose stop` 可以停掉数据服务，数据仍然保留。已有数据库的密码不会因为修改 `.env` 自动重置。

更完整的知识库使用方法见 [RAGFlow 官方项目](https://github.com/infiniflow/ragflow)。
