import logging

from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel, Field

from app.dependencies import get_resources
from app.services.generation import generate
from app.services.retrieval import retrieve

logger = logging.getLogger(__name__)
router = APIRouter()
#类，实例化之后是对象
class ChatRequest(BaseModel):
    question:str = Field(...,
                         min_length=1,
                         max_length=4000,)


@router.post("/chat")
#res里面已经挂载了三个，在main里面的embeding，milvs，agent
#个人问题讲解，body只是一个变量名，用来调用ChatRequet里面的属性而已可以替换人很内容
async def chat(body: ChatRequest, res=Depends(get_resources)):
    try:
        print("\n========== 收到新问题 ==========")
        print("用户问题:", body.question)
        print("初始化用的模型:", res.embedding.model)  # 检查嵌入模型是谁
        print("Milvus 连接信息:", res.milvus)#打印Milvus信息
        #调用retrieve方法，将传入的问题向量化，return：list[]
        #个人问题讲解：
        #1.为什么要传入res.milvus,res.embedding呢？答：这是依赖传递，方便函数根据自己的需要去调用里面的方法
        hits = retrieve(res.milvus, res.embedding, body.question)#传入Milvus连接地址，嵌入模型，问题对象由外层准备，业务函数只声明自己需要什么

        print("检索到的结果数量:", len(hits))
        if hits:
            print("第一条文本:", hits[0]["entity"]["text"][:20], "...")
        print("==============================\n")

        if not hits:
            return {"answer": "我暂时无法回答你的消息", "sources": []}

        answer = await generate(res.agent, body.question, hits)

        sources = [
            {"chunk_id":h["entity"].get("chunk_id"),
             "source":h["entity"].get("source"),}
            for h in hits
        ]
        return {"answer":answer,"sources":sources}
    except Exception as e:
        logger.error("chat failed")
        raise HTTPException(status_code=502,detail=f"chat failed:{e}")