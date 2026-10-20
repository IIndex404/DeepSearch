# DeepSearch

多智能体深度研究与信息检索平台。

开发与维护：[IIndex404](https://github.com/IIndex404) · [MIT License](LICENSE)

输入研究问题后，主智能体协调联网搜索、业务数据库和知识库助手获取信息，结合上传资料整理回答，也可以生成 Markdown 或 PDF 报告。前端实时展示任务、助手调用和工具执行状态。

## 功能

- 联网搜索：通过 Tavily 查询公开网页信息。
- 数据库检索：查看 MySQL 表、读取数据并执行 SQL 查询。
- 知识库检索：通过 RAGFlow 查询聊天助手与知识库内容。
- 文件处理：上传本次会话资料，读取文件并生成报告。
- 实时进度：通过 WebSocket 展示任务执行情况。
- 模型设置：在本地页面修改 DeepSeek 接口地址、模型名称和 API Key。

后端使用 Python、FastAPI、DeepAgents 和 LangChain，前端使用 Vue 3、TypeScript 和 Vite。

## Windows 本地运行

需要 Python 3.12 或更高版本、uv、Node.js 22.12 或更高版本，以及你自己的 DeepSeek 和 Tavily API Key。PDF 转换使用 Windows Microsoft Word COM，需安装桌面版 Word。MySQL 和 RAGFlow 用于相应检索能力。

```powershell
git clone https://github.com/IIndex404/DeepSearch.git
cd DeepSearch
powershell -NoProfile -ExecutionPolicy Bypass -File .\Setup-DeepSearch.ps1
```

安装脚本会创建 `backend/.env`、安装锁定的 Python 与前端依赖并构建网页。打开 `backend/.env`，至少填写 `DEEPSEEK_API_KEY` 和 `TAVILY_API_KEY`；数据库与知识库配置见 [数据服务说明](docs/data-services.md)。模型名称可按账号支持情况修改，或启动后通过“模型设置”调整。

然后双击 `Start-DeepSearch.cmd`，访问 [http://127.0.0.1:8000](http://127.0.0.1:8000)。

| 入口 | 用途 |
| --- | --- |
| `Start-DeepSearch.cmd` | 后台启动主程序并打开页面 |
| `Stop-DeepSearch.cmd` | 停止此部署记录的主程序 |
| `Status-DeepSearch.cmd` | 检查主程序状态 |
| `Start-DataServices.cmd` | 按配置启动可选的本地 RAGFlow 数据服务 |
| `/health` | 主程序健康检查 |
| `/docs` | FastAPI 接口文档 |

默认启动脚本仅监听本机 `127.0.0.1`。Tavily 客户端在启动时初始化，因此启动前必须填写自己的 Tavily Key。

## 目录

```text
backend/
  agent/          主智能体和三个检索助手
  api/            任务、上传、下载、模型设置与 WebSocket
  tools/          搜索、SQL、知识库、文件与报告工具
  prompt/         智能体提示词
  utils/          日志、路径与转换工具
  .env.example    配置模板
  uv.lock         Python 依赖锁
frontend/         Vue 3 页面与前端依赖锁
services/ragflow/ 可选本地数据服务部署配置
docs/             数据服务说明
```

## 开发与 Git

修改前端后，在 `frontend` 中运行 `npm run build` 并刷新页面；修改后端后重启主程序。

```powershell
git status
git diff
git add <需要提交的文件>
git diff --cached
git commit -m "describe your change"
git push
```

`.gitignore` 排除真实 `.env`、上传文件、生成报告、服务数据、模型缓存、依赖目录和运行日志。仓库只提供空密钥配置模板。

## 使用边界

当前以 Windows 本机使用为主，尚未提供完整的多人账号与权限体系。SQL 工具会执行模型生成的查询，应连接只读账号。生成内容取决于模型与检索结果，需要自行核对。PDF 转换还依赖本机 Word 环境。

仓库不包含个人登录信息、真实业务数据、已导入的知识库和历史报告。RAGFlow 是独立第三方知识库服务，相关部署文件的许可见 [第三方依赖说明](THIRD_PARTY_NOTICES.md)。
