# Intelligent Customer Service

一个基于 FastAPI、Milvus 和 LangChain 的客服知识库 RAG 服务。系统从本地知识库检索相关片段，再调用大模型生成带来源引用的回答，并提供可直接使用的聊天页面。

## 功能

- `POST /chat`：输入问题，返回回答和知识库来源
- `POST /admin/reindex`：重建 Milvus 知识库索引
- 基于 DashScope Embedding 的语义检索
- 基于 DeepSeek 的答案生成
- FastAPI 生命周期内复用 Milvus、Embedding 和对话模型客户端
- 内置响应式聊天页面和 Swagger API 文档

## 项目结构

```text
app/
  main.py                 FastAPI 入口、生命周期和静态页面
  config.py               .env 配置
  dependencies.py         应用共享资源依赖
  routers/
    chat.py               问答接口
    admin.py              索引管理接口
  services/
    embedding.py          Embedding 客户端和批量向量化
    ingest.py             文档切分和索引写入
    milvue_client.py      Milvus 连接与集合初始化
    retrieval.py          向量检索
    generation.py         提示词构建和答案生成
  static/                 聊天页面资源
knowledge.txt             示例客服知识库
```

## 环境要求

- Python 3.11 或更高版本，当前使用 Python 3.13 验证
- 可访问的 Milvus 服务
- DashScope API Key
- DeepSeek API Key

## 本地运行

创建并激活虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

创建本地配置：

```powershell
Copy-Item .env.example .env
```

编辑 `.env`，至少填写以下内容：

```env
DEEPSEEK_API_KEY=你的密钥
DASHSCOPE_API_KEY=你的密钥
MILVUS_URL=http://你的Milvus地址:19530
EMBED_MODEL_NAME=你的Embedding模型
EMBED_DIM=你的向量维度
LLM_MODEL=你的对话模型
LLM_PROVIDER=deepseek
KNOWLEDGE_FILE=knowledge.txt
ADMIN_TOKEN=你的管理令牌
```

启动服务：

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

访问聊天页面：

```text
http://127.0.0.1:8000/
```

访问接口文档：

```text
http://127.0.0.1:8000/docs
```

## 建立知识库索引

首次运行或修改 `knowledge.txt` 后，需要重建索引：

```powershell
$headers = @{ "X-Admin-Token" = "你的管理令牌" }
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/admin/reindex?recreate=true" `
  -Headers $headers
```

`recreate=true` 会删除旧集合并重新写入索引。执行前请确认 Milvus 中的数据可以重建。

## 问答接口示例

```powershell
$body = @{ question = "基础版支持多少人？" } | ConvertTo-Json
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/chat" `
  -ContentType "application/json; charset=utf-8" `
  -Body $body
```

响应示例：

```json
{
  "answer": "基础版正式成员上限为 10 人，按已激活成员计算。[片段1]",
  "sources": [
    {
      "chunk_id": 12,
      "source": "knowledge.txt"
    }
  ]
}
```

## 配置说明

| 变量 | 说明 |
| --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek API Key |
| `DEEPSEEK_BASE_URL` | DeepSeek API 地址 |
| `LLM_MODEL` | 对话模型名称 |
| `LLM_PROVIDER` | LangChain 模型提供方，当前为 `deepseek` |
| `DASHSCOPE_API_KEY` | DashScope API Key |
| `EMBED_MODEL_NAME` | Embedding 模型名称 |
| `EMBED_DIM` | Embedding 向量维度，必须与 Milvus 集合一致 |
| `EMBED_BATCH_SIZE` | 批量向量化大小 |
| `MILVUS_URL` | Milvus 服务地址 |
| `DB_NAME` | Milvus 数据库名称 |
| `COLLECTION_NAME` | Milvus 集合名称 |
| `KNOWLEDGE_FILE` | 本地知识库文件路径 |
| `ADMIN_TOKEN` | 重建索引接口的管理令牌 |

## 安全说明

- `.env` 包含真实密钥，已被 `.gitignore` 忽略，不应提交。
- 不要把真实密钥写入 `.env.example`、README 或源代码。
- `/chat` 当前没有用户鉴权，公开部署前应增加认证、限流和请求审计。
- `test/` 是本地学习示例，不纳入当前 Git 提交。
