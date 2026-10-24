import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from langchain.chat_models import init_chat_model

from app import config
from app.services.embedding import create_embedding
from app.routers import chat, admin
from app.services.milvue_client import create_client, ensure_collection

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent / "static"

SWAGGER_JS_URL = (
    "https://cdn.bootcdn.net/ajax/libs/swagger-ui/"
    "5.17.14/swagger-ui-bundle.min.js"
)
SWAGGER_CSS_URL = (
    "https://cdn.bootcdn.net/ajax/libs/swagger-ui/"
    "5.17.14/swagger-ui.min.css"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动：初始化所有共享资源
    #create_client创建milvus实例对象，赋值给app.state.milvus挂载到app.state里面
    app.state.milvus = create_client()
    ensure_collection(app.state.milvus, recreate=False)   # 幂等，不删数据，判断是否有这个集合（表）
    app.state.embedding = create_embedding()#创建嵌入对象
    app.state.agent = init_chat_model(
        model=config.LLM_MODEL,
        model_provider=config.LLM_PROVIDER)#创建模型
    logger.info("resources initialized")
    yield
    # 关闭：清理（Milvus 一般无需显式关闭，留位置给未来资源）
    logger.info("shutting down")

app = FastAPI(
    title="RAG Service",
    lifespan=lifespan,
    docs_url=None,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(chat.router, tags=["chat"])
app.include_router(admin.router, tags=["admin"])


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url=SWAGGER_JS_URL,
        swagger_css_url=SWAGGER_CSS_URL,
    )
